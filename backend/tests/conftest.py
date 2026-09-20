import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Set testing environment variables
os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "false"
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_bloop.db"
os.environ["ELEVENLABS_API_KEY"] = ""

from backend.app.main import app
from backend.app.db.session import engine, Base, SessionLocal
from backend.app.db.init_db import init_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    init_db(db)
    db.close()
    yield
    # Cleanup test db
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test_bloop.db"):
        try:
            os.remove("test_bloop.db")
        except Exception:
            pass


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
