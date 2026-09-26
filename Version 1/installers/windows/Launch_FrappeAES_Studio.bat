@echo off
:: ============================================================================
:: Frappe Autonomous Enterprise Studio (Frappe AES) - Local Runtime Launcher
:: Starts the native Python Frappe Local Machine Runtime Server & Desk Application
:: ============================================================================
title Frappe Autonomous Enterprise Studio - Local Machine Runtime

set SCRIPT_DIR=%~dp0
set REPO_ROOT=%SCRIPT_DIR%..\..
cd /d "%REPO_ROOT%"

echo ==============================================================================
echo [*] Starting Frappe Autonomous Local Machine Runtime on http://localhost:8050...
echo [*] Integrated with 53 Autonomous AI Agents and Live Data Simulator
echo ==============================================================================

:: Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not detected in your PATH. Please install Python 3.9+.
    pause
    exit /b 1
)

:: Start the Python Local Runtime Server in the background or new window
start "Frappe Local Runtime Server" cmd /k "python bin\frappe_runtime_server.py 8050"

:: Wait 2 seconds for server to bind port
timeout /t 2 /nobreak >nul

echo [*] Opening Frappe Desk Studio in Browser...

:: Launch Edge in Dedicated App Mode
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" (
    start "" "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" --app="http://localhost:8050"
    goto :done
)

:: Launch Chrome in Dedicated App Mode
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    start "" "%ProgramFiles%\Google\Chrome\Application\chrome.exe" --app="http://localhost:8050"
    goto :done
)

:: Fallback to default browser
start "" "http://localhost:8050"

:done
echo [SUCCESS] Frappe Autonomous Desk is now running live on http://localhost:8050!
