import secrets
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, get_db
from app.models import User
from app.core.security import token
from app.seed import seed

PASSWORD = secrets.token_urlsafe(18)

@pytest.fixture
def env():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    @event.listens_for(engine, 'connect')
    def constraints(conn, _): conn.execute('PRAGMA foreign_keys=ON')
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, expire_on_commit=False)()
    seed(db, PASSWORD)
    app.dependency_overrides[get_db] = lambda: db
    client = TestClient(app)
    users = {u.email.split('@')[0]: u for u in db.query(User)}
    def headers(handle): return {'Authorization': 'Bearer ' + token(users[handle])}
    yield client, db, users, headers
    app.dependency_overrides.clear()
    client.close()
    db.close()
    engine.dispose()
