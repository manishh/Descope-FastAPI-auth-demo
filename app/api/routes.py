from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
import requests
from app.auth import (
    create_access_token, create_refresh_token, get_current_user, 
    verify_password, SECRET_KEY, ALGORITHM
)
from app.db_utils import get_user_by_email
from jose import jwt, JWTError

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "All is well...!"}


@router.get("/zen-wisdom")
def zen_quote():
    resp = requests.get("https://zenquotes.io/api/random/")
    _zquote = resp.json()[0] if resp.status_code == 200 else {"q": "No Zen wisdom today.", "a": ""}
    return {"quote": _zquote.get("q"), "attribution": _zquote.get("a")}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["email"]})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/refresh")
def refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get("type")
        if email is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": email})
    return {"access_token": new_access_token, "token_type": "bearer"}
    