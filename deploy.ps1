# ORBITE — build frontend + tests backend + redémarrage waitress.
# Usage : powershell -ExecutionPolicy Bypass -File deploy.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $root ".venv\Scripts\python.exe"

Write-Host "[1/3] Build frontend..."
Push-Location (Join-Path $root "frontend")
npm.cmd run build
if ($LASTEXITCODE -ne 0) { Pop-Location; exit $LASTEXITCODE }
Pop-Location

Write-Host "[2/3] Tests backend..."
Push-Location (Join-Path $root "backend")
& $py manage.py test
$testExit = $LASTEXITCODE
Pop-Location
if ($testExit -ne 0) { Write-Host "Tests en échec : deploiement annule."; exit $testExit }

Write-Host "[3/3] Redemarrage waitress..."
$port = if ($env:ORBITE_SERVE_PORT) { $env:ORBITE_SERVE_PORT } else { "8000" }
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $conn | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
}
New-Item -ItemType Directory -Force -Path (Join-Path $env:TEMP "opencode") | Out-Null
$env:ORBITE_SERVE_LOGFILE = Join-Path $env:TEMP "opencode\orbite.log"
Start-Process -FilePath $py -ArgumentList "serve.py" -WorkingDirectory (Join-Path $root "backend") -WindowStyle Hidden
Start-Sleep -Seconds 5
Write-Host "Serveur relance. (log : $env:ORBITE_SERVE_LOGFILE)"