from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.decision_service import DecisionService
from app.models import User, UserRole, DecisionStatus
from pydantic import BaseModel

router = APIRouter(prefix="/decisions", tags=["decisions"])

async def get_user(db: AsyncSession = Depends(get_db)) -> User:
    from sqlalchemy import select
    r = await db.execute(select(User).where(User.email == "demo@cobaltforge.local"))
    u = r.scalar_one_or_none()
    if not u:
        u = User(keycloak_sub="demo", email="demo@cobaltforge.local", name="Demo", role=UserRole.ADMIN)
        db.add(u)
        await db.commit()
        await db.refresh(u)
    return u

class DC(BaseModel):
    question: str
    answer: str
    normalized_requirement: str
    constraints: str = ""
    tags: str = ""

class DR(BaseModel):
    id: uuid.UUID
    stable_id: str
    question: str
    answer: str
    normalized_requirement: str
    constraints: str
    tags: str
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

@router.post("", response_model=DR)
async def create_d(data: DC, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app.models.session import GrillingSession, SessionStatus
    r = await db.execute(select(GrillingSession).where(GrillingSession.owner_id == u.id, GrillingSession.status == SessionStatus.ACTIVE).order_by(GrillingSession.created_at.desc()))
    s = r.scalar_one_or_none()
    if not s: raise HTTPException(400, "No active session")
    return await DecisionService(db).create(s.id, u.id, data.question, data.answer, data.normalized_requirement, data.constraints, data.tags)

@router.get("", response_model=List[DR])
async def list_d(sid: Optional[uuid.UUID] = None, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    if not sid:
        from sqlalchemy import select
        from app.models.session import GrillingSession, SessionStatus
        r = await db.execute(select(GrillingSession).where(GrillingSession.owner_id == u.id, GrillingSession.status == SessionStatus.ACTIVE).order_by(GrillingSession.created_at.desc()))
        s = r.scalar_one_or_none()
        if not s: return []
        sid = s.id
    return await DecisionService(db).list(sid)

@router.get("/{did}", response_model=DR)
async def get_d(did: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    d = await DecisionService(db).get(did)
    if not d: raise HTTPException(404, "Not found")
    return d

@router.get("/sessions/{sid}/coverage")
async def cov(sid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    return await DecisionService(db).coverage(sid)