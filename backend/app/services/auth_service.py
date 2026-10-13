from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import Optional
from app.core.config import settings
import httpx

class AuthService:
    def __init__(self):
        self._jwks = None
        self._jwks_at = None

    def create_token(self, d: dict, e: Optional[timedelta] = None) -> str:
        td = d.copy()
        td.update({"exp": datetime.now(timezone.utc) + (e or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)), "iat": datetime.now(timezone.utc)})
        return jwt.encode(td, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def decode(self, t: str) -> Optional[dict]:
        try: return jwt.decode(t, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except JWTError: return None

    async def jwks(self) -> dict:
        if self._jwks and self._jwks_at and (datetime.now(timezone.utc) - self._jwks_at).total_seconds() < 3600: return self._jwks
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/certs")
            r.raise_for_status()
            self._jwks = r.json()
            self._jwks_at = datetime.now(timezone.utc)
            return self._jwks

    async def validate(self, t: str) -> Optional[dict]:
        try:
            j = await self.jwks()
            kid = jwt.get_unverified_header(t).get("kid")
            k = next((x for x in j.get("keys", []) if x.get("kid") == kid), None)
            if not k: return None
            return jwt.decode(t, k, algorithms=["RS256"], audience=settings.OIDC_CLIENT_ID, issuer=settings.OIDC_ISSUER_URL)
        except JWTError: return None

    def auth_url(self, state: str, challenge: str, nonce: str) -> str:
        p = {"client_id": settings.OIDC_CLIENT_ID, "redirect_uri": settings.OIDC_REDIRECT_URI, "response_type": "code", "scope": settings.OIDC_SCOPES, "state": state, "code_challenge": challenge, "code_challenge_method": "S256", "nonce": nonce}
        return f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/auth?{'&'.join(f'{k}={v}' for k,v in p.items())}"

    async def exchange(self, code: str, verifier: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=10) as c:
            try:
                r = await c.post(f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/token", data={"grant_type": "authorization_code", "client_id": settings.OIDC_CLIENT_ID, "client_secret": settings.OIDC_CLIENT_SECRET, "code": code, "redirect_uri": settings.OIDC_REDIRECT_URI, "code_verifier": verifier})
                r.raise_for_status()
                return r.json()
            except: return None

    async def refresh(self, rt: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=10) as c:
            try:
                r = await c.post(f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/token", data={"grant_type": "refresh_token", "client_id": settings.OIDC_CLIENT_ID, "client_secret": settings.OIDC_CLIENT_SECRET, "refresh_token": rt})
                r.raise_for_status()
                return r.json()
            except: return None

    async def userinfo(self, at: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=10) as c:
            try:
                r = await c.get(f"{settings.OIDC_ISSUER_URL}/protocol/openid-connect/userinfo", headers={"Authorization": f"Bearer {at}"})
                r.raise_for_status()
                return r.json()
            except: return None

auth_service = AuthService()