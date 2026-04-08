from fastapi import APIRouter
import requests

from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)


@router.get("/health")
def health_check():
    return {"status": "All is well...!"}


@router.get("/zen-wisdom")
def zen_quote():
    resp = requests.get("https://zenquotes.io/api/random/")
    _zquote = resp.json()[0] if resp.status_code == 200 else {"q": "No Zen wisdom today.", "a": ""}
    return {"quote": _zquote.get("q"), "attribution": _zquote.get("a")}
    