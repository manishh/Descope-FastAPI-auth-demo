# FastAPI Auth Demo - Claude Code Update

A FastAPI application demonstrating JWT-based authentication with bcrypt password hashing.

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

---

## API Routes

### General

| Method | Path | Auth required | Description |
|--------|------|---------------|-------------|
| `GET` | `/` | No | Health check — confirms the API is running |
| `GET` | `/health` | No | Returns `{ "status": "All is well...!" }` |
| `GET` | `/zen-wisdom` | No | Returns a random Zen quote from ZenQuotes |

### Auth (`/auth`)

| Method | Path | Auth required | Description |
|--------|------|---------------|-------------|
| `POST` | `/auth/login` | No | Exchange email + password for an access token and a refresh token |
| `GET` | `/auth/me` | Yes (access token) | Return the authenticated user's profile |
| `POST` | `/auth/refresh` | No | Exchange a valid refresh token for a new token pair |

#### `POST /auth/login`

Accepts `application/x-www-form-urlencoded` (OAuth2 password flow):

```
username=user@example.com&password=secret
```

Response:

```json
{
  "access_token": "<jwt>",
  "refresh_token": "<jwt>",
  "token_type": "bearer"
}
```

#### `GET /auth/me`

Requires `Authorization: Bearer <access_token>` header.

```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "bio": "..."
}
```

#### `POST /auth/refresh`

```json
{ "refresh_token": "<jwt>" }
```

Returns a fresh token pair in the same shape as `/auth/login`.

---

## Authentication Implementation

JWT-based auth was added with the following design decisions:

- **Password hashing** — `bcrypt` is called directly (`bcrypt.hashpw` / `bcrypt.checkpw`) instead of going through `passlib`. This avoids the `DeprecationWarning: 'crypt' is deprecated` warning that `passlib` triggers when imported on Python 3.12+.
- **JWT signing** — `python-jose` with `HS256`. Tokens carry a `token_type` claim (`"access"` or `"refresh"`) so the two token types cannot be used interchangeably.
- **Access tokens** expire after 15 minutes; **refresh tokens** expire after 7 days.
- **`/auth/me`** uses a FastAPI `Depends` on `OAuth2PasswordBearer`, so it integrates cleanly with the `/docs` UI.
- **Secret key** is read from the `SECRET_KEY` environment variable (falls back to a placeholder — override this in production).

## Running Tests

```bash
pytest tests/ -v
```

The test suite covers login (success + failure cases), the protected `/me` route (valid token, missing token, malformed token, wrong token type), and the `/refresh` endpoint (happy path, token reuse, invalid token).

---
**Author:** Claude Code (Sonnet 4.6)