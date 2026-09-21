# ============================================================================
# Frappe Autonomous Enterprise Studio (Frappe AES) - Windows Desktop Installer
# Creates a native Windows Desktop shortcut and Start Menu integration
# ============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LauncherBat = Join-Path $ScriptDir "Launch_FrappeAES_Studio.bat"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "Frappe AES Studio.lnk"

Write-Host "[*] Installing Frappe AES Desktop Studio Shortcut..." -ForegroundColor Cyan

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $LauncherBat
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "Frappe Autonomous Enterprise Studio (52 AI Agents No-Code Platform)"
$Shortcut.Save()

Write-Host "[SUCCESS] Created Desktop Shortcut: $ShortcutPath" -ForegroundColor Green
Write-Host "You can now double-click 'Frappe AES Studio' on your desktop to prompt and build apps!" -ForegroundColor Yellow
