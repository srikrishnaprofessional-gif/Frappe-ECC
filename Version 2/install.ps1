# Install Frappe ECC into Claude Code (default) or Cursor on Windows.
#   .\install.ps1                 Claude Code plugin, user scope
#   .\install.ps1 cursor [DIR]    Cursor rules into DIR\.cursor\rules
param([string]$Target = "claude", [string]$Project = ".")
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) { $Python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $Python) { Write-Error "Python 3.10+ is required"; exit 1 }
$env:PYTHONPATH = $Root
if ($Target -eq "cursor") {
    & $Python.Source -m frappe_ecc install cursor --project $Project
} else {
    & $Python.Source -m frappe_ecc install claude
}
exit $LASTEXITCODE
