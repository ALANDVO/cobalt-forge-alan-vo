from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.prd_service import PRDService
from app.models import User, UserRole, PRDStatus
from pydantic import BaseModel

router = APIRouter(prefix="/prds", tags=["prds"])

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

class PC(BaseModel):
    title: str

class PR(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

@router.post("", response_model=PR)
async def create_p(data: PC, sid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    return await PRDService(db).create_prd(sid, u.id, data.title)

@router.get("", response_model=List[PR])
async def list_p(sid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    return await PRDService(db).list_prds(sid)

@router.get("/{pid}", response_model=PR)
async def get_p(pid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    p = await PRDService(db).get_prd(pid)
    if not p: raise HTTPException(404, "Not found")
    return p

@router.post("/{pid}/gen", response_model=PR)
async def gen_p(pid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    p = await PRDService(db).gen(pid)
    if not p: raise HTTPException(404, "Not found")
    return p

@router.post("/{pid}/fin", response_model=PR)
async def fin_p(pid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    p = await PRDService(db).fin(pid)
    if not p: raise HTTPException(404, "Not found")
    return p

@router.get("/{pid}/cov")
async def cov_p(pid: uuid.UUID, u: User = Depends(get_user), db: AsyncSession = Depends(get_db)):
    return await PRDService(db).check(pid)