param(
    [string]$BaseUrl = "http://localhost:6000/api/directory/v1",
    [string]$ApiKey = "change_me",
    [string]$PatientFirstName = "Danielle",
    [string]$PatientFatherName = "Alexander",
    [string]$PatientLastName = "Hill"
)

# Hard pass/fail regression suite for THIS mock, proving it matches the
# OpenAPI v1.1 contract (see vendor-deliverable/API_Implementation_Requirements.md
# and vendor-deliverable/2026-09-08_v1.1-gap-analysis.md). Not an
# exploratory tester - every check is a real assertion with a real exit
# code, so "100%" is an objective, scriptable fact, not something to
# eyeball from green text.

$Failures = New-Object System.Collections.ArrayList
$PassCount = 0
$FailCount = 0

function Invoke-DirectoryApi {
    # Deliberately NOT using Invoke-WebRequest. Its handling of error
    # response bodies (400+) has proven inconsistent across different
    # Windows PowerShell builds/machines - $_.ErrorDetails.Message worked on
    # one machine and came back empty on another for the identical request.
    # Talking to HttpWebRequest directly sidesteps that: we own the response
    # object on both the success AND error path, so reading its stream is
    # reliable regardless of which machine this runs on.
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
    Assert-Check "  patient field set exactly matches contract" (Test-FieldSet $FirstPatient @("patient_id","full_name","first_name","last_name","birth_date","age","sex")) "(fields: $($FirstPatient.PSObject.Properties.Name -join ', '))"
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

# 7. Workers: default limit is 10, field set, and q is a documented no-op
$r = Invoke-DirectoryApi -Path "/workers" -WithAuth
Assert-Check "GET /workers -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
Assert-Check "  default limit is 10, not 100" ($r.Body.limit -eq 10) "(got $($r.Body.limit))"
$WorkerTotalNoQ = $r.Body.total
$FirstWorker = $null
if ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0) { $FirstWorker = $r.Body.items[0] }
if ($FirstWorker) {
    Assert-Check "  worker field set exactly matches contract" (Test-FieldSet $FirstWorker @("employee_id","full_name","job_id","job_title","department_id","department_name","section_id","administration_id","is_manager","is_active")) "(fields: $($FirstWorker.PSObject.Properties.Name -join ', '))"
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
Write-Host ("=" * 60)
Write-Host "RESULT: $PassCount passed, $FailCount failed"
Write-Host ("=" * 60)

if ($FailCount -gt 0) {
    Write-Host ""
    Write-Host "Failures:" -ForegroundColor Red
    foreach ($f in $Failures) { Write-Host "  - $f" -ForegroundColor Red }
    exit 1
} else {
    Write-Host "100% pass." -ForegroundColor Green
    exit 0
}
