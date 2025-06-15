"""
conftest.py  – shared pytest fixtures for Trading-Simulation-Game
-----------------------------------------------------------------
* Ensures project packages (backend.app …) are importable.
* Creates an in-memory SQLite database for each test session.
* Exposes `db`  – a SQLAlchemy session fixture.
* Exposes `client` – FastAPI TestClient fixture (uses the same DB).
"""

import os
# Ensure DATABASE_URL is available so backend.app.core.database doesn't error
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

# ── 1. repo root on PYTHONPATH  ──────────────────────────────────────────────
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]   # repo root (one level up from tests/)
sys.path.append(str(ROOT))                   # make `backend` package importable


# ── 2. pytest, SQLAlchemy, FastAPI imports  ──────────────────────────────────
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from backend.app.core.database import Base  # your project's DB Base
from backend.app.main import app                     # your FastAPI instance


# ── 3. set up in-memory SQLite engine  ───────────────────────────────────────
TEST_DB_URL = "sqlite+pysqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# create schema once per test run
Base.metadata.create_all(bind=engine)


# ── 4. dependency override so the app uses the test DB ───────────────────────
def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# import the original get_db dependencies from individual API modules
from backend.app.api.order import get_db as order_get_db
from backend.app.api.trade import get_db as trade_get_db
from backend.app.api.position import get_db as position_get_db

# override them to point at the in-memory test DB
app.dependency_overrides[order_get_db] = _override_get_db
app.dependency_overrides[trade_get_db] = _override_get_db
app.dependency_overrides[position_get_db] = _override_get_db


# ── 5. pytest fixtures ───────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def db():
    """Direct access to the test DB (session-wide)."""
    yield TestingSessionLocal()

@pytest.fixture(scope="function")
def client():
    """
    FastAPI TestClient that runs each test in its own transaction,
    which rolls back automatically for isolation.
    """
    # open a txn
    connection = engine.connect()
    trans = connection.begin()
    TestingSessionLocal.configure(bind=connection)

    with TestClient(app) as c:
        yield c

    # roll back
    trans.rollback()
    connection.close()