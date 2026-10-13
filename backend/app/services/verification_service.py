from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from app.models import VerificationEvidence, EvidenceType, DecisionRecord, Issue


class VerificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_evidence(self, decision_id: uuid.UUID, evidence_type: EvidenceType, title: str, description: str, artifact_ref: Optional[str], passed: bool, verified_by: uuid.UUID, issue_id: Optional[uuid.UUID] = None) -> VerificationEvidence:
        e = VerificationEvidence(decision_id=decision_id, issue_id=issue_id, evidence_type=evidence_type, title=title, description=description, artifact_ref=artifact_ref, passed=passed, verified_by=verified_by)
        self.db.add(e)
        await self.db.commit()
        await self.db.refresh(e)
        return e

    async def get_decision_evidence(self, decision_id: uuid.UUID) -> List[VerificationEvidence]:
        r = await self.db.execute(select(VerificationEvidence).where(VerificationEvidence.decision_id == decision_id).order_by(VerificationEvidence.verified_at.desc()))
        return list(r.scalars().all())

    async def get_issue_evidence(self, issue_id: uuid.UUID) -> List[VerificationEvidence]:
        r = await self.db.execute(select(VerificationEvidence).where(VerificationEvidence.issue_id == issue_id).order_by(VerificationEvidence.verified_at.desc()))
        return list(r.scalars().all())

    async def get_coverage(self, decision_ids: List[uuid.UUID]) -> dict:
        if not decision_ids: return {"total": 0, "verified": 0, "failed": 0, "pending": 0, "details": []}
        r = await self.db.execute(select(VerificationEvidence).where(VerificationEvidence.decision_id.in_(decision_ids)))
        all_e = list(r.scalars().all())
        by_d = {}
        for e in all_e:
            if e.decision_id not in by_d: by_d[e.decision_id] = []
            by_d[e.decision_id].append(e)
        v = f = p = 0
        details = []
        for did in decision_ids:
            es = by_d.get(did, [])
            if not es: p += 1; details.append({"decision_id": str(did), "status": "pending", "evidence_count": 0})
            else:
                pc = sum(1 for e in es if e.passed)
                fc = sum(1 for e in es if not e.passed)
                if pc > 0 and fc == 0: v += 1; s = "verified"
                elif fc > 0: f += 1; s = "failed"
                else: p += 1; s = "pending"
                details.append({"decision_id": str(did), "status": s, "evidence_count": len(es), "passed": pc, "failed": fc})
        return {"total": len(decision_ids), "verified": v, "failed": f, "pending": p, "details": details}