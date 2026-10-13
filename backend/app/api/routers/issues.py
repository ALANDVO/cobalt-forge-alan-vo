from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import datetime

from app.core.database import get_db
from app.services.issue_service import IssueService
from app.models import User, UserRole, IssueStatus, IssueTrackerType
from pydantic import BaseModel

router = APIRouter(prefix="/issues", tags=["issues"])

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

class IC(BaseModel):
    title: str
    description: str
    acceptance_criteria: List[str] = []
    decision_refs: List[str] = []
    blockers: List[uuid.UUID] = []
    priority: int = 0
    tracker_type: IssueTrackerType = IssueTrackerType.LOCAL

class IR(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    priority: int
    acceptance_criteria: List[str]
    decision_refs: List[str]
    blockers: List[uuid.UUID]
    commit_ref: Optional[str]
    tracker_type: str
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

@router.post("", response_model=IR)
async def ci(d: IC, pid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await IssueService(db).create_issue(pid, d.title, d.description, d.acceptance_criteria, d.decision_refs, d.blockers, d.priority, d.tracker_type, x.id)

@router.get("", response_model=List[IR])
async def li(pid: uuid.UUID, s: Optional[IssueStatus] = None, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await IssueService(db).list_issues(pid, s)

@router.get("/{iid}", response_model=IR)
async def gi(iid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    i = await IssueService(db).get_issue(iid)
    if not i: raise HTTPException(404, "Not found")
    return i

@router.patch("/{iid}/status", response_model=IR)
async def uis(iid: uuid.UUID, s: IssueStatus, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    i = await IssueService(db).update_issue_status(iid, s)
    if not i: raise HTTPException(404, "Not found")
    return i

@router.post("/{iid}/comp", response_model=IR)
async def ci2(iid: uuid.UUID, sha: str, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    i = await IssueService(db).complete_issue(iid, sha)
    if not i: raise HTTPException(404, "Not found")
    return i

@router.get("/prds/{pid}/frontier")
async def fi(pid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await IssueService(db).get_frontier_issues(pid)

@router.post("/prds/{pid}/gen")
async def gi2(pid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    is_ = await IssueService(db).generate_issues_from_prd(pid)
    return {"issues": is_, "count": len(is_)}