param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { & $Python -m venv .venv }
& '.\.venv\Scripts\python.exe' -m pip install -r backend/requirements.lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed' }
Push-Location -LiteralPath frontend
try { npm ci; if ($LASTEXITCODE -ne 0) { throw 'Frontend installation failed' } } finally { Pop-Location }
Push-Location -LiteralPath backend
try { & '..\.venv\Scripts\python.exe' -m app.seed; if ($LASTEXITCODE -ne 0) { throw 'Seed failed' } } finally { Pop-Location }
Write-Host 'Setup complete. Run scripts/run.ps1 or follow README terminal commands.'
