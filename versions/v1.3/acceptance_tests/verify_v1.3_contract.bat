@echo off
REM Double-click wrapper for verify_v1.3_contract.ps1. Passes any extra
REM arguments straight through, e.g.:
REM   verify_v1.3_contract.bat -BaseUrl http://localhost:6002/api/directory/v1 -CheckSourceDown
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_v1.3_contract.ps1" %*
set EXITCODE=%ERRORLEVEL%
echo.
pause
exit /b %EXITCODE%
