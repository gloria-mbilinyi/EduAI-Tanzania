import subprocess
from sqlalchemy import create_engine, text, inspect
from app.migrate import migrate
from app.seed import seed
from sqlalchemy.orm import Session

def test_upgrade_preserves_every_legacy_row_and_is_idempotent(tmp_path):
    old_schema = subprocess.check_output(['git', 'show', 'b45aa52:docs/architecture/SCHEMA.sql'], text=True)
    engine = create_engine('sqlite:///' + str(tmp_path / 'existing.db'))
    with engine.begin() as conn:
        for statement in old_schema.split(';'):
            if statement.strip(): conn.exec_driver_sql(statement)
    with Session(engine) as db:
        seed(db, 'Migration-only-fictional-password')
    with engine.connect() as conn:
        tables = inspect(conn).get_table_names()
        before = {t: list(conn.exec_driver_sql(f'SELECT * FROM "{t}"')) for t in tables}
    migrate(engine)
    migrate(engine)
    with engine.connect() as conn:
        for table, rows in before.items():
            assert list(conn.exec_driver_sql(f'SELECT * FROM "{table}"')) == rows
        assert conn.execute(text('SELECT COUNT(*) FROM submission_attempts')).scalar() > 0
        assert conn.execute(text('SELECT MIN(score) FROM grade_history')).scalar() == 45
        assert conn.execute(text('SELECT COUNT(*) FROM schema_migrations')).scalar() == 2
