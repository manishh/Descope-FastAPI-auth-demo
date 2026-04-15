import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db_utils import init_db, seed_users

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    seed_users()

def test_login_success():
    response = client.post(
        "/login",
        data={"username": "manish@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_failure():
    response = client.post(
        "/login",
        data={"username": "manish@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_me_protected():
    # Unauthorized
    response = client.get("/me")
    assert response.status_code == 401

    # Authorized
    login_res = client.post(
        "/login",
        data={"username": "manish@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "manish@example.com"

def test_refresh_token():
    login_res = client.post(
        "/login",
        data={"username": "manish@example.com", "password": "password123"}
    )
    refresh_token = login_res.json()["refresh_token"]
    response = client.post(f"/refresh?token={refresh_token}")
    assert response.status_code == 200
    assert "access_token" in response.json()