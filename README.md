# FastAPI Project - OpenAI Codex Update

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Authentication

This app now includes JWT-based authentication with:

- `POST /login`: accepts `email` + `password`, returns `access_token`, `refresh_token`, and `token_type`.
- `GET /me`: protected route, requires `Authorization: Bearer <access_token>`.
- `POST /refresh`: accepts `refresh_token`, returns a new `access_token`.

Default seeded users use password `password123`.

## Route Summary

- `GET /`: root status message.
- `GET /health`: health check.
- `GET /zen-wisdom`: returns a quote from Zen Quotes API.
- `POST /login`: issue access/refresh tokens.
- `GET /me`: return current authenticated user profile.
- `POST /refresh`: issue a fresh access token using a valid refresh token.

## How Auth Was Implemented

- Password hashing and verification use `bcrypt`.
- JWT signing/verification use `python-jose` with `HS256`.
- Access and refresh tokens are issued with token-type claims (`access`/`refresh`) and expirations.
- `user_profiles` now includes a `password_hash` column (auto-added for existing DBs).
- DB startup init/seed runs via FastAPI lifespan startup.

## Tests

Pytest coverage was added for auth flows:

- login returns tokens
- `/me` rejects missing token and accepts valid token
- `/refresh` returns a new access token that works on `/me`

Run tests:

```bash
./venv/bin/pytest -q tests/test_auth.py
```

## Docs

Visit http://localhost:8000/docs for the interactive API docs.

---

**Author:** OpenAI Codex (`GPT-5.3-Codex`)
