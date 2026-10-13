from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.verification_service import VerificationService
from app.models import User, UserRole, EvidenceType
from pydantic import BaseModel

router = APIRouter(prefix="/verification", tags=["verification"])

async def u(db: AsyncSession = Depends(get_db)) -> User:
    from sqlalchemy import select
    r = await db.execute(select(User).where(User.email == "demo@cobaltforge.local"))
    x = r.scalar_one_or_none()
    if not x:
        x = User(keycloak_sub="demo", email="demo@cobaltforge.local", name="Demo", role=UserRole.ADMIN)
        db.add(x)
        await db.commit()
        await db.refresh(x)
    return x

class EC(BaseModel):
    evidence_type: EvidenceType
    title: str
    description: str = ""
    artifact_ref: Optional[str] = None
    passed: bool
    issue_id: Optional[uuid.UUID] = None

class ER(BaseModel):
    id: uuid.UUID
    decision_id: uuid.UUID
    issue_id: Optional[uuid.UUID]
    evidence_type: str
    title: str
    description: str
    artifact_ref: Optional[str]
    passed: bool
    verified_at: datetime
    class Config: from_attributes = True

@router.post("/evidence", response_model=ER)
async def ae(d: EC, did: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await VerificationService(db).add_evidence(did, d.evidence_type, d.title, d.description, d.artifact_ref, d.passed, x.id, d.issue_id)

@router.get("/decisions/{did}/evidence", response_model=List[ER])
async def gde(did: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await VerificationService(db).get_decision_evidence(did)

@router.get("/issues/{iid}/evidence", response_model=List[ER])
async def gie(iid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await VerificationService(db).get_issue_evidence(iid)

@router.get("/cov")
async def vc(dids: List[uuid.UUID], x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await VerificationService(db).get_coverage(dids)