@echo off
REM Double-click to run the Hospital Directory API v1.2 test.
REM Edit settings.txt first (server address, API key, a real patient name).
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
pause
exit /b %EXITCODE%
