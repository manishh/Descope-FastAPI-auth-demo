from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_returns_tokens():
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert "refresh_token" in data


def test_me_requires_valid_access_token():
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "secret123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()

    protected_response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert protected_response.status_code == 200
    user = protected_response.json()
    assert user["username"] == "testuser"
    assert user["email"] == "testuser@example.com"


def test_refresh_returns_new_access_token():
    login_response = client.post(
        "/login",
        json={"username": "testuser", "password": "secret123"},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    refreshed_data = refresh_response.json()
    assert refreshed_data["token_type"] == "bearer"
    assert refreshed_data["access_token"]
    assert refreshed_data["refresh_token"]


def test_login_fails_with_invalid_credentials():
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_me_fails_without_token():
    response = client.get("/me")
    assert response.status_code == 401
