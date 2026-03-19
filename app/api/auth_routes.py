from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.db_utils import get_user_by_email

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Authenticate with email + password; returns an access token and a refresh token."""
    user = get_user_by_email(form.username)
    if not user or not user["password_hash"] or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token_data = {"sub": user["email"]}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """Return the profile of the currently authenticated user."""
    email = current_user.get("sub")
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "bio": user["bio"],
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest):
    """Exchange a valid refresh token for a new access token and refresh token."""
    payload = decode_token(body.refresh_token, "refresh")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    token_data = {"sub": email}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
