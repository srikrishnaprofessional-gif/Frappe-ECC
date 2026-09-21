@echo off
:: ============================================================================
:: Frappe Autonomous Enterprise Studio (Frappe AES) - Windows Native Launcher
:: Launches the Studio in dedicated standalone desktop application mode
:: ============================================================================
title Frappe AES Desktop Studio

set SCRIPT_DIR=%~dp0
set STUDIO_HTML=%SCRIPT_DIR%..\..\studio\index.html

:: Normalize path
for %%i in ("%STUDIO_HTML%") do set ABS_STUDIO_HTML=%%~fi

echo [*] Launching Frappe Autonomous Enterprise Studio...
echo [*] Target Interface: %ABS_STUDIO_HTML%

:: Check if Microsoft Edge exists (installed by default on Windows 10/11)
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app="file:///%ABS_STUDIO_HTML:\=/%"
    goto :done
)

:: Check if Google Chrome exists
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app="file:///%ABS_STUDIO_HTML:\=/%"
    goto :done
)

:: Fallback to default browser
start "" "%ABS_STUDIO_HTML%"

:done
echo [SUCCESS] Frappe AES Studio is now active!
