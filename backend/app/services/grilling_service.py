from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid, json

from app.models import GrillingSession, GrillingRound, GrillingQuestion, GrillingAssumption, SessionStatus, QuestionType, QuestionStatus, DecisionRecord, DecisionStatus
from app.services.decision_service import DecisionService

class GrillingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ds = DecisionService(db)

    async def create_session(self, oid: uuid.UUID, t: str, d: str = "") -> GrillingSession:
        s = GrillingSession(owner_id=oid, title=t, description=d, status=SessionStatus.ACTIVE, current_round=0, question_counter=0, assumption_counter=0, design_tree="{}")
        self.db.add(s)
        await self.db.commit()
        await self.db.refresh(s)
        return s
    async def get_session(self, sid: uuid.UUID) -> Optional[GrillingSession]:
        r = await self.db.execute(select(GrillingSession).options(selectinload(GrillingSession.rounds).selectinload(GrillingRound.questions), selectinload(GrillingSession.rounds).selectinload(GrillingRound.assumptions), selectinload(GrillingSession.decisions)).where(GrillingSession.id == sid).execution_options(populate_existing=True))
        return r.scalar_one_or_none()
    async def list_sessions(self, oid: uuid.UUID) -> List[GrillingSession]:
        r = await self.db.execute(select(GrillingSession).where(GrillingSession.owner_id == oid).order_by(GrillingSession.created_at.desc()))
        return list(r.scalars().all())

    async def start_round(self, sid: uuid.UUID) -> Optional[GrillingRound]:
        s = await self.get_session(sid)
        if not s or s.status != SessionStatus.ACTIVE: return None
        rn = s.current_round + 1
        ro = GrillingRound(session_id=sid, round_number=rn, frontier_questions="[]", pivot_order="[]")
        self.db.add(ro)
        s.current_round = rn
        await self.db.commit()
        await self.db.refresh(ro)
        return ro

    async def add_question(self, rid: uuid.UUID, qt: str, de: str = "", qty: QuestionType = QuestionType.DETAIL, pre: List[int] = None, opt: List[dict] = None, ro: str = "", rr: str = "") -> Optional[GrillingQuestion]:
        r = await self.db.get(GrillingRound, rid)
        if not r: return None
        s = await self.db.get(GrillingSession, r.session_id)
        if not s: return None
        s.question_counter += 1
        q = GrillingQuestion(round_id=rid, session_id=s.id, question_number=s.question_counter, question_text=qt, detailed_explanation=de, question_type=qty, prerequisites=json.dumps(pre or []), options=json.dumps(opt or []), recommended_option=ro, recommended_reason=rr, status=QuestionStatus.PENDING)
        self.db.add(q)
        await self.db.commit()
        await self.db.refresh(q)
        return q

    async def add_assumption(self, rid: uuid.UUID, at: str) -> Optional[GrillingAssumption]:
        r = await self.db.get(GrillingRound, rid)
        if not r: return None
        s = await self.db.get(GrillingSession, r.session_id)
        if not s: return None
        s.assumption_counter += 1
        a = GrillingAssumption(round_id=rid, session_id=s.id, assumption_number=s.assumption_counter, assumption_text=at)
        self.db.add(a)
        await self.db.commit()
        await self.db.refresh(a)
        return a

    async def answer_question(self, qid: uuid.UUID, ans: str, aid: uuid.UUID) -> Optional[GrillingQuestion]:
        q = await self.db.get(GrillingQuestion, qid)
        if not q or q.status != QuestionStatus.PENDING: return None
        q.answer = ans
        q.status = QuestionStatus.ANSWERED
        q.answered_at = datetime.now(timezone.utc)
        d = await self.ds.create(q.session_id, aid, q.question_text, ans, ans, "", "", DecisionStatus.RESOLVED)
        q.decision_record_id = d.id
        await self.db.commit()
        await self.db.refresh(q)
        return q

    async def veto_assumption(self, aid: uuid.UUID) -> Optional[GrillingAssumption]:
        a = await self.db.get(GrillingAssumption, aid)
        if not a or a.vetoed: return None
        a.vetoed = True
        a.vetoed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(a)
        return a

    async def complete_session(self, sid: uuid.UUID) -> Optional[GrillingSession]:
        s = await self.db.get(GrillingSession, sid)
        if not s: return None
        r = await self.db.execute(select(func.count(GrillingQuestion.id)).where(GrillingQuestion.session_id == sid, GrillingQuestion.status == QuestionStatus.PENDING))
        if (r.scalar() or 0) > 0: raise ValueError("Pending questions remain")
        s.status = SessionStatus.COMPLETED
        s.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(s)
        return s

    def compute_frontier(self, s: GrillingSession) -> List[GrillingQuestion]:
        aq = [q for r in s.rounds for q in r.questions]
        an = {q.question_number for q in aq if q.status == QuestionStatus.ANSWERED}
        f = [q for q in aq if q.status == QuestionStatus.PENDING and all(p in an for p in json.loads(q.prerequisites) if q.prerequisites)]
        f.sort(key=lambda q: (q.question_type != QuestionType.PIVOT, q.question_number))
        return f

    async def prepare_round_questions(self, sid: uuid.UUID) -> Dict[str, Any]:
        s = await self.get_session(sid)
        if not s: return {"questions": [], "assumptions": []}
        f = self.compute_frontier(s)
        r = s.rounds[-1] if s.rounds else None
        return {"questions": [{"id": str(q.id), "number": f"Q{q.question_number}", "text": q.question_text, "explanation": q.detailed_explanation, "type": q.question_type.value, "options": json.loads(q.options) if q.options else [], "recommended": q.recommended_option, "recommended_reason": q.recommended_reason} for q in f], "assumptions": [{"id": str(a.id), "number": f"A{a.assumption_number}", "text": a.assumption_text, "vetoed": a.vetoed} for a in (r.assumptions if r else [])]}