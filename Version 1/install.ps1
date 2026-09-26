<#
.SYNOPSIS
    Frappe ECC - Universal Installation Script for Windows PowerShell
.DESCRIPTION
    Installs Frappe ECC into Antigravity, Claude Code, Cursor, or all supported editors.
.EXAMPLE
    .\install.ps1 -Profile minimal -Target antigravity
#>

[CmdletBinding()]
param (
    [string]$Profile = "minimal",
    [string]$Target = "antigravity",
    [switch]$DryRun
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$pythonCmd = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { "python3" } else { $null }

$argsList = @("--profile", $Profile, "--target", $Target)
if ($DryRun) {
    $argsList += "--dry-run"
}

if ($pythonCmd) {
    & $pythonCmd "$scriptDir\bin\frappe_ecc_install.py" @argsList
} elseif (Get-Command node -ErrorAction SilentlyContinue) {
    & node "$scriptDir\bin\frappe-ecc.js" @argsList
} else {
    Write-Error "Python 3 or Node.js is required to install Frappe ECC."
    exit 1
}
