# FastAPI Project

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

## Docs

Visit http://localhost:8000/docs for the interactive API docs.

## Authentication Routes

This project now includes JWT-based authentication with the following endpoints:

- `POST /login` - Accepts `username` and `password`, returns `access_token` and `refresh_token`
- `GET /me` - Protected route that returns the authenticated user's profile using a valid `Bearer` access token
- `POST /refresh` - Accepts a `refresh_token` and returns a new access token and refresh token

## What changed

- Added `app/api/auth.py` to handle login, protected user lookup, token refresh, password hashing, and JWT signing/verification
- Updated `app/api/routes.py` to include the auth router
- Added `bcrypt` for password hashing and `python-jose[cryptography]` for JWT handling
- Added pytest coverage in `tests/test_auth.py` for login, protected `/me` access, and refresh behavior

---

**Author:** Github Copilot (`Raptor mini (Preview)`)
