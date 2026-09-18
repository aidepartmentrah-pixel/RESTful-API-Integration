@echo off
REM Double-click wrapper for verify_v1.2_contract.ps1. Passes any extra
REM arguments straight through, e.g.:
REM   verify_v1.2_contract.bat -BaseUrl http://localhost:6001/api/directory/v1
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_v1.2_contract.ps1" %*
set EXITCODE=%ERRORLEVEL%
echo.
pause
exit /b %EXITCODE%
