# ORBITE — verification rapide avant build : config Django + tests IA & paiement.
# Usage : powershell -ExecutionPolicy Bypass -File check.ps1
$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $root ".venv\Scripts\python.exe"

Push-Location (Join-Path $root "backend")
& $py manage.py check --deploy 2>&1 | Select-Object -First 5
Write-Host ""
& $py manage.py test apps.ai apps.payments --keepdb
Pop-Location
Write-Host "check.ps1 termine."