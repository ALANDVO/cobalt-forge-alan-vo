from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from datetime import datetime, timezone
import uuid, json

from app.models import Issue, IssueStatus, IssueTrackerType, PRD

class IssueService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, pid: uuid.UUID, t: str, d: str, ac: List[str] = None, dr: List[str] = None, b: List[uuid.UUID] = None, p: int = 0, tt: IssueTrackerType = IssueTrackerType.LOCAL, aid: Optional[uuid.UUID] = None) -> Issue:
        if not await self.db.get(PRD, pid): raise ValueError("PRD not found")
        i = Issue(prd_id=pid, assignee_id=aid, tracker_type=tt, title=t, description=d, status=IssueStatus.OPEN, priority=p, acceptance_criteria=json.dumps(ac or []), decision_refs=json.dumps(dr or []), blockers=json.dumps([str(x) for x in b or []]))
        self.db.add(i)
        await self.db.commit()
        await self.db.refresh(i)
        return i

    async def get(self, iid: uuid.UUID) -> Optional[Issue]:
        r = await self.db.execute(select(Issue).options(selectinload(Issue.verification_evidence), selectinload(Issue.prd)).where(Issue.id == iid))
        return r.scalar_one_or_none()

    async def list(self, pid: uuid.UUID, s: Optional[IssueStatus] = None) -> List[Issue]:
        q = select(Issue).where(Issue.prd_id == pid)
        if s: q = q.where(Issue.status == s)
        q = q.order_by(Issue.priority.desc(), Issue.created_at)
        r = await self.db.execute(q)
        return list(r.scalars().all())

    async def update_status(self, iid: uuid.UUID, s: IssueStatus) -> Optional[Issue]:
        i = await self.get(iid)
        if not i: return None
        i.status = s
        if s == IssueStatus.DONE: i.closed_at = datetime.now(timezone.utc)
        i.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(i)
        return i

    async def comp(self, iid: uuid.UUID, sha: str) -> Optional[Issue]:
        i = await self.get(iid)
        if not i: return None
        i.status = IssueStatus.DONE
        i.commit_ref = sha
        i.closed_at = datetime.now(timezone.utc)
        i.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(i)
        return i

    async def frontier(self, pid: uuid.UUID) -> List[Issue]:
        all_i = await self.list(pid)
        done = {i.id for i in all_i if i.status == IssueStatus.DONE}
        f = [i for i in all_i if i.status != IssueStatus.DONE and all(uuid.UUID(x) in done for x in json.loads(i.blockers) if i.blockers)]
        return sorted(f, key=lambda i: (-i.priority, i.created_at))

    async def gen(self, pid: uuid.UUID) -> List[Issue]:
        p = await self.db.get(PRD, pid)
        if not p or not p.content: return []
        issues = []
        for line in p.content.split("\n"):
            if line.startswith("### US-"):
                t = line[4:].strip()
                issues.append(await self.create(pid, t, "", [], [], [], 0))
        return issues