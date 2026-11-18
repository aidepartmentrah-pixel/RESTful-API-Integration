# Reads settings.txt, runs the v1.2 test, saves the full output in results\.
# Plain ASCII on purpose, so Windows PowerShell 5.1 reads it the same everywhere.

param([string]$SettingsFile = "")

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $SettingsFile) { $SettingsFile = Join-Path $Here "settings.txt" }
Write-Host "Settings : $SettingsFile"

$Settings = @{}
foreach ($Line in (Get-Content -LiteralPath $SettingsFile -Encoding UTF8)) {
    $T = $Line.Trim()
    if ($T -eq "" -or $T.StartsWith("#")) { continue }
    $Eq = $T.IndexOf("=")
    if ($Eq -lt 1) { continue }
    $Settings[$T.Substring(0, $Eq).Trim()] = $T.Substring($Eq + 1).Trim()
}

$Names = @("BaseUrl", "ApiKey", "ErBaseUrl", "ErApiKey", "PatientFirstName", "PatientFatherName", "PatientLastName")
$Missing = $Names | Where-Object { -not $Settings[$_] }
if ($Missing) {
    Write-Host "settings.txt is missing: $($Missing -join ', ')" -ForegroundColor Red
    exit 2
}
$Unfilled = @("ApiKey", "ErApiKey") | Where-Object { $Settings[$_] -like "PUT-THE-*" }
if ($Unfilled) {
    Write-Host "Open settings.txt and fill in: $($Unfilled -join ', ')" -ForegroundColor Red
    exit 2
}

# Accept a full endpoint address pasted by mistake: keep only the base.
foreach ($K in @("BaseUrl", "ErBaseUrl")) {
    $Settings[$K] = $Settings[$K].TrimEnd("/") -replace "/current-visits$", ""
}

$ResultsDir = Join-Path $Here "results"
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
$Stamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $ResultsDir "v1.2-test_$Stamp.txt"

Start-Transcript -LiteralPath $LogFile | Out-Null
Write-Host "Hospital Directory API v1.2 - offline test (as delivered by 3iSoft)"
Write-Host "Computer : $env:COMPUTERNAME"
Write-Host "Patient  : $($Settings.PatientFirstName) $($Settings.PatientFatherName) $($Settings.PatientLastName)"
Write-Host "Started  : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

$Params = @{}
foreach ($N in $Names) { $Params[$N] = $Settings[$N] }
$ErrorActionPreference = "Continue"
& (Join-Path $Here "verify_v1.2_delivered.ps1") @Params
$Code = $LASTEXITCODE

Write-Host ""
Write-Host "Finished : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  (exit code $Code)"
Stop-Transcript | Out-Null
Write-Host ""
Write-Host "Full results saved to:" -ForegroundColor Cyan
Write-Host "  $LogFile"
exit $Code
