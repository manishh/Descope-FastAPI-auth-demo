# FastAPI JWT Authentication Demo

This project demonstrates a secure FastAPI application featuring JWT-based authentication, password hashing, and token-based session management.

## Setup

```bash
# Install required dependencies
pip install fastapi uvicorn "passlib[bcrypt]" python-jose[cryptography] python-multipart pytest httpx requests
```

## Run

```bash
uvicorn app.main:app --reload
```

## Docs

Visit http://localhost:8000/docs for the interactive API docs.

---

**Author:** Gemini Code Assist (Gemini 3 Flash Preview)
