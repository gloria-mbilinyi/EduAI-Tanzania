"""Back up SQLite consistently, migrate additively, and verify all old rows."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from datetime import datetime,timezone
from sqlalchemy import inspect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from app.core.database import engine
from app.migrate import migrate

def digest(conn,table):
    rows=conn.exec_driver_sql('SELECT * FROM "'+table.replace('"','""')+'" ORDER BY 1').fetchall()
    return len(rows),hashlib.sha256(repr(rows).encode()).hexdigest()

def upgrade(directory):
    if engine.dialect.name!='sqlite':raise SystemExit('This backup helper supports SQLite. For PostgreSQL take and verify pg_dump before python -m app.migrate.')
    source=Path(engine.url.database).resolve()
    if not source.is_file():raise SystemExit('Existing database not found; no new database was created. Use setup only for a new installation.')
    directory=Path(directory).resolve();directory.mkdir(parents=True,exist_ok=True)
    backup=directory/('eduai-before-upgrade-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.sqlite.backup')
    # Reuse the verified engine connection; Windows sandbox paths may contain '#'.
    with engine.connect() as source_connection,sqlite3.connect(backup) as dst:
        # The destination is a new disposable backup, never the live database.
        # Avoid journal filename length limits on deeply nested Windows paths.
        dst.execute('PRAGMA journal_mode=OFF')
        source_connection.connection.driver_connection.backup(dst)
        if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Backup integrity check failed')
    with engine.connect() as conn:
        before={t:digest(conn,t) for t in inspect(conn).get_table_names() if t!='schema_migrations'}
    migrate()
    with engine.connect() as conn:
        after={t:digest(conn,t) for t in before}
        if before!=after:raise RuntimeError('Legacy rows changed unexpectedly. Stop the application and inspect the verified backup.')
        versions=list(conn.exec_driver_sql('SELECT version FROM schema_migrations ORDER BY version').scalars())
    result={'backup':str(backup),'backup_integrity':'ok','legacy_tables_unchanged':len(before),'schema_versions':versions}
    print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--backup-dir',default=str(ROOT/'work/backups'))
    upgrade(parser.parse_args().backup_dir)
