from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from app.migrate import migrate
from app.seed import seed
from sqlalchemy.orm import Session

def test_upgrade_preserves_every_legacy_row_and_is_idempotent(tmp_path,monkeypatch):
    old_schema = (Path(__file__).with_name('fixtures')/'001_schema.sql').read_text(encoding='utf-8')
    engine = create_engine('sqlite:///' + str(tmp_path / 'existing.db'))
    with engine.begin() as conn:
        for statement in old_schema.split(';'):
            if statement.strip(): conn.exec_driver_sql(statement)
    # A legacy fixture cannot call the upgraded performance service before migration.
    monkeypatch.setattr('app.seed.generate',lambda *args:('Preserved original recommendation',['Original evidence']))
    with Session(engine) as db:
        seed(db, 'Migration-only-fictional-password')
    with engine.connect() as conn:
        tables = inspect(conn).get_table_names()
        before = {t: list(conn.exec_driver_sql(f'SELECT * FROM "{t}"')) for t in tables}
    import importlib.util
    spec=importlib.util.spec_from_file_location('upgrade',Path(__file__).resolve().parents[2]/'scripts/upgrade_database.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    monkeypatch.setattr(helper,'engine',engine);monkeypatch.setattr(helper,'migrate',lambda:migrate(engine))
    result=helper.upgrade(tmp_path/'private-backups')
    assert Path(result['backup']).is_file() and result['backup_integrity']=='ok'
    migrate(engine)
    with engine.connect() as conn:
        for table, rows in before.items():
            assert list(conn.exec_driver_sql(f'SELECT * FROM "{table}"')) == rows
        assert conn.execute(text('SELECT COUNT(*) FROM submission_attempts')).scalar() > 0
        assert conn.execute(text('SELECT MIN(score) FROM grade_history')).scalar() == 45
        assert conn.execute(text('SELECT COUNT(*) FROM schema_migrations')).scalar() == 3
