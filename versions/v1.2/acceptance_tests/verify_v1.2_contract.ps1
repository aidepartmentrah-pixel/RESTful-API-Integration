param(
    [string]$BaseUrl = "http://localhost:6001/api/directory/v1",
    [string]$ApiKey = "change_me",
    [string]$PatientFirstName = "Danielle",
    [string]$PatientFatherName = "Alexander",
    [string]$PatientLastName = "Hill"
)

# Hard pass/fail regression suite for the v1.2 mock. Runs the FULL v1.1
# suite first (v1.2 must be a strict superset - no regressions), then
# checks each of the 5 proposed v1.2 additions individually. Each addition
# reports one of three states, not just pass/fail:
#   PASS                - implemented and behaves per the v1.2 spec
#   FAIL                - implemented but wrong (a real bug)
#   NOT-YET-IMPLEMENTED - route/field absent; expected before Period D,
#                         a real problem after it
# NOT-YET-IMPLEMENTED does not count as a failure for the exit code, so
# this script is safe to run at any point in Period C/D/E and still tell
# you the truth about where things stand.

$Failures = New-Object System.Collections.ArrayList
$PassCount = 0
$FailCount = 0
$FeatureLines = New-Object System.Collections.ArrayList

function Invoke-DirectoryApi {
    param([string]$Path, [switch]$WithAuth)
    $Uri = "$BaseUrl$Path"
    $Result = [PSCustomObject]@{ StatusCode = $null; Body = $null }

    $Request = [System.Net.HttpWebRequest]::Create($Uri)
    $Request.Method = "GET"
    $Request.Timeout = 10000
    $Request.Accept = "application/json"
    if ($WithAuth) { $Request.Headers.Add("X-API-Key", $ApiKey) }

    $Response = $null
    try {
        $Response = $Request.GetResponse()
    } catch [System.Net.WebException] {
        $Response = $_.Exception.Response
        if (-not $Response) {
            $Result.Body = $_.Exception.Message
            return $Result
        }
    }

    $Result.StatusCode = [int]$Response.StatusCode
    $Stream = $Response.GetResponseStream()
    $MemStream = New-Object System.IO.MemoryStream
    $Stream.CopyTo($MemStream)
    $Utf8Text = [System.Text.Encoding]::UTF8.GetString($MemStream.ToArray())
    try { $Result.Body = $Utf8Text | ConvertFrom-Json } catch { $Result.Body = $Utf8Text }
    $Response.Close()

    return $Result
}

function Assert-Check {
    param([string]$Name, [bool]$Condition, [string]$Detail = "")
    if ($Condition) {
        Write-Host "PASS  $Name" -ForegroundColor Green
        $script:PassCount++
    } else {
        Write-Host "FAIL  $Name  $Detail" -ForegroundColor Red
        $script:FailCount++
        [void]$Failures.Add("$Name  $Detail")
    }
}

function Test-FieldSet {
    param($Obj, [string[]]$ExpectedFields)
    if ($null -eq $Obj) { return $false }
    $Actual = @($Obj.PSObject.Properties.Name | Sort-Object)
    $Expected = @($ExpectedFields | Sort-Object)
    return (Compare-Object $Actual $Expected -SyncWindow 0).Count -eq 0
}

function Report-Feature {
    param([string]$Name, [string]$State, [string]$Detail = "")
    $Color = switch ($State) {
        "PASS" { "Green" }
        "NOT-YET-IMPLEMENTED" { "Yellow" }
        default { "Red" }
    }
    $Line = "{0,-24} {1}" -f $Name, $State
    Write-Host $Line -ForegroundColor $Color
    if ($Detail) { Write-Host "  $Detail" -ForegroundColor $Color }
    [void]$FeatureLines.Add($Line)
    if ($State -eq "FAIL") {
        $script:FailCount++
        [void]$Failures.Add("$Name  $Detail")
    } elseif ($State -eq "PASS") {
        $script:PassCount++
    }
}

Write-Host "=== Part 1: full v1.1 suite (must remain a strict superset) ===" -ForegroundColor Cyan
Write-Host "Verifying $BaseUrl against the OpenAPI v1.1 contract" -ForegroundColor Cyan
Write-Host ""

# 1. Health
$r = Invoke-DirectoryApi -Path "/health"
Assert-Check "GET /health -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
Assert-Check "  service == his-general-directory" ($r.Body.service -eq "his-general-directory") "(got $($r.Body.service))"
Assert-Check "  api_version == 1.0.0" ($r.Body.api_version -eq "1.0.0") "(got $($r.Body.api_version))"

# 2. Patients, no criteria -> 422 VALIDATION_ERROR
$r = Invoke-DirectoryApi -Path "/patients" -WithAuth
Assert-Check "GET /patients (no criteria) -> 422" ($r.StatusCode -eq 422) "(got $($r.StatusCode))"
Assert-Check "  error == VALIDATION_ERROR" ($r.Body.error -eq "VALIDATION_ERROR") "(got $($r.Body.error))"

# 3. A lone name field is rejected
$r = Invoke-DirectoryApi -Path "/patients?first_name=$([uri]::EscapeDataString($PatientFirstName))" -WithAuth
Assert-Check "GET /patients?first_name=<alone> -> 422" ($r.StatusCode -eq 422) "(got $($r.StatusCode))"
Assert-Check "  error == VALIDATION_ERROR" ($r.Body.error -eq "VALIDATION_ERROR") "(got $($r.Body.error))"

# 3b. first_name + last_name without father_name is still rejected
$r = Invoke-DirectoryApi -Path "/patients?first_name=$([uri]::EscapeDataString($PatientFirstName))&last_name=$([uri]::EscapeDataString($PatientLastName))" -WithAuth
Assert-Check "GET /patients?first_name=&last_name= (no father) -> 422" ($r.StatusCode -eq 422) "(got $($r.StatusCode))"
Assert-Check "  error == VALIDATION_ERROR" ($r.Body.error -eq "VALIDATION_ERROR") "(got $($r.Body.error))"

# 4. Full first+father+last trio -> 200, field set
$NameQuery = "first_name=$([uri]::EscapeDataString($PatientFirstName))&father_name=$([uri]::EscapeDataString($PatientFatherName))&last_name=$([uri]::EscapeDataString($PatientLastName))"
$r = Invoke-DirectoryApi -Path "/patients?$NameQuery&limit=5" -WithAuth
Assert-Check "GET /patients?first_name=&father_name=&last_name= -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
$FirstPatient = $null
if ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0) { $FirstPatient = $r.Body.items[0] }
Assert-Check "  at least one result" ($null -ne $FirstPatient) "(0 results - try -PatientFirstName/-PatientFatherName/-PatientLastName with a real seeded name)"
if ($FirstPatient) {
    Assert-Check "  patient_id has no P- prefix" ($FirstPatient.patient_id -notmatch "^P-") "(got $($FirstPatient.patient_id))"
}

# 5. Patient exact lookup + 404
if ($FirstPatient) {
    $r = Invoke-DirectoryApi -Path "/patients/$($FirstPatient.patient_id)" -WithAuth
    Assert-Check "GET /patients/{id} -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
}
$r = Invoke-DirectoryApi -Path "/patients/999999999" -WithAuth
Assert-Check "GET /patients/{bogus} -> 404" ($r.StatusCode -eq 404) "(got $($r.StatusCode))"
Assert-Check "  error == PATIENT_NOT_FOUND" ($r.Body.error -eq "PATIENT_NOT_FOUND") "(got $($r.Body.error))"

# 6. Doctors field set + active_only
$r = Invoke-DirectoryApi -Path "/doctors?limit=5" -WithAuth
Assert-Check "GET /doctors -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
$DefaultTotal = $r.Body.total
$FirstDoctor = $null
if ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0) { $FirstDoctor = $r.Body.items[0] }
if ($FirstDoctor) {
    Assert-Check "  doctor field set exactly matches contract" (Test-FieldSet $FirstDoctor @("doctor_id","full_name","specialty_id","specialty_name","department_id","department_name","is_active")) "(fields: $($FirstDoctor.PSObject.Properties.Name -join ', '))"
    Assert-Check "  doctor_id has no D- prefix" ($FirstDoctor.doctor_id -notmatch "^D-") "(got $($FirstDoctor.doctor_id))"
}
$r = Invoke-DirectoryApi -Path "/doctors?active_only=false&limit=5" -WithAuth
Assert-Check "GET /doctors?active_only=false -> total >= default total" ($r.Body.total -ge $DefaultTotal) "(active_only=false total=$($r.Body.total), default total=$DefaultTotal)"

if ($FirstDoctor) {
    $r = Invoke-DirectoryApi -Path "/doctors/$($FirstDoctor.doctor_id)" -WithAuth
    Assert-Check "GET /doctors/{id} -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
}
$r = Invoke-DirectoryApi -Path "/doctors/999999999" -WithAuth
Assert-Check "GET /doctors/{bogus} -> 404" ($r.StatusCode -eq 404) "(got $($r.StatusCode))"
Assert-Check "  error == DOCTOR_NOT_FOUND" ($r.Body.error -eq "DOCTOR_NOT_FOUND") "(got $($r.Body.error))"

# 7. Workers: default limit is 10, q is a documented no-op
$r = Invoke-DirectoryApi -Path "/workers" -WithAuth
Assert-Check "GET /workers -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
Assert-Check "  default limit is 10, not 100" ($r.Body.limit -eq 10) "(got $($r.Body.limit))"
$WorkerTotalNoQ = $r.Body.total
$FirstWorker = $null
if ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0) { $FirstWorker = $r.Body.items[0] }
if ($FirstWorker) {
    Assert-Check "  employee_id has no E- prefix" ($FirstWorker.employee_id -notmatch "^E-") "(got $($FirstWorker.employee_id))"
}
$r = Invoke-DirectoryApi -Path "/workers?q=ThisShouldNotFilterAnything&limit=10" -WithAuth
Assert-Check "  q has no effect on /workers (matches contract + confirmed real behavior)" ($r.Body.total -eq $WorkerTotalNoQ) "(no-q total=$WorkerTotalNoQ, with-q total=$($r.Body.total))"

if ($FirstWorker) {
    $r = Invoke-DirectoryApi -Path "/workers/$($FirstWorker.employee_id)" -WithAuth
    Assert-Check "GET /workers/{id} -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
    Assert-Check "  is_active is true on exact lookup" ($r.Body.is_active -eq $true) "(got $($r.Body.is_active))"
}
$r = Invoke-DirectoryApi -Path "/workers/999999999" -WithAuth
Assert-Check "GET /workers/{bogus} -> 404" ($r.StatusCode -eq 404) "(got $($r.StatusCode))"
Assert-Check "  error == WORKER_NOT_FOUND" ($r.Body.error -eq "WORKER_NOT_FOUND") "(got $($r.Body.error))"

# 8. Auth
$r = Invoke-DirectoryApi -Path "/doctors?limit=1"
Assert-Check "GET /doctors with no key -> 401" ($r.StatusCode -eq 401) "(got $($r.StatusCode))"
Assert-Check "  error == UNAUTHORIZED" ($r.Body.error -eq "UNAUTHORIZED") "(got $($r.Body.error))"

Write-Host ""
Write-Host "=== Part 2: the 5 proposed v1.2 additions ===" -ForegroundColor Cyan
Write-Host ""

# --- 1. father-names (implemented) ---
$r = Invoke-DirectoryApi -Path "/patients/father-names?first_name=$([uri]::EscapeDataString($PatientFirstName))&last_name=$([uri]::EscapeDataString($PatientLastName))" -WithAuth
if ($r.StatusCode -eq 404) {
    Report-Feature "father-names" "NOT-YET-IMPLEMENTED"
} elseif ($r.StatusCode -eq 200 -and $r.Body -and (Test-FieldSet $r.Body @("success","first_name","last_name","candidates","total_candidates"))) {
    Report-Feature "father-names" "PASS" "candidates=$($r.Body.total_candidates)"
} else {
    Report-Feature "father-names" "FAIL" "(status=$($r.StatusCode), fields: $($r.Body.PSObject.Properties.Name -join ', '))"
}

# --- 2. first-names (proposed) ---
$r = Invoke-DirectoryApi -Path "/patients/first-names?last_name=$([uri]::EscapeDataString($PatientLastName))" -WithAuth
if ($r.StatusCode -eq 404) {
    Report-Feature "first-names" "NOT-YET-IMPLEMENTED"
} elseif ($r.StatusCode -eq 200 -and $r.Body -and (Test-FieldSet $r.Body @("success","last_name","candidates","total_candidates"))) {
    Report-Feature "first-names" "PASS" "candidates=$($r.Body.total_candidates)"
} else {
    Report-Feature "first-names" "FAIL" "(status=$($r.StatusCode), fields: $($r.Body.PSObject.Properties.Name -join ', '))"
}

# --- 3. worker section_name / administration_name (proposed) ---
if ($FirstWorker -and ($FirstWorker.PSObject.Properties.Name -notcontains "section_name")) {
    Report-Feature "worker-section-admin" "NOT-YET-IMPLEMENTED"
} elseif ($FirstWorker -and (Test-FieldSet $FirstWorker @("employee_id","full_name","job_id","job_title","department_id","department_name","section_id","section_name","administration_id","administration_name","is_manager","is_active"))) {
    Report-Feature "worker-section-admin" "PASS"
} else {
    $Fields = if ($FirstWorker) { $FirstWorker.PSObject.Properties.Name -join ', ' } else { "(no worker in seed data)" }
    Report-Feature "worker-section-admin" "FAIL" "(fields: $Fields)"
}

# --- 4. patient encounter_type (proposed) ---
if ($FirstPatient -and ($FirstPatient.PSObject.Properties.Name -notcontains "encounter_type")) {
    Report-Feature "patient-encounter-type" "NOT-YET-IMPLEMENTED"
} elseif ($FirstPatient -and (Test-FieldSet $FirstPatient @("patient_id","full_name","first_name","last_name","birth_date","age","sex","encounter_type"))) {
    Report-Feature "patient-encounter-type" "PASS" "encounter_type=$($FirstPatient.encounter_type)"
} else {
    $Fields = if ($FirstPatient) { $FirstPatient.PSObject.Properties.Name -join ', ' } else { "(no patient in seed data)" }
    Report-Feature "patient-encounter-type" "FAIL" "(fields: $Fields)"
}

# --- 5. GET /er/current-visits (proposed) ---
$r = Invoke-DirectoryApi -Path "/er/current-visits" -WithAuth
if ($r.StatusCode -eq 404) {
    Report-Feature "er-current-visits" "NOT-YET-IMPLEMENTED"
} elseif ($r.StatusCode -eq 200 -and $r.Body -and (Test-FieldSet $r.Body @("success","items","total"))) {
    Report-Feature "er-current-visits" "PASS" "total=$($r.Body.total)"
} else {
    Report-Feature "er-current-visits" "FAIL" "(status=$($r.StatusCode))"
}

Write-Host ""
Write-Host ("=" * 60)
Write-Host "RESULT: $PassCount passed, $FailCount failed"
Write-Host ("=" * 60)

if ($FailCount -gt 0) {
    Write-Host ""
    Write-Host "Failures:" -ForegroundColor Red
    foreach ($f in $Failures) { Write-Host "  - $f" -ForegroundColor Red }
    exit 1
} else {
    Write-Host "0 real failures (NOT-YET-IMPLEMENTED lines above are informational, not failures)." -ForegroundColor Green
    exit 0
}
