# Preserving an existing database

Stop both application servers before upgrading. Keep the original database, uploads, and development secret together in a private backup location. Never run a reset command. The seed command skips a database that already has users.

From the repository root in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
.\scripts\upgrade.ps1 -BackupDirectory 'C:\EduAI-private-backups'
```

Use the same `DATABASE_URL` environment variable as the existing installation. Relative SQLite paths resolve from `backend` in these commands. The default application path is the repository-root `eduai.db` when DATABASE_URL is unset. No database was present at the start of this enhancement; migration compatibility was tested on a populated temporary baseline-schema database.

The helper uses SQLite's online backup API, checks backup integrity, records private row digests, applies forward-only migrations, and verifies that every pre-existing row is unchanged. Backups contain password hashes and personal records; keep them private and out of Git. A failed migration must be investigated before restarting. To recover, stop all servers, retain the failed database for diagnosis, and restore a verified backup with its matching application version. Do not roll an enhanced database back to old code while users are writing.

Version 1 is the original 28-table schema. Version 2 adds policies, attempts, additional-attempt grades, immutable feedback history, resubmission approvals, final selections, and recommendation snapshots. Version 3 adds typed-question settings, quiz review evidence, and pending manual responses. No legacy table is dropped, altered, or rebuilt. Submission remains the stable assessment record; its original Grade remains attempt 1. Attempts 2 and above use AttemptGrade. Old recommendation content overwritten before this upgrade cannot be recovered; current and future versions are snapshotted.

For PostgreSQL, take and verify a `pg_dump` backup and run `python -m app.migrate` from `backend`. PostgreSQL deployment and restoration have not been integration-tested here.

Optional Ollama is disabled by default. Check RAM, free disk, and GPU/VRAM before selecting a model with the school. This project never downloads a model. After separately installing one, set `OLLAMA_ENABLED=true` and `OLLAMA_MODEL` to its exact installed tag. The authenticated `/api/tutor/provider-health` endpoint checks availability. All core tools work without it.
