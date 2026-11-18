# v1.2 acceptance test for the local v1.2-dev mock (port 6001).
#
# Runs the SAME test the hospital's offline PC runs against the real 3iSoft
# servers (../offline_test_kit/), just with the mock's settings. One test,
# two targets: if it passes here and there, the mock matches the real API.
#
#   powershell -File verify_v1.2_contract.ps1                 # mock settings
#   powershell -File verify_v1.2_contract.ps1 -SettingsFile X # any settings file

param([string]$SettingsFile = "")

$Kit = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..\offline_test_kit"
if (-not $SettingsFile) { $SettingsFile = Join-Path $Kit "settings.local-mock.txt" }
& (Join-Path $Kit "run.ps1") -SettingsFile $SettingsFile
exit $LASTEXITCODE
