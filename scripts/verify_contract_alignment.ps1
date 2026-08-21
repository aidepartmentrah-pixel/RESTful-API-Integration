param(
    [string]$BaseUrl = "http://localhost:6000/api/directory/v1",
    [string]$ApiKey = "change_me",
    [string]$PatientSearch = "Danielle Johnson"
)

# Hard pass/fail regression suite for THIS mock, proving it matches the
# confirmed real-API behavior (see vendor-deliverable/API_Implementation_Requirements.md
# and the plan this was built from). Not an exploratory tester - every
# check is a real assertion with a real exit code, so "100%" is an
# objective, scriptable fact, not something to eyeball from green text.

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

Write-Host "Verifying $BaseUrl against the confirmed real-API contract" -ForegroundColor Cyan
Write-Host ""

# 1. Health
$r = Invoke-DirectoryApi -Path "/health"
Assert-Check "GET /health -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"

# 2. Patients, no criteria -> 422 VALIDATION_ERROR
$r = Invoke-DirectoryApi -Path "/patients" -WithAuth
Assert-Check "GET /patients (no criteria) -> 422" ($r.StatusCode -eq 422) "(got $($r.StatusCode))"
Assert-Check "  error == VALIDATION_ERROR" ($r.Body.error -eq "VALIDATION_ERROR") "(got $($r.Body.error))"

# 3. Patient search rejects a partial (single-word) name, same as the real API
$r = Invoke-DirectoryApi -Path "/patients?q=$([uri]::EscapeDataString($PatientSearch.Split(' ')[0]))" -WithAuth
Assert-Check "GET /patients?q=<single word> -> 422" ($r.StatusCode -eq 422) "(got $($r.StatusCode))"
Assert-Check "  error == VALIDATION_ERROR" ($r.Body.error -eq "VALIDATION_ERROR") "(got $($r.Body.error))"

# 4. Patient search field set
$r = Invoke-DirectoryApi -Path "/patients?q=$([uri]::EscapeDataString($PatientSearch))&limit=5" -WithAuth
Assert-Check "GET /patients?q=... -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
$PatientFound = $r.Success -or ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0)
$FirstPatient = $null
if ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0) { $FirstPatient = $r.Body.items[0] }
Assert-Check "  at least one result for '$PatientSearch'" ($null -ne $FirstPatient) "(0 results - try -PatientSearch with a real seeded name)"
if ($FirstPatient) {
    Assert-Check "  patient field set exactly matches contract" (Test-FieldSet $FirstPatient @("patient_id","full_name","first_name","last_name","birth_date","age","sex")) "(fields: $($FirstPatient.PSObject.Properties.Name -join ', '))"
}

# 5. Patient exact lookup + 404
if ($FirstPatient) {
    $r = Invoke-DirectoryApi -Path "/patients/$($FirstPatient.patient_id)" -WithAuth
    Assert-Check "GET /patients/{id} -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
}
$r = Invoke-DirectoryApi -Path "/patients/DOES-NOT-EXIST-999" -WithAuth
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
}
$r = Invoke-DirectoryApi -Path "/doctors?active_only=false&limit=5" -WithAuth
Assert-Check "GET /doctors?active_only=false -> total >= default total" ($r.Body.total -ge $DefaultTotal) "(active_only=false total=$($r.Body.total), default total=$DefaultTotal)"

if ($FirstDoctor) {
    $r = Invoke-DirectoryApi -Path "/doctors/$($FirstDoctor.doctor_id)" -WithAuth
    Assert-Check "GET /doctors/{id} -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
}
$r = Invoke-DirectoryApi -Path "/doctors/DOES-NOT-EXIST-999" -WithAuth
Assert-Check "GET /doctors/{bogus} -> 404" ($r.StatusCode -eq 404) "(got $($r.StatusCode))"
Assert-Check "  error == DOCTOR_NOT_FOUND" ($r.Body.error -eq "DOCTOR_NOT_FOUND") "(got $($r.Body.error))"

# 7. Workers field set (must include department_name now)
$r = Invoke-DirectoryApi -Path "/workers?limit=5" -WithAuth
Assert-Check "GET /workers -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
$FirstWorker = $null
if ($r.Body -and $r.Body.items -and $r.Body.items.Count -gt 0) { $FirstWorker = $r.Body.items[0] }
if ($FirstWorker) {
    Assert-Check "  worker field set exactly matches contract (incl. department_name)" (Test-FieldSet $FirstWorker @("employee_id","full_name","job_id","job_title","department_id","department_name","section_id","administration_id","is_manager","is_active")) "(fields: $($FirstWorker.PSObject.Properties.Name -join ', '))"
}
if ($FirstWorker) {
    $r = Invoke-DirectoryApi -Path "/workers/$($FirstWorker.employee_id)" -WithAuth
    Assert-Check "GET /workers/{id} -> 200" ($r.StatusCode -eq 200) "(got $($r.StatusCode))"
}
$r = Invoke-DirectoryApi -Path "/workers/DOES-NOT-EXIST-999" -WithAuth
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
