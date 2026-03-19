import os
from datetime import datetime, timedelta, timezone
from typing import Literal

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-before-deploying-to-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def _create_token(
    data: dict,
    expires_delta: timedelta,
    token_type: Literal["access", "refresh"],
) -> str:
    payload = {
        **data,
        "exp": datetime.now(timezone.utc) + expires_delta,
        "token_type": token_type,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict) -> str:
    return _create_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access")


def create_refresh_token(data: dict) -> str:
    return _create_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh")


def decode_token(token: str, expected_type: Literal["access", "refresh"]) -> dict:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise exc
    if payload.get("token_type") != expected_type:
        raise exc
    return payload


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """FastAPI dependency — injects the decoded access-token payload."""
    return decode_token(token, "access")
