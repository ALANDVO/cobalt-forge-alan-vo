from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
import uuid, json

from app.models import PRD, PRDDecisionMapping, PRDStatus, DecisionRecord, DecisionStatus, GrillingSession
from app.services.decision_service import DecisionService

class PRDService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ds = DecisionService(db)

    async def create_prd(self, sid: uuid.UUID, aid: uuid.UUID, t: str) -> PRD:
        s = await self.db.get(GrillingSession, sid)
        if not s: raise ValueError("Session not found")
        p = PRD(session_id=sid, author_id=aid, title=t, content="", status=PRDStatus.DRAFT, version=1, decision_coverage=json.dumps({}))
        self.db.add(p)
        await self.db.commit()
        await self.db.refresh(p)
        return p

    async def get_prd(self, pid: uuid.UUID) -> Optional[PRD]:
        r = await self.db.execute(select(PRD).options(selectinload(PRD.decision_mappings).selectinload(PRDDecisionMapping.decision)).where(PRD.id == pid))
        return r.scalar_one_or_none()

    async def list_prds(self, sid: uuid.UUID) -> List[PRD]:
        r = await self.db.execute(select(PRD).where(PRD.session_id == sid).order_by(PRD.created_at.desc()))
        return list(r.scalars().all())

    async def gen(self, pid: uuid.UUID) -> Optional[PRD]:
        p = await self.get_prd(pid)
        if not p: return None
        d = await self.ds.list_decisions(p.session_id, status=DecisionStatus.RESOLVED)
        cov = {}
        lines = [f"# {p.title}", "", f"**Session:** {p.session_id}", f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d')}", f"**Version:** {p.version}", "", "## Traceability", "", "| ID | Question | Requirement | Constraints | Status |", "|----|----------|-------------|-------------|--------|"]
        for d in d:
            req = d.normalized_requirement[:100] + ("..." if len(d.normalized_requirement)>100 else "")
            con = d.constraints[:80] + ("..." if len(d.constraints)>80 else "")
            lines.append(f"| {d.stable_id} | {d.question[:60]}... | {req} | {con} | {d.status.value} |")
            cov[str(d.id)] = "covered"
        lines.extend(["", "## User Stories", ""])
        for i, d in enumerate(d, 1):
            lines.extend([f"### US-{i:03d}: {d.question[:80]}", f"**Decision:** {d.stable_id}", f"**Requirement:** {d.normalized_requirement}", f"**Constraints:** {d.constraints or 'None'}", "", "**Acceptance Criteria:**", f"- [ ] {d.normalized_requirement}", *(f"- [ ] {c.strip()}" for c in d.constraints.split(";") if c.strip()), ""])
        lines.extend(["", "## Constraints", ""])
        for d in d:
            if d.constraints:
                lines.extend([f"### {d.stable_id}: {d.question[:60]}", d.constraints, ""])
        p.content = "\n".join(lines)
        p.decision_coverage = json.dumps(cov)
        p.updated_at = datetime.now(timezone.utc)
        for i, d in enumerate(d, 1):
            self.db.add(PRDDecisionMapping(prd_id=p.id, decision_id=d.id, user_story_refs=json.dumps([f"US-{i:03d}"]), constraint_refs=json.dumps([]), acceptance_criteria_refs=json.dumps([]), coverage_status="covered"))
        await self.db.commit()
        await self.db.refresh(p)
        return p

    async def fin(self, pid: uuid.UUID) -> Optional[PRD]:
        p = await self.get_prd(pid)
        if not p: return None
        p.status = PRDStatus.FINALIZED
        p.finalized_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(p)
        return p

    async def check(self, pid: uuid.UUID) -> dict:
        p = await self.get_prd(pid)
        if not p: return {"error": "PRD not found"}
        d = await self.ds.list_decisions(p.session_id)
        cov = json.loads(p.decision_coverage) if p.decision_coverage else {}
        m, s, c = [], [], []
        for d in d:
            st = cov.get(str(d.id), "missing")
            if st == "covered": c.append(d.stable_id)
            elif st == "stale": s.append(d.stable_id)
            else: m.append(d.stable_id)
        return {"total_decisions": len(d), "covered": len(c), "missing": len(m), "stale": len(s), "missing_ids": m, "stale_ids": s, "coverage_percentage": (len(c)/len(d)*100) if d else 100}