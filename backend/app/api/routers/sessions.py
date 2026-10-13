from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid
from datetime import datetime
import json

from app.core.database import get_db
from app.services.grilling_service import GrillingService
from app.models import User, UserRole, SessionStatus, QuestionType, QuestionStatus
from pydantic import BaseModel
router = APIRouter(prefix="/sessions", tags=["sessions"])


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

class SC(BaseModel):
    title: str
    description: str = ""

class SR(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    status: str
    current_round: int
    created_at: datetime
    updated_at: datetime
    class Config: from_attributes = True

class RR(BaseModel):
    id: uuid.UUID
    round_number: int
    started_at: datetime
    class Config: from_attributes = True

class AC(BaseModel):
    assumption_text: str

class AR(BaseModel):
    id: uuid.UUID
    assumption_number: int
    assumption_text: str
    vetoed: bool
    class Config: from_attributes = True

class QC(BaseModel):
    question_text: str
    detailed_explanation: str = ""
    question_type: QuestionType = QuestionType.DETAIL
    prerequisites: List[int] = []
    options: List[dict] = []
    recommended_option: str = ""
    recommended_reason: str = ""

class AQ(BaseModel):
    answer: str

class QR(BaseModel):
    id: uuid.UUID
    question_number: int
    question_text: str
    detailed_explanation: str
    question_type: str
    prerequisites: List[int]
    options: List[dict]
    recommended_option: str
    recommended_reason: str
    status: str
    answer: str
    decision_record_id: Optional[uuid.UUID]
    class Config: from_attributes = True


def question_to_response(q) -> QR:
    return QR(
        id=q.id,
        question_number=q.question_number,
        question_text=q.question_text,
        detailed_explanation=q.detailed_explanation,
        question_type=q.question_type.value,
        prerequisites=json.loads(q.prerequisites) if q.prerequisites else [],
        options=json.loads(q.options) if q.options else [],
        recommended_option=q.recommended_option,
        recommended_reason=q.recommended_reason,
        status=q.status.value,
        answer=q.answer,
        decision_record_id=q.decision_record_id,
    )


@router.post("", response_model=SR)
async def c(data: SC, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await GrillingService(db).create_session(x.id, data.title, data.description)

@router.get("", response_model=List[SR])
async def l(x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await GrillingService(db).list_sessions(x.id)

@router.get("/{sid}", response_model=SR)
async def g(sid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    s = await GrillingService(db).get_session(sid)
    if not s: raise HTTPException(404, "Not found")
    return s

@router.post("/{sid}/rounds", response_model=RR)
async def sr(sid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    r = await GrillingService(db).start_round(sid)
    if not r: raise HTTPException(400, "Cannot start")
    return r

@router.post("/rounds/{rid}/questions", response_model=QR)
async def aq(rid: uuid.UUID, data: QC, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    q = await GrillingService(db).add_question(rid, data.question_text, data.detailed_explanation, data.question_type, data.prerequisites, data.options, data.recommended_option, data.recommended_reason)
    if not q: raise HTTPException(400, "Cannot add")
    return question_to_response(q)

@router.post("/rounds/{rid}/assumptions", response_model=AR)
async def aa(rid: uuid.UUID, data: AC, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    a = await GrillingService(db).add_assumption(rid, data.assumption_text)
    if not a: raise HTTPException(400, "Cannot add")
    return a

@router.post("/questions/{qid}/answer", response_model=QR)
async def an(qid: uuid.UUID, data: AQ, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    q = await GrillingService(db).answer_question(qid, data.answer, x.id)
    if not q: raise HTTPException(400, "Cannot answer")
    return question_to_response(q)

@router.post("/assumptions/{aid}/veto", response_model=AR)
async def va(aid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    a = await GrillingService(db).veto_assumption(aid)
    if not a: raise HTTPException(400, "Cannot veto")
    return a

@router.post("/{sid}/comp", response_model=SR)
async def cs(sid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    s = await GrillingService(db).complete_session(sid)
    if not s: raise HTTPException(400, "Cannot complete")
    return s

@router.get("/{sid}/prep")
async def pr(sid: uuid.UUID, x: User = Depends(u), db: AsyncSession = Depends(get_db)):
    return await GrillingService(db).prepare_round_questions(sid)