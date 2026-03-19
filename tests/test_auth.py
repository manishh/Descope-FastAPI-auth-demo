"""
Tests for /auth/login, /auth/me, and /auth/refresh.
A fresh in-memory-equivalent SQLite DB is created for every test (see conftest.py).
"""
from tests.conftest import TEST_EMAIL, TEST_PASSWORD


# ---------------------------------------------------------------------------
# /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_success_returns_both_tokens(self, client):
        resp = client.post("/auth/login", data={"username": TEST_EMAIL, "password": TEST_PASSWORD})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    def test_wrong_password_is_401(self, client):
        resp = client.post("/auth/login", data={"username": TEST_EMAIL, "password": "wrong"})
        assert resp.status_code == 401

    def test_unknown_email_is_401(self, client):
        resp = client.post("/auth/login", data={"username": "nobody@example.com", "password": TEST_PASSWORD})
        assert resp.status_code == 401

    def test_missing_credentials_is_422(self, client):
        resp = client.post("/auth/login")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# /auth/me
# ---------------------------------------------------------------------------

class TestMe:
    def test_returns_profile_with_valid_token(self, client, auth_headers):
        resp = client.get("/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == TEST_EMAIL
        assert "name" in body
        assert "bio" in body
        assert "password_hash" not in body  # never leak the hash

    def test_no_token_is_401(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    def test_malformed_token_is_401(self, client):
        resp = client.get("/auth/me", headers={"Authorization": "Bearer not.a.token"})
        assert resp.status_code == 401

    def test_refresh_token_rejected_as_access_token(self, client, tokens):
        # A refresh token must not be usable as an access token
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /auth/refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    def test_returns_new_token_pair(self, client, tokens):
        resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body

    def test_new_access_token_is_usable(self, client, tokens):
        refresh_resp = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
        new_access = refresh_resp.json()["access_token"]
        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {new_access}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == TEST_EMAIL

    def test_access_token_rejected_as_refresh_token(self, client, tokens):
        resp = client.post("/auth/refresh", json={"refresh_token": tokens["access_token"]})
        assert resp.status_code == 401

    def test_invalid_refresh_token_is_401(self, client):
        resp = client.post("/auth/refresh", json={"refresh_token": "garbage"})
        assert resp.status_code == 401
