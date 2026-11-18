param(
    [string]$BaseUrl = "http://localhost:18080/his-general/api/directory/v1",
    [string]$ApiKey = "change_me",
    [string]$ErBaseUrl = "http://localhost:18080/his-er/api/er/v1",
    [string]$ErApiKey = "change_me",
    [string]$PatientFirstName = "",
    [string]$PatientFatherName = "",
    [string]$PatientLastName = ""
)

# Hospital Directory API v1.2 - test of what 3iSoft DELIVERED
# (document "HIS API - v1.2 Additions", received 18 Nov 2026).
#
#   Part 1  v1.1 regression: everything from v1.1 still works.
#   Part 2  the three v1.2 additions, as 3iSoft documented them:
#             A. GET /patients/father-names          (Directory API)
#             B. GET /hr-workers, /hr-workers/{id}   (Directory API)
#             C. GET /current-visits                 (ER API: own address, own key)
#
# PASS / FAIL lines count towards the result. INFO lines are things to know,
# not failures. This file is plain ASCII on purpose (Windows PowerShell 5.1);
# Arabic letters are built from their Unicode numbers.

$ErrorActionPreference = "Continue"
$Failures = New-Object System.Collections.ArrayList
$Infos = New-Object System.Collections.ArrayList
$PassCount = 0
$FailCount = 0

# ---------------------------------------------------------------- Arabic
function U([int[]]$Codes) { -join ($Codes | ForEach-Object { [char]$_ }) }
$AR_MALE = U 0x0630,0x0643,0x0631                 # "male"
$AR_FEMALE = U 0x0627,0x0646,0x062B,0x0649        # "female"

function Normalize-Name([string]$s) {
    # 3iSoft's rule: trim; alef forms -> bare alef; ta marbuta -> ha; alef maqsura -> ya.
    if ($null -eq $s) { return $null }
    $t = $s.Trim()
    $t = $t.Replace([char]0x0623, [char]0x0627).Replace([char]0x0625, [char]0x0627).Replace([char]0x0622, [char]0x0627)
    $t = $t.Replace([char]0x0629, [char]0x0647).Replace([char]0x0649, [char]0x064A)
    return $t
}

function Test-Mojibake([string]$s) {
    # Arabic read as Latin-1 shows up as runs of these letters; real Arabic never contains them.
    if (-not $s) { return $false }
    return ($s.IndexOf([char]0x00D8) -ge 0 -or $s.IndexOf([char]0x00D9) -ge 0)
}

# ---------------------------------------------------------------- HTTP
function Invoke-Api {
    param([string]$Base, [string]$Path, [string]$Key = $null)
    $Result = [PSCustomObject]@{ StatusCode = $null; Body = $null; ContentType = ""; Raw = "" }
    $Request = [System.Net.HttpWebRequest]::Create("$Base$Path")
    $Request.Method = "GET"
    $Request.Timeout = 15000
    $Request.Accept = "application/json"
    if ($Key) { $Request.Headers.Add("X-API-Key", $Key) }
    $Response = $null
    try {
        $Response = $Request.GetResponse()
    } catch [System.Net.WebException] {
        $Response = $_.Exception.Response
        if (-not $Response) { $Result.Body = $_.Exception.Message; return $Result }
    }
    $Result.StatusCode = [int]$Response.StatusCode
    $Result.ContentType = [string]$Response.ContentType
    $Mem = New-Object System.IO.MemoryStream
    $Response.GetResponseStream().CopyTo($Mem)
    $Result.Raw = [System.Text.Encoding]::UTF8.GetString($Mem.ToArray())
    try { $Result.Body = $Result.Raw | ConvertFrom-Json } catch { $Result.Body = $Result.Raw }
    $Response.Close()
    return $Result
}
function DirApi([string]$Path, [switch]$NoKey) { if ($NoKey) { Invoke-Api $BaseUrl $Path } else { Invoke-Api $BaseUrl $Path $ApiKey } }
function Er([string]$Path, [string]$Key) { Invoke-Api $ErBaseUrl $Path $Key }
function Q([string]$s) { [uri]::EscapeDataString($s) }

# ---------------------------------------------------------------- reporting
function Check([string]$Name, [bool]$Ok, [string]$Detail = "") {
    if ($Ok) {
        Write-Host "PASS  $Name" -ForegroundColor Green
        $script:PassCount++
    } else {
        Write-Host "FAIL  $Name  $Detail" -ForegroundColor Red
        $script:FailCount++
        [void]$Failures.Add("$Name  $Detail")
    }
}
function Info([string]$Text) {
    Write-Host "INFO  $Text" -ForegroundColor Yellow
    [void]$Infos.Add($Text)
}
function Section([string]$Title) {
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Cyan
}
function Fields($Obj) { if ($null -eq $Obj) { @() } else { @($Obj.PSObject.Properties.Name) } }
function Same-Fields($Obj, [string[]]$Expected) {
    if ($null -eq $Obj) { return $false }
    $a = @(Fields $Obj | Sort-Object); $e = @($Expected | Sort-Object)
    return (Compare-Object $a $e -SyncWindow 0).Count -eq 0
}
function Show-Fields($Obj) { "(fields: " + ((Fields $Obj) -join ", ") + ")" }
function Is-Error($r, [int]$Status, [string]$Code) {
    return ($r.StatusCode -eq $Status -and $r.Body -and $r.Body.error -eq $Code)
}
function Got($r) { "(got $($r.StatusCode) $(if ($r.Body -and $r.Body.error) { $r.Body.error }))" }
function Items($r) { if ($r.Body -and $null -ne $r.Body.items) { @($r.Body.items) } else { @() } }

function Ordered-Ok([string]$a, [string]$b) {
    # "Alphabetical" may be code-point order or a language-aware order: accept either.
    if ([string]::CompareOrdinal($a, $b) -le 0) { return $true }
    if ([string]::Compare($a, $b, [System.Globalization.CultureInfo]::InvariantCulture, [System.Globalization.CompareOptions]::None) -le 0) { return $true }
    $ar = [System.Globalization.CultureInfo]::GetCultureInfo("ar-SA")
    return ([string]::Compare($a, $b, $ar, [System.Globalization.CompareOptions]::None) -le 0)
}

Write-Host "Directory API : $BaseUrl"
Write-Host "ER API        : $ErBaseUrl"

# ================================================================ PART 1
Section "Part 1: v1.1 regression"

$r = DirApi "/health" -NoKey
Check "GET /health -> 200" ($r.StatusCode -eq 200) (Got $r)
if ($r.StatusCode -eq 200) {
    Check "  service == his-general-directory" ($r.Body.service -eq "his-general-directory") "(got $($r.Body.service))"
    Info "health reports api_version = $($r.Body.api_version)"
}

$r = DirApi "/patients"
Check "GET /patients (no criteria) -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)

$r = DirApi "/patients?first_name=$(Q $PatientFirstName)"
Check "GET /patients first_name alone -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)

$r = DirApi "/patients?first_name=$(Q $PatientFirstName)&last_name=$(Q $PatientLastName)"
Check "GET /patients first+last without father -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)

$r = DirApi "/patients?first_name=$(Q $PatientFirstName)&father_name=$(Q $PatientFatherName)&last_name=$(Q $PatientLastName)&limit=5"
Check "GET /patients with all three names -> 200" ($r.StatusCode -eq 200) (Got $r)
$FirstPatient = (Items $r) | Select-Object -First 1
Check "  the patient in settings.txt is found" ($null -ne $FirstPatient) "(0 results: put a real patient's exact names in settings.txt)"
if ($FirstPatient) {
    $r = DirApi "/patients/$(Q $FirstPatient.patient_id)"
    Check "GET /patients/{id} -> 200" ($r.StatusCode -eq 200) (Got $r)
}
$r = DirApi "/patients/999999999"
Check "GET /patients/{unknown} -> 404 PATIENT_NOT_FOUND" (Is-Error $r 404 "PATIENT_NOT_FOUND") (Got $r)

$r = DirApi "/doctors?limit=5"
Check "GET /doctors -> 200" ($r.StatusCode -eq 200) (Got $r)
$FirstDoctor = (Items $r) | Select-Object -First 1
if ($FirstDoctor) {
    Check "  doctor fields match v1.1" (Same-Fields $FirstDoctor @("doctor_id","full_name","specialty_id","specialty_name","department_id","department_name","is_active")) (Show-Fields $FirstDoctor)
    $r = DirApi "/doctors/$(Q $FirstDoctor.doctor_id)"
    Check "GET /doctors/{id} -> 200" ($r.StatusCode -eq 200) (Got $r)
}
$r = DirApi "/doctors/999999999"
Check "GET /doctors/{unknown} -> 404 DOCTOR_NOT_FOUND" (Is-Error $r 404 "DOCTOR_NOT_FOUND") (Got $r)

$r = DirApi "/workers"
Check "GET /workers -> 200" ($r.StatusCode -eq 200) (Got $r)
Check "  default limit is 10" ($r.Body.limit -eq 10) "(got $($r.Body.limit))"
$W1 = (Items $r) | Select-Object -First 1
if ($W1) {
    $r = DirApi "/workers/$(Q $W1.employee_id)"
    Check "GET /workers/{id} -> 200" ($r.StatusCode -eq 200) (Got $r)
    if ((Fields $W1) -contains "section_name") {
        Info "/workers now also returns section_name/administration_name"
    } else {
        Info "/workers is unchanged (no section/administration names); 3iSoft put them in /hr-workers"
    }
}
$r = DirApi "/workers/999999999"
Check "GET /workers/{unknown} -> 404 WORKER_NOT_FOUND" (Is-Error $r 404 "WORKER_NOT_FOUND") (Got $r)

$r = DirApi "/doctors?limit=1" -NoKey
Check "Directory API without key -> 401 UNAUTHORIZED" (Is-Error $r 401 "UNAUTHORIZED") (Got $r)

# ================================================================ PART 2A
Section "Part 2A: GET /patients/father-names"

$FN = "first_name=$(Q $PatientFirstName)&last_name=$(Q $PatientLastName)"
$r = DirApi "/patients/father-names?$FN"
Check "father-names -> 200" ($r.StatusCode -eq 200) (Got $r)
if ($r.StatusCode -eq 200) {
    $FB = $r.Body
    Check "  response fields: success, first_name, last_name, candidates, total_candidates" (Same-Fields $FB @("success","first_name","last_name","candidates","total_candidates")) (Show-Fields $FB)
    Check "  success is true" ($FB.success -eq $true)
    $C = @($FB.candidates)
    Check "  at least one father name for the settings patient" ($C.Count -ge 1) "(0 candidates)"
    $BadItem = $C | Where-Object { -not (Same-Fields $_ @("father_name","patient_count")) } | Select-Object -First 1
    Check "  every candidate has exactly father_name, patient_count" ($null -eq $BadItem) (Show-Fields $BadItem)
    $BadCount = $C | Where-Object { -not ($_.patient_count -is [int] -or $_.patient_count -is [long]) -or $_.patient_count -lt 1 } | Select-Object -First 1
    Check "  every patient_count is a whole number >= 1" ($null -eq $BadCount) "(got $($BadCount.patient_count))"
    $SortBad = $null
    for ($i = 0; $i -lt $C.Count - 1; $i++) {
        $a = $C[$i]; $b = $C[$i + 1]
        $ok = ($a.patient_count -gt $b.patient_count) -or ($a.patient_count -eq $b.patient_count -and (Ordered-Ok $a.father_name $b.father_name))
        if (-not $ok) { $SortBad = "position $($i+1): '$($a.father_name)' ($($a.patient_count)) before '$($b.father_name)' ($($b.patient_count))"; break }
    }
    Check "  sorted: highest patient_count first, ties alphabetical" ($null -eq $SortBad) "($SortBad)"
    if ($C.Count -lt 50) {
        Check "  total_candidates = number returned (fewer than the default limit 50 came back)" ($FB.total_candidates -eq $C.Count) "(returned $($C.Count), total_candidates $($FB.total_candidates))"
    } else {
        Check "  total_candidates >= number returned" ($FB.total_candidates -ge $C.Count) "(returned $($C.Count), total_candidates $($FB.total_candidates))"
    }
    $Moji = $C | Where-Object { Test-Mojibake $_.father_name } | Select-Object -First 1
    Check "  Arabic father names are real Arabic (not garbled)" ($null -eq $Moji) "(got '$($Moji.father_name)')"
    $Wanted = Normalize-Name $PatientFatherName
    if (-not ($C | Where-Object { (Normalize-Name $_.father_name) -eq $Wanted })) {
        Info "the settings father name is not among the candidates as typed (it may be shown in English for these records)"
    }
    $AllTotal = $FB.total_candidates

    $r = DirApi "/patients/father-names?$FN&limit=1"
    Check "father-names limit=1 -> 200 with at most 1 candidate" ($r.StatusCode -eq 200 -and @($r.Body.candidates).Count -le 1) (Got $r)
    if ($r.StatusCode -eq 200) {
        Check "  total_candidates does not change with limit (counts all matches)" ($r.Body.total_candidates -eq $AllTotal) "(limit=1 total $($r.Body.total_candidates), no-limit total $AllTotal)"
    }
}
$r = DirApi "/patients/father-names?first_name=$(Q $PatientFirstName)"
Check "father-names without last_name -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)
Check "  message: Both 'first_name' and 'last_name' are required" ($r.Body.message -eq "Both 'first_name' and 'last_name' are required") "(got '$($r.Body.message)')"
$r = DirApi "/patients/father-names?last_name=$(Q $PatientLastName)"
Check "father-names without first_name -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)
$r = DirApi "/patients/father-names?$FN&limit=0"
Check "father-names limit=0 -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)
Check "  message: limit must be between 1 and 200" ($r.Body.message -eq "limit must be between 1 and 200") "(got '$($r.Body.message)')"
$r = DirApi "/patients/father-names?$FN&limit=201"
Check "father-names limit=201 -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)
$r = DirApi "/patients/father-names?$FN&limit=200"
Check "father-names limit=200 -> 200" ($r.StatusCode -eq 200) (Got $r)
$r = DirApi "/patients/father-names?first_name=ZzNoSuchName&last_name=ZzNoSuchFamily"
Check "father-names with no match -> 200, empty list, total 0" ($r.StatusCode -eq 200 -and @($r.Body.candidates).Count -eq 0 -and $r.Body.total_candidates -eq 0) (Got $r)
$r = DirApi "/patients/father-names?$FN" -NoKey
Check "father-names without key -> 401 UNAUTHORIZED" (Is-Error $r 401 "UNAUTHORIZED") (Got $r)

# ================================================================ PART 2B
Section "Part 2B: GET /hr-workers"

$HrFields = @("employee_id","full_name","job_id","job_title","administration_id","administration_name","section_id","section_name","department_id","department_name","is_manager","is_active")
$r = DirApi "/hr-workers"
Check "hr-workers -> 200" ($r.StatusCode -eq 200) (Got $r)
$HrTotal = $null
if ($r.StatusCode -eq 200) {
    Check "  envelope: success, items, total, limit, offset" (Same-Fields $r.Body @("success","items","total","limit","offset")) (Show-Fields $r.Body)
    Check "  default limit is 10, offset 0" ($r.Body.limit -eq 10 -and $r.Body.offset -eq 0) "(limit $($r.Body.limit), offset $($r.Body.offset))"
    Check "  at most 10 items" ((Items $r).Count -le 10) "(got $((Items $r).Count))"
    $HrTotal = $r.Body.total
    Info "hr-workers total = $HrTotal"
}

# A sample large enough to find a worker with all three levels filled in.
$r = DirApi "/hr-workers?limit=500"
Check "hr-workers limit=500 -> 200" ($r.StatusCode -eq 200) (Got $r)
$Sample = Items $r
if ($Sample.Count -gt 0) {
    $BadItem = $Sample | Where-Object { -not (Same-Fields $_ $HrFields) } | Select-Object -First 1
    Check "  every worker has exactly the 12 documented fields" ($null -eq $BadItem) (Show-Fields $BadItem)
    $BadActive = $Sample | Where-Object { -not ($_.is_active -is [bool]) } | Select-Object -First 1
    Check "  is_active is true/false on every worker" ($null -eq $BadActive) "(got '$($BadActive.is_active)')"
    $Moji = $Sample | Where-Object { (Test-Mojibake $_.full_name) -or (Test-Mojibake $_.administration_name) -or (Test-Mojibake $_.section_name) -or (Test-Mojibake $_.department_name) } | Select-Object -First 1
    Check "  Arabic names and unit names are real Arabic (not garbled)" ($null -eq $Moji) "(employee $($Moji.employee_id))"
    $NoUnit = @($Sample | Where-Object { -not $_.administration_name }).Count
    if ($NoUnit -gt 0) { Info "$NoUnit of $($Sample.Count) sampled workers have no administration_name" }
}

$Full = $Sample | Where-Object { $_.administration_name -and $_.section_name -and $_.department_name } | Select-Object -First 1
if ($Sample.Count -gt 0) {
    $W = $Sample[0]
    $r = DirApi "/hr-workers/$(Q $W.employee_id)"
    Check "hr-workers/{id} -> 200" ($r.StatusCode -eq 200) (Got $r)
    if ($r.StatusCode -eq 200) {
        Check "  single worker object, no list envelope, 12 fields" (Same-Fields $r.Body $HrFields) (Show-Fields $r.Body)
        Check "  same employee_id as requested" ($r.Body.employee_id -eq $W.employee_id) "(asked $($W.employee_id), got $($r.Body.employee_id))"
    }
}
$r = DirApi "/hr-workers/999999999"
Check "hr-workers/{unknown} -> 404 WORKER_NOT_FOUND" (Is-Error $r 404 "WORKER_NOT_FOUND") (Got $r)

if ($HrTotal -ge 2) {
    $p1 = DirApi "/hr-workers?limit=1&offset=0"; $p2 = DirApi "/hr-workers?limit=1&offset=1"
    $a = (Items $p1) | Select-Object -First 1; $b = (Items $p2) | Select-Object -First 1
    Check "paging: offset=1 gives a different worker, same total" ($a -and $b -and $a.employee_id -ne $b.employee_id -and $p2.Body.total -eq $HrTotal) "(offset0 $($a.employee_id), offset1 $($b.employee_id), total $($p2.Body.total))"
}
$r = DirApi "/hr-workers?limit=0"
Check "hr-workers limit=0 -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)
$r = DirApi "/hr-workers?limit=501"
Check "hr-workers limit=501 -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)
$r = DirApi "/hr-workers?offset=-1"
Check "hr-workers offset=-1 -> 422 VALIDATION_ERROR" (Is-Error $r 422 "VALIDATION_ERROR") (Got $r)

function Filter-Total([string]$Query) {
    $x = DirApi "/hr-workers?$Query&limit=500"
    if ($x.StatusCode -ne 200) { return @{ Ok = $false; Total = $null; Items = @(); R = $x } }
    return @{ Ok = $true; Total = $x.Body.total; Items = (Items $x); R = $x }
}

if ($Full) {
    $Adm = $Full.administration_name; $Sec = $Full.section_name; $Dep = $Full.department_name
    Info "filter tests use worker $($Full.employee_id): $Adm / $Sec / $Dep"

    foreach ($Level in @(@("administration", $Adm, "administration_name"), @("section", $Sec, "section_name"), @("department", $Dep, "department_name"))) {
        $Param = $Level[0]; $Name = $Level[1]; $Field = $Level[2]
        $f = Filter-Total "$Param=$(Q $Name)"
        Check "filter $Param=<name> -> 200 with at least 1 worker" ($f.Ok -and $f.Total -ge 1) (Got $f.R)
        if ($f.Ok) {
            $Target = Normalize-Name $Name
            if ($Param -eq "department") {
                $Wrong = $f.Items | Where-Object { (Normalize-Name $_.department_name) -ne $Target } | Select-Object -First 1
                Check "  every worker returned is in that department" ($null -eq $Wrong) "(employee $($Wrong.employee_id) is in '$($Wrong.department_name)')"
            } else {
                $Wrong = $f.Items | Where-Object { (Normalize-Name $_.$Field) -ne $Target } | Select-Object -First 1
                Check "  every worker returned is under that $Param (including units below it)" ($null -eq $Wrong) "(employee $($Wrong.employee_id) has $Field '$($Wrong.$Field)')"
            }
            $Variant = "  " + (Normalize-Name $Name) + "  "
            $v = Filter-Total "$Param=$(Q $Variant)"
            Check "  same result with extra spaces and unified spelling" ($v.Ok -and $v.Total -eq $f.Total) "(original $($f.Total), variant $($v.Total))"
            Set-Variable -Name "Total_$Param" -Value $f.Total
            Set-Variable -Name "Items_$Param" -Value $f.Items
        }
    }
    # Hierarchy: the lower level's workers that sit under THIS parent must all be in the
    # parent's result. (Names can repeat elsewhere in the tree - 3iSoft returns both units -
    # so the lower level's plain total may legitimately be larger.)
    foreach ($Pair in @(@("administration", "section", $Adm, "administration_name"), @("section", "department", $Sec, "section_name"))) {
        $Up = $Pair[0]; $Down = $Pair[1]; $UpName = Normalize-Name $Pair[2]; $UpField = $Pair[3]
        $UpTotal = Get-Variable -Name "Total_$Up" -ValueOnly -ErrorAction SilentlyContinue
        $UpItems = @(Get-Variable -Name "Items_$Up" -ValueOnly -ErrorAction SilentlyContinue)
        $DownItems = @(Get-Variable -Name "Items_$Down" -ValueOnly -ErrorAction SilentlyContinue)
        if ($null -eq $UpTotal -or $DownItems.Count -eq 0) { continue }
        $Under = @($DownItems | Where-Object { (Normalize-Name $_.$UpField) -eq $UpName })
        Check "hierarchy: $Up total >= its $Down workers under it" ($UpTotal -ge $Under.Count) "($Up $UpTotal, $Down workers under it $($Under.Count))"
        if ($UpTotal -le 500) {
            $UpIds = @{}; foreach ($w in $UpItems) { $UpIds[$w.employee_id] = $true }
            $Missing = $Under | Where-Object { -not $UpIds.ContainsKey($_.employee_id) } | Select-Object -First 1
            Check "  every $Down worker under it is in the $Up result" ($null -eq $Missing) "(employee $($Missing.employee_id) missing)"
        }
    }
    $f = Filter-Total "administration=$(Q $Adm)&department=$(Q $Dep)"
    Check "two filters together (AND) -> at least 1, not more than either alone" ($f.Ok -and $f.Total -ge 1 -and $f.Total -le $Total_department) "(AND total $($f.Total), department alone $Total_department)"
} else {
    Info "no worker in the first 500 has all three levels filled in: filter tests skipped"
}
$f = Filter-Total "administration=$(Q 'ZzNoSuchUnit 123')"
Check "filter with an unknown name -> 200, empty, total 0" ($f.Ok -and $f.Total -eq 0 -and $f.Items.Count -eq 0) (Got $f.R)
if ($null -ne $HrTotal) {
    $r = DirApi "/hr-workers?section="
    Check "empty filter (?section=) is ignored: same total as no filter" ($r.StatusCode -eq 200 -and $r.Body.total -eq $HrTotal) "(got $($r.StatusCode), total $($r.Body.total) vs $HrTotal)"
}
$r = DirApi "/hr-workers" -NoKey
Check "hr-workers without key -> 401 UNAUTHORIZED" (Is-Error $r 401 "UNAUTHORIZED") (Got $r)

# ================================================================ PART 2C
Section "Part 2C: ER current visits ($ErBaseUrl/current-visits)"

$r = Er "/current-visits" $ErApiKey
Check "ER current-visits -> 200" ($r.StatusCode -eq 200) (Got $r)
if ($r.StatusCode -eq 200) {
    Check "  Content-Type is JSON in UTF-8" ($r.ContentType -match "application/json" -and $r.ContentType -match "utf-8") "(got '$($r.ContentType)')"
    Check "  envelope: success, items, total" (Same-Fields $r.Body @("success","items","total")) (Show-Fields $r.Body)
    $V = Items $r
    Check "  total = number of items (full list, no paging)" ($r.Body.total -eq $V.Count) "(total $($r.Body.total), items $($V.Count))"
    Info "patients in the ER right now: $($V.Count)"
    if ($V.Count -eq 0) {
        Info "the ER list is empty right now: field checks skipped. Run again when patients are in the ER."
    } else {
        $ErFields = @("er_visit_id","first_name","father_name","last_name","arrival_time","gender","age","chief_complaint")
        $BadItem = $V | Where-Object { -not (Same-Fields $_ $ErFields) } | Select-Object -First 1
        Check "  every visit has exactly the 8 documented fields (none missing)" ($null -eq $BadItem) (Show-Fields $BadItem)
        $BadId = $V | Where-Object { -not ($_.er_visit_id -is [string]) -or -not $_.er_visit_id } | Select-Object -First 1
        Check "  er_visit_id is a non-empty text value" ($null -eq $BadId) "(got '$($BadId.er_visit_id)')"
        $Dupes = @($V | Group-Object er_visit_id | Where-Object { $_.Count -gt 1 })
        Check "  er_visit_id is unique in the list" ($Dupes.Count -eq 0) "(repeated: $(($Dupes | ForEach-Object { $_.Name }) -join ', '))"
        $IsoRx = '^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?[+-]\d{2}:\d{2}$'
        $BadTime = $V | Where-Object { -not ($_.arrival_time -is [string]) -or $_.arrival_time -notmatch $IsoRx } | Select-Object -First 1
        Check "  arrival_time is ISO 8601 with a time-zone offset" ($null -eq $BadTime) "(got '$($BadTime.arrival_time)')"
        $BadAge = $V | Where-Object { $null -ne $_.age -and (-not ($_.age -is [int] -or $_.age -is [long]) -or $_.age -lt 0 -or $_.age -gt 130) } | Select-Object -First 1
        Check "  age is a whole number 0-130, or null" ($null -eq $BadAge) "(got '$($BadAge.age)')"
        $OddGender = @($V | Where-Object { $null -ne $_.gender -and $_.gender -ne $AR_MALE -and $_.gender -ne $AR_FEMALE })
        if ($OddGender.Count -gt 0) { Info "$($OddGender.Count) visit(s) have a gender other than the two Arabic words (raw code, allowed): $(($OddGender | ForEach-Object { $_.gender } | Select-Object -Unique) -join ', ')" }
        $Moji = $V | Where-Object { (Test-Mojibake $_.first_name) -or (Test-Mojibake $_.father_name) -or (Test-Mojibake $_.last_name) -or (Test-Mojibake $_.chief_complaint) -or (Test-Mojibake $_.gender) } | Select-Object -First 1
        Check "  Arabic names and complaints are real Arabic (not garbled)" ($null -eq $Moji) "(visit $($Moji.er_visit_id))"
        $SortBad = $null
        for ($i = 0; $i -lt $V.Count - 1; $i++) {
            try {
                $ta = [DateTimeOffset]::Parse($V[$i].arrival_time); $tb = [DateTimeOffset]::Parse($V[$i + 1].arrival_time)
            } catch { $SortBad = "unreadable arrival_time"; break }
            if ($ta -gt $tb) { $SortBad = "visit $($V[$i].er_visit_id) ($($V[$i].arrival_time)) before $($V[$i+1].er_visit_id) ($($V[$i+1].arrival_time))"; break }
            if ($ta -eq $tb) {
                $ia = 0L; $ib = 0L
                $tie = if ([long]::TryParse($V[$i].er_visit_id, [ref]$ia) -and [long]::TryParse($V[$i+1].er_visit_id, [ref]$ib)) { $ia -le $ib } else { [string]::CompareOrdinal($V[$i].er_visit_id, $V[$i+1].er_visit_id) -le 0 }
                if (-not $tie) { $SortBad = "same time, visit $($V[$i].er_visit_id) before $($V[$i+1].er_visit_id)"; break }
            }
        }
        Check "  sorted: earliest arrival first, equal times by visit id" ($null -eq $SortBad) "($SortBad)"
        $NullComplaints = @($V | Where-Object { $null -eq $_.chief_complaint }).Count
        $NullAges = @($V | Where-Object { $null -eq $_.age }).Count
        Info "visits without chief_complaint: $NullComplaints, without age: $NullAges (null is allowed)"
    }
    $r2 = Er "/current-visits" $ErApiKey
    if ($r2.StatusCode -eq 200) {
        Info "a second call 1 moment later returned $(@(Items $r2).Count) visits (the list is live)"
    }
}
$r = Er "/current-visits" $null
Check "ER without key -> 401 UNAUTHORIZED" (Is-Error $r 401 "UNAUTHORIZED") (Got $r)
if ($ApiKey -ne $ErApiKey) {
    $r = Er "/current-visits" $ApiKey
    Check "ER rejects the Directory API key (keys are separate) -> 401" ($r.StatusCode -eq 401) (Got $r)
} else {
    Info "ApiKey and ErApiKey are the same in settings.txt: the 'separate keys' check is skipped"
}

# ================================================================ RESULT
Write-Host ""
Write-Host ("=" * 64)
Write-Host "RESULT: $PassCount passed, $FailCount failed, $($Infos.Count) info"
Write-Host ("=" * 64)
if ($FailCount -gt 0) {
    Write-Host ""
    Write-Host "Failures:" -ForegroundColor Red
    foreach ($f in $Failures) { Write-Host "  - $f" -ForegroundColor Red }
    exit 1
}
Write-Host "No failures." -ForegroundColor Green
exit 0
