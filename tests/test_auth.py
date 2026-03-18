from pathlib import Path
import sys
import os
import httpx

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import db_utils
from app.main import app, startup_event


@pytest.fixture()
async def client(tmp_path: Path):
    os.environ["BCRYPT_ROUNDS"] = "4"
    test_db = tmp_path / "test_auth.db"
    original_db_path = db_utils.DB_PATH
    db_utils.DB_PATH = test_db

    db_utils.init_db()
    db_utils.seed_users(
        [
            {
                "name": "Test User",
                "email": "test@example.com",
                "bio": "Auth test account",
                "password": "test-password",
            }
        ]
    )
    startup_event()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client

    db_utils.DB_PATH = original_db_path


async def _login(client: httpx.AsyncClient):
    response = await client.post(
        "/login",
        json={"email": "test@example.com", "password": "test-password"},
    )
    assert response.status_code == 200
    return response.json()


@pytest.mark.anyio
async def test_login_returns_access_token(client: httpx.AsyncClient):
    payload = await _login(client)
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


@pytest.mark.anyio
async def test_me_requires_valid_token(client: httpx.AsyncClient):
    unauthorized = await client.get("/me")
    assert unauthorized.status_code == 401

    login_payload = await _login(client)
    response = await client.get(
        "/me",
        headers={"Authorization": f"Bearer {login_payload['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


@pytest.mark.anyio
async def test_refresh_returns_new_access_token(client: httpx.AsyncClient):
    login_payload = await _login(client)

    refresh_response = await client.post(
        "/refresh",
        json={"refresh_token": login_payload["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert "access_token" in refreshed
    assert refreshed["token_type"] == "bearer"

    me_response = await client.get(
        "/me",
        headers={"Authorization": f"Bearer {refreshed['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "test@example.com"
