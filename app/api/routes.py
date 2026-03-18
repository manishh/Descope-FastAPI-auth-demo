from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
import requests

from app.auth import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_password,
)
from app.db_utils import get_user_by_email, get_user_by_id

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.get("/health")
async def health_check():
    return {"status": "All is well...!"}


@router.get("/zen-wisdom")
async def zen_quote():
    resp = requests.get("https://zenquotes.io/api/random/")
    _zquote = resp.json()[0] if resp.status_code == 200 else {"q": "No Zen wisdom today.", "a": ""}
    return {"quote": _zquote.get("q"), "attribution": _zquote.get("a")}


@router.post("/login")
async def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)
    if user is None or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return {
        "access_token": create_access_token(user_id=user["id"], email=user["email"]),
        "refresh_token": create_refresh_token(user_id=user["id"], email=user["email"]),
        "token_type": "bearer",
    }


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "bio": current_user["bio"],
    }


@router.post("/refresh")
async def refresh(payload: RefreshRequest):
    token_payload = decode_token(payload.refresh_token, expected_type="refresh")
    user = get_user_by_id(int(token_payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return {
        "access_token": create_access_token(user_id=user["id"], email=user["email"]),
        "token_type": "bearer",
    }
    
