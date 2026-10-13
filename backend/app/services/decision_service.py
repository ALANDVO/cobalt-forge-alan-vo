from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from app.models import DecisionRecord, DecisionVersion, DecisionStatus
from app.models.session import GrillingSession

class DecisionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, sid: uuid.UUID, aid: uuid.UUID, q: str, a: str, nr: str, c: str = "", t: str = "", st: DecisionStatus = DecisionStatus.RESOLVED) -> DecisionRecord:
        s = await self.db.get(GrillingSession, sid)
        if not s: raise ValueError("Session not found")
        n = await self.db.execute(select(func.count(DecisionRecord.id)).where(DecisionRecord.session_id == sid))
        d = DecisionRecord(stable_id=f"DEC-{(n.scalar() or 0)+1:03d}", session_id=sid, author_id=aid, question=q, answer=a, normalized_requirement=nr, constraints=c, tags=t, status=st, version=1)
        self.db.add(d)
        await self.db.flush()
        self.db.add(DecisionVersion(record_id=d.id, version=1, question=q, answer=a, normalized_requirement=nr, constraints=c, tags=t, status=st, changed_by=aid, change_reason="Initial"))
        await self.db.commit()
        await self.db.refresh(d)
        return d

    async def get(self, did: uuid.UUID) -> Optional[DecisionRecord]:
        r = await self.db.execute(select(DecisionRecord).options(selectinload(DecisionRecord.versions)).where(DecisionRecord.id == did))
        return r.scalar_one_or_none()

    async def list(self, sid: uuid.UUID, st: Optional[DecisionStatus] = None) -> List[DecisionRecord]:
        q = select(DecisionRecord).where(DecisionRecord.session_id == sid)
        if st: q = q.where(DecisionRecord.status == st)
        q = q.order_by(DecisionRecord.created_at)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def update(self, did: uuid.UUID, aid: uuid.UUID, q: str = None, a: str = None, nr: str = None, c: str = None, t: str = None, st: DecisionStatus = None, r: str = "") -> Optional[DecisionRecord]:
        d = await self.get(did)
        if not d: return None
        self.db.add(DecisionVersion(record_id=d.id, version=d.version, question=d.question, answer=d.answer, normalized_requirement=d.normalized_requirement, constraints=d.constraints, tags=d.tags, status=d.status, changed_by=aid, change_reason=r or "Update"))
        if q is not None: d.question = q
        if a is not None: d.answer = a
        if nr is not None: d.normalized_requirement = nr
        if c is not None: d.constraints = c
        if t is not None: d.tags = t
        if st is not None: d.status = st
        d.version += 1
        d.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(d)
        return d

    async def coverage(self, sid: uuid.UUID) -> dict:
        d = await self.list(sid)
        t = len(d)
        r = sum(1 for x in d if x.status == DecisionStatus.RESOLVED)
        dr = sum(1 for x in d if x.status == DecisionStatus.DRAFT)
        rv = sum(1 for x in d if x.status == DecisionStatus.REVISED)
        s = sum(1 for x in d if x.status == DecisionStatus.SUPERSEDED)
        return {"total": t, "resolved": r, "draft": dr, "revised": rv, "superseded": s, "coverage_percentage": (r/t*100) if t else 0}