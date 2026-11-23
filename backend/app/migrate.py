"""Versioned baseline migration. Run python -m app.migrate from backend/."""
from sqlalchemy import text
from .core.database import engine, Base
from . import models

def migrate():
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, description VARCHAR(200) NOT NULL)'))
        if conn.execute(text('SELECT version FROM schema_migrations WHERE version=1')).first() is None:
            Base.metadata.create_all(conn)
            conn.execute(text("INSERT INTO schema_migrations VALUES (1, 'EduAI normalized baseline')"))

if __name__ == '__main__':
    migrate()
    print('Schema migration 001 applied or already present')
