from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import hashlib
import base64
import secrets

from app.core.database import get_db
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    nonce = secrets.token_urlsafe(32)
    auth_url = auth_service.auth_url(state, challenge, nonce)
    return {"auth_url": auth_url, "state": state, "code_verifier": verifier, "nonce": nonce}

@router.get("/callback")
async def cb(code: str, state: str, code_verifier: str):
    t = await auth_service.exchange(code, code_verifier)
    if not t: raise HTTPException(400, "Token exchange failed")
    ui = await auth_service.userinfo(t["access_token"])
    if not ui: raise HTTPException(400, "Failed to get user info")
    return {"access_token": t["access_token"], "refresh_token": t.get("refresh_token"), "userinfo": ui}