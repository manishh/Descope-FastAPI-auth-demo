import pytest
from fastapi.testclient import TestClient

import app.db_utils as db_utils
from app.auth import hash_password
from app.db_utils import init_db, seed_users
from app.main import app

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "hunter2"


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Point DB_PATH at a fresh temp file for every test."""
    monkeypatch.setattr(db_utils, "DB_PATH", tmp_path / "test.db")
    init_db()
    seed_users([
        {
            "name": "Test User",
            "email": TEST_EMAIL,
            "bio": "Test bio",
            "password_hash": hash_password(TEST_PASSWORD),
        }
    ])
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Return Bearer headers for the test user."""
    resp = client.post("/auth/login", data={"username": TEST_EMAIL, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def tokens(client):
    """Return the full token payload for the test user."""
    resp = client.post("/auth/login", data={"username": TEST_EMAIL, "password": TEST_PASSWORD})
    assert resp.status_code == 200
    return resp.json()
