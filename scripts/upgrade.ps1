param([string]$BackupDirectory = '')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (-not $BackupDirectory) { $BackupDirectory = Join-Path $projectRoot 'work\backups' }
Push-Location -LiteralPath (Join-Path $projectRoot 'backend')
try {
    & (Join-Path $projectRoot '.venv\Scripts\python.exe') (Join-Path $PSScriptRoot 'upgrade_database.py') --backup-dir $BackupDirectory
    if ($LASTEXITCODE -ne 0) { throw 'Upgrade stopped. Inspect the result before starting the application.' }
} finally { Pop-Location }
