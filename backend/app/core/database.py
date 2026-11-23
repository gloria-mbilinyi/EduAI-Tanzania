from datetime import datetime, timezone
from sqlalchemy import create_engine, event, Column, Integer, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

Base = declarative_base()
class Entity:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=now)

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {})
if DATABASE_URL.startswith('sqlite'):
    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
def get_db():
    with SessionLocal() as session:
        yield session
