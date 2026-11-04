param(
    [string]$BaseUrl = "http://localhost:6002/api/directory/v1",
    [string]$ApiKey = "",
    # Opt-in: stops the mock's Postgres container, checks both endpoints answer 503
    # (never 200 with an empty list), then starts it again.
    [switch]$CheckSourceDown,
    [string]$PostgresContainer = "mock-v13-dev-postgres-1"
)

# Acceptance test for the v1.3 mock: the two proposed BCI radiology endpoints,
# checked against the BCI test world (seed/bci_test_world.json, the same file
# the mock was seeded from). A small smoke check of the older endpoints runs
# first (the full v1.1/v1.2 behaviour is covered by the mock's pytest suite).
# Each addition reports PASS or FAIL; exit code 1 if anything failed.

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
if (-not $ApiKey) {
    $EnvFile = Join-Path $Root ".env"
    if (Test-Path $EnvFile) {
        $Line = Get-Content $EnvFile | Where-Object { $_ -match '^API_KEY=' } | Select-Object -First 1
        if ($Line) { $ApiKey = $Line.Substring(8) }
    }
}
if (-not $ApiKey) { Write-Host "No API key: pass -ApiKey or put API_KEY in the repo .env" -ForegroundColor Red; exit 2 }

$World = Get-Content (Join-Path $Root "seed\bci_test_world.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$Records = @($World.patients)

$PassCount = 0
$FailCount = 0
$Features = @{}

function Invoke-Api {
    param([string]$Path, [string]$Key = $ApiKey, [switch]$NoKey)
    $Result = [PSCustomObject]@{ StatusCode = $null; Body = $null; Raw = $null }
    $Request = [System.Net.HttpWebRequest]::Create("$BaseUrl$Path")
    $Request.Method = "GET"
    $Request.Timeout = 10000
    $Request.Accept = "application/json"
    if (-not $NoKey) { $Request.Headers.Add("X-API-Key", $Key) }
    $Response = $null
    try { $Response = $Request.GetResponse() }
    catch [System.Net.WebException] {
        $Response = $_.Exception.Response
        if (-not $Response) { $Result.Raw = $_.Exception.Message; return $Result }
    }
    $Result.StatusCode = [int]$Response.StatusCode
    $Mem = New-Object System.IO.MemoryStream
    $Response.GetResponseStream().CopyTo($Mem)
    $Result.Raw = [System.Text.Encoding]::UTF8.GetString($Mem.ToArray())
    try { $Result.Body = $Result.Raw | ConvertFrom-Json } catch { $Result.Body = $null }
    $Response.Close()
    return $Result
}

function Assert-Check {
    param([string]$Feature, [string]$Name, [bool]$Condition, [string]$Detail = "")
    if ($Condition) { Write-Host "PASS  $Name" -ForegroundColor Green; $script:PassCount++ }
    else {
        Write-Host "FAIL  $Name  $Detail" -ForegroundColor Red; $script:FailCount++
        $script:Features[$Feature] = "FAIL"
    }
    if (-not $script:Features.ContainsKey($Feature)) { $script:Features[$Feature] = "PASS" }
}

# Strict equality that treats $null and missing as equal, and compares text case-sensitively.
function Same($A, $B) {
    if ($null -eq $A -and $null -eq $B) { return $true }
    if ($null -eq $A -or $null -eq $B) { return $false }
    return ([string]$A -ceq [string]$B)
}

function Names-Match($Item, $Rec) {
    $Ar = $Rec.name_ar; $En = $Rec.name_en
    return (Same $Item.first_name_ar $Ar.first) -and (Same $Item.father_name_ar $Ar.father) -and
        (Same $Item.last_name_ar $Ar.family) -and (Same $Item.mother_name_ar $Ar.mother) -and
        (Same $Item.first_name_en $En.first) -and (Same $Item.father_name_en $En.father) -and
        (Same $Item.last_name_en $En.family) -and (Same $Item.mother_name_en $En.mother)
}

# ---------- smoke: the older endpoints still behave ----------
Write-Host "== smoke: older endpoints" -ForegroundColor Cyan
$R = Invoke-Api "/health" -NoKey
Assert-Check "smoke" "health is open and healthy" ($R.StatusCode -eq 200 -and $R.Body.status -eq "healthy")
$R = Invoke-Api "/patients/10001" -NoKey
Assert-Check "smoke" "a directory route without a key is 401" ($R.StatusCode -eq 401)
$R = Invoke-Api "/patients/10001"
Assert-Check "smoke" "a directory patient is still found" ($R.StatusCode -eq 200 -and $R.Body.patient_id -eq "10001")
$R = Invoke-Api "/er/current-visits"
Assert-Check "smoke" "v1.2 er/current-visits still answers" ($R.StatusCode -eq 200 -and $R.Body.success -eq $true)
$R = Invoke-Api "/patients/9999.100001"
Assert-Check "smoke" "test-world patients are NOT in the directory patients table" ($R.StatusCode -eq 404)

# ---------- 1. visits/today ----------
Write-Host "== bci-visits-today" -ForegroundColor Cyan
$Beirut = [TimeZoneInfo]::FindSystemTimeZoneById("Middle East Standard Time")  # Beirut
$Today = [TimeZoneInfo]::ConvertTime([DateTime]::UtcNow, $Beirut).Date

$Expected = @()
foreach ($Rec in $Records) { foreach ($V in @($Rec.visits_today)) { $Expected += [PSCustomObject]@{ Rec = $Rec; V = $V } } }
$Expected = @($Expected | Sort-Object { $_.V.time }, { $_.V.visit_id })

$R = Invoke-Api "/bci-radiology/visits/today"
Assert-Check "bci-visits-today" "returns 200 with success true" ($R.StatusCode -eq 200 -and $R.Body.success -eq $true) "status=$($R.StatusCode)"
$Items = @($R.Body.items)
Assert-Check "bci-visits-today" "total equals the number of items and the test world's visits ($($Expected.Count))" `
    ($R.Body.total -eq $Items.Count -and $Items.Count -eq $Expected.Count) "total=$($R.Body.total) items=$($Items.Count)"
$Ids = ($Items | ForEach-Object { $_.visit_id }) -join ","
$ExpectedIds = ($Expected | ForEach-Object { $_.V.visit_id }) -join ","
Assert-Check "bci-visits-today" "visits are in the test world's order (time, then visit id)" ($Ids -ceq $ExpectedIds) "got=$Ids"

$BadTime = @(); $BadFields = @(); $BadNames = @()
$Fields = "visit_id,mrn,first_name_ar,father_name_ar,last_name_ar,mother_name_ar,first_name_en,father_name_en,last_name_en,mother_name_en,birth_date,sex,visit_time,visit_kind,doctor_name,status" -split ","
for ($i = 0; $i -lt [Math]::Min($Items.Count, $Expected.Count); $i++) {
    $It = $Items[$i]; $Ex = $Expected[$i]
    $Local = $Today.Add([TimeSpan]::Parse($Ex.V.time))
    $Off = $Beirut.GetUtcOffset($Local)
    $Sign = if ($Off -ge [TimeSpan]::Zero) { "+" } else { "-" }
    $Want = $Local.ToString("yyyy-MM-ddTHH:mm:ss") + $Sign + ("{0:00}:{1:00}" -f [Math]::Abs($Off.Hours), [Math]::Abs($Off.Minutes))
    if (-not (Same $It.visit_time $Want)) { $BadTime += "$($It.visit_id): got $($It.visit_time) want $Want" }
    $Props = @($It.PSObject.Properties.Name | Sort-Object)
    if ((Compare-Object $Props @($Fields | Sort-Object) -SyncWindow 0).Count -ne 0) { $BadFields += $It.visit_id }
    if (-not (Names-Match $It $Ex.Rec)) { $BadNames += $It.visit_id }
    elseif (-not ((Same $It.mrn $Ex.Rec.mrn) -and (Same $It.birth_date $Ex.Rec.birth_date) -and (Same $It.sex $Ex.Rec.sex) -and
            (Same $It.visit_kind $Ex.V.kind) -and (Same $It.doctor_name $Ex.V.doctor) -and (Same $It.status $Ex.V.status))) { $BadNames += $It.visit_id }
}
Assert-Check "bci-visits-today" "every visit_time is TODAY ($($Today.ToString('yyyy-MM-dd'))) in Beirut with the right offset" ($BadTime.Count -eq 0) ($BadTime -join "; ")
Assert-Check "bci-visits-today" "every item has exactly the documented fields" ($BadFields.Count -eq 0) ($BadFields -join ",")
Assert-Check "bci-visits-today" "names (Arabic and English), birth date, sex, kind, doctor, status match the test world" ($BadNames.Count -eq 0) ($BadNames -join ",")

$NoVisit = @($Records | Where-Object { @($_.visits_today).Count -eq 0 })
$Absent = $true; foreach ($Rec in $NoVisit) { if (@($Items | Where-Object { $_.mrn -ceq $Rec.mrn }).Count -ne 0) { $Absent = $false } }
Assert-Check "bci-visits-today" "patients without a visit today are absent ($(($NoVisit | ForEach-Object { $_.mrn }) -join ', '))" ($NoVisit.Count -gt 0 -and $Absent)
$Multi = @($Records | Where-Object { @($_.visits_today).Count -ge 2 })
$MultiOk = $Multi.Count -gt 0; foreach ($Rec in $Multi) { if (@($Items | Where-Object { $_.mrn -ceq $Rec.mrn }).Count -ne @($Rec.visits_today).Count) { $MultiOk = $false } }
Assert-Check "bci-visits-today" "a patient with two visits appears twice" $MultiOk
$Frozen = @($Items | Where-Object { $_.status -ceq "frozen" })
Assert-Check "bci-visits-today" "the frozen visit is listed with status frozen" ($Frozen.Count -eq 1)
$R2 = Invoke-Api "/bci-radiology/visits/today?limit=1&offset=3"
Assert-Check "bci-visits-today" "limit/offset have no effect (complete snapshot)" ($R2.StatusCode -eq 200 -and $R2.Body.total -eq $Expected.Count)
$R3 = Invoke-Api "/bci-radiology/visits/today" -NoKey
Assert-Check "bci-visits-today" "no key is 401 UNAUTHORIZED" ($R3.StatusCode -eq 401 -and $R3.Body.error -eq "UNAUTHORIZED")
$R3 = Invoke-Api "/bci-radiology/visits/today" -Key "wrong-key"
Assert-Check "bci-visits-today" "wrong key is 401 UNAUTHORIZED" ($R3.StatusCode -eq 401 -and $R3.Body.error -eq "UNAUTHORIZED")

# ---------- 2. patients/{mrn} ----------
Write-Host "== bci-patient" -ForegroundColor Cyan
$PField = "mrn,first_name_ar,father_name_ar,last_name_ar,mother_name_ar,first_name_en,father_name_en,last_name_en,mother_name_en,birth_date,sex,nationality,id_number,has_allergy,phones" -split ","
$BadAny = @()
foreach ($Rec in $Records) {
    $P = Invoke-Api "/bci-radiology/patients/$($Rec.mrn)"
    $Why = @()
    if ($P.StatusCode -ne 200) { $Why += "status $($P.StatusCode)" }
    else {
        $B = $P.Body
        if ((Compare-Object @($B.PSObject.Properties.Name | Sort-Object) @($PField | Sort-Object) -SyncWindow 0).Count -ne 0) { $Why += "fields" }
        if (-not (Names-Match $B $Rec)) { $Why += "names" }
        if (-not ((Same $B.mrn $Rec.mrn) -and (Same $B.birth_date $Rec.birth_date) -and (Same $B.sex $Rec.sex) -and
                (Same $B.nationality $Rec.nationality) -and (Same $B.id_number $Rec.id_number))) { $Why += "identity" }
        if ($B.has_allergy -ne $Rec.has_allergy) { $Why += "allergy" }
        $GotPh = (@($B.phones) | ForEach-Object { "$($_.number)|$($_.owner)" }) -join ";"
        $WantPh = (@($Rec.phones) | ForEach-Object { "$($_.number)|$($_.owner)" }) -join ";"
        if ($GotPh -cne $WantPh) { $Why += "phones" }
        if ($P.Raw -notmatch [regex]::Escape($Rec.name_ar.first)) { $Why += "arabic-bytes" }
    }
    if ($Why.Count) { $BadAny += "$($Rec.mrn): $($Why -join ',')" }
}
Assert-Check "bci-patient" "all $($Records.Count) test-world MRNs return the right fields (Arabic as UTF-8, phones, allergy, nationality, id)" ($BadAny.Count -eq 0) ($BadAny -join "; ")
$TwoMrn = @($Records | Group-Object person_key | Where-Object { $_.Count -eq 2 } | Select-Object -First 1)
$Both = $TwoMrn.Count -eq 1
if ($Both) { foreach ($Rec in $TwoMrn[0].Group) { if ((Invoke-Api "/bci-radiology/patients/$($Rec.mrn)").StatusCode -ne 200) { $Both = $false } } }
Assert-Check "bci-patient" "both MRNs of the person with two MRNs work" $Both
$R = Invoke-Api "/bci-radiology/patients/9999.999999"
Assert-Check "bci-patient" "unknown MRN is 404 PATIENT_NOT_FOUND" ($R.StatusCode -eq 404 -and $R.Body.error -eq "PATIENT_NOT_FOUND")
$R = Invoke-Api "/bci-radiology/patients/9999.10000"
Assert-Check "bci-patient" "a partial MRN is not matched (404)" ($R.StatusCode -eq 404)
$R = Invoke-Api "/bci-radiology/patients/$($Records[0].mrn)" -NoKey
Assert-Check "bci-patient" "no key is 401 UNAUTHORIZED" ($R.StatusCode -eq 401 -and $R.Body.error -eq "UNAUTHORIZED")
$R = Invoke-Api "/bci-radiology/patients/$($Records[0].mrn)" -Key "wrong-key"
Assert-Check "bci-patient" "wrong key is 401 UNAUTHORIZED" ($R.StatusCode -eq 401 -and $R.Body.error -eq "UNAUTHORIZED")

# ---------- 3. source down (opt-in) ----------
if ($CheckSourceDown) {
    Write-Host "== source down (stopping $PostgresContainer)" -ForegroundColor Cyan
    docker stop $PostgresContainer | Out-Null
    try {
        $V = Invoke-Api "/bci-radiology/visits/today"
        Assert-Check "bci-source-down" "visits/today is 503 SERVICE_UNAVAILABLE, not 200 with an empty list" ($V.StatusCode -eq 503 -and $V.Body.error -eq "SERVICE_UNAVAILABLE") "status=$($V.StatusCode) body=$($V.Raw)"
        $P = Invoke-Api "/bci-radiology/patients/$($Records[0].mrn)"
        Assert-Check "bci-source-down" "patients/{mrn} is 503 SERVICE_UNAVAILABLE, not 404" ($P.StatusCode -eq 503 -and $P.Body.error -eq "SERVICE_UNAVAILABLE") "status=$($P.StatusCode)"
    } finally {
        docker start $PostgresContainer | Out-Null
    }
    for ($t = 0; $t -lt 30; $t++) {
        $H = Invoke-Api "/bci-radiology/visits/today"
        if ($H.StatusCode -eq 200) { break }
        Start-Sleep -Seconds 2
    }
    Assert-Check "bci-source-down" "the API recovers by itself when the database is back" ($H.StatusCode -eq 200 -and $H.Body.total -eq $Expected.Count)
} else {
    Write-Host "(source-down check skipped: run with -CheckSourceDown)" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "---- v1.3 features ----"
foreach ($Name in "bci-visits-today", "bci-patient", "bci-source-down") {
    if ($Features.ContainsKey($Name)) { "{0,-18} {1}" -f "${Name}:", $Features[$Name] }
}
Write-Host "smoke:             $($Features['smoke'])"
Write-Host "$PassCount passed, $FailCount failed"
if ($FailCount -gt 0) { exit 1 } else { exit 0 }
