import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models import User, UserRole, GrillingSession, SessionStatus, DecisionRecord, DecisionStatus, QuestionType, DecisionVersion
from app.services.decision_service import DecisionService
from app.services.grilling_service import GrillingService
import uuid


# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestAsyncSessionMaker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestAsyncSessionMaker() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db_session():
    async with TestAsyncSessionMaker() as session:
        yield session


@pytest.fixture
async def demo_user(db_session: AsyncSession) -> User:
    user = User(
        keycloak_sub="test-user",
        email="test@cobaltforge.local",
        name="Test User",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def active_session(db_session: AsyncSession, demo_user: User) -> GrillingSession:
    session = GrillingSession(
        owner_id=demo_user.id,
        title="Test Session",
        description="Test Description",
        status=SessionStatus.ACTIVE,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


class TestHealthEndpoint:
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestSessionManagement:
    async def test_create_session(self, client: AsyncClient, demo_user: User):
        response = await client.post(
            "/api/v1/sessions",
            json={"title": "New Session", "description": "Test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Session"
        assert data["status"] == "active"

    async def test_list_sessions(self, client: AsyncClient, demo_user: User):
        # Create a session via API
        await client.post("/api/v1/sessions", json={"title": "Test Session", "description": "Test"})
        response = await client.get("/api/v1/sessions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(s["title"] == "Test Session" for s in data)

    async def test_get_session(self, client: AsyncClient, demo_user: User, active_session: GrillingSession):
        response = await client.get(f"/api/v1/sessions/{active_session.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(active_session.id)

    async def test_start_round(self, client: AsyncClient, demo_user: User, active_session: GrillingSession):
        response = await client.post(f"/api/v1/sessions/{active_session.id}/rounds")
        assert response.status_code == 200
        data = response.json()
        assert data["round_number"] == 1


class TestGrillingWorkflow:
    async def test_add_question(self, client: AsyncClient, demo_user: User):
        # Create session via API
        session_resp = await client.post("/api/v1/sessions", json={"title": "Test", "description": "Test"})
        session_id = session_resp.json()["id"]

        # Start round
        round_resp = await client.post(f"/api/v1/sessions/{session_id}/rounds")
        round_id = round_resp.json()["id"]

        # Add question
        response = await client.post(
            f"/api/v1/sessions/rounds/{round_id}/questions",
            json={
                "question_text": "What database should we use?",
                "detailed_explanation": "Need to choose between PostgreSQL and SQLite",
                "question_type": "pivot",
                "prerequisites": [],
                "options": [
                    {"label": "A", "text": "PostgreSQL"},
                    {"label": "B", "text": "SQLite"},
                ],
                "recommended_option": "B",
                "recommended_reason": "Simpler for development",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["question_text"] == "What database should we use?"
        assert data["question_type"] == "pivot"

    async def test_add_assumption(self, client: AsyncClient, demo_user: User):
        session_resp = await client.post("/api/v1/sessions", json={"title": "Test", "description": "Test"})
        session_id = session_resp.json()["id"]

        round_resp = await client.post(f"/api/v1/sessions/{session_id}/rounds")
        round_id = round_resp.json()["id"]

        response = await client.post(
            f"/api/v1/sessions/rounds/{round_id}/assumptions",
            json={"assumption_text": "User prefers simplicity over features"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["assumption_text"] == "User prefers simplicity over features"

    async def test_answer_question_creates_decision(self, client: AsyncClient, demo_user: User):
        session_resp = await client.post("/api/v1/sessions", json={"title": "Test", "description": "Test"})
        session_id = session_resp.json()["id"]

        round_resp = await client.post(f"/api/v1/sessions/{session_id}/rounds")
        round_id = round_resp.json()["id"]

        q_resp = await client.post(
            f"/api/v1/sessions/rounds/{round_id}/questions",
            json={
                "question_text": "What database should we use?",
                "question_type": "pivot",
                "options": [{"label": "A", "text": "PostgreSQL"}, {"label": "B", "text": "SQLite"}],
                "recommended_option": "B",
            },
        )
        question_id = q_resp.json()["id"]

        response = await client.post(
            f"/api/v1/sessions/questions/{question_id}/answer",
            json={"answer": "We will use SQLite for development"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "answered"
        assert data["answer"] == "We will use SQLite for development"
        assert data["decision_record_id"] is not None

class TestDecisionService:
    async def test_create_decision(self, db_session: AsyncSession, demo_user: User, active_session: GrillingSession):
        service = DecisionService(db_session)
        decision = await service.create(
            sid=active_session.id,
            aid=demo_user.id,
            q="Test question?",
            a="Test answer",
            nr="System must do X",
            c="Must be fast; Must be secure",
            t="database,performance",
        )
        assert decision.stable_id == "DEC-001"
        assert decision.question == "Test question?"
        assert decision.status == DecisionStatus.RESOLVED

    async def test_list_decisions(self, db_session: AsyncSession, demo_user: User, active_session: GrillingSession):
        service = DecisionService(db_session)
        await service.create(sid=active_session.id, aid=demo_user.id, q="Q1", a="A1", nr="R1")
        await service.create(sid=active_session.id, aid=demo_user.id, q="Q2", a="A2", nr="R2")

        decisions = await service.list(active_session.id)
        assert len(decisions) == 2

    async def test_coverage_report(self, db_session: AsyncSession, demo_user: User, active_session: GrillingSession):
        service = DecisionService(db_session)
        await service.create(sid=active_session.id, aid=demo_user.id, q="Q1", a="A1", nr="R1", st=DecisionStatus.RESOLVED)
        await service.create(sid=active_session.id, aid=demo_user.id, q="Q2", a="A2", nr="R2", st=DecisionStatus.DRAFT)

        report = await service.coverage(active_session.id)
        assert report["total"] == 2
        assert report["resolved"] == 1
        assert report["draft"] == 1
        assert report["coverage_percentage"] == 50.0

class TestGrillingService:
    async def test_compute_frontier(self, db_session: AsyncSession, demo_user: User, active_session: GrillingSession):
        service = GrillingService(db_session)

        # Start round
        round_obj = await service.start_round(active_session.id)

        # Add questions with prerequisites
        q1 = await service.add_question(
            rid=round_obj.id,
            qt="Q1: Root decision?",
            qty=QuestionType.PIVOT,
            pre=[],
        )
        q2 = await service.add_question(
            rid=round_obj.id,
            qt="Q2: Depends on Q1?",
            qty=QuestionType.DETAIL,
            pre=[1],
        )
        q3 = await service.add_question(
            rid=round_obj.id,
            qt="Q3: Independent?",
            qty=QuestionType.DETAIL,
            pre=[],
        )

        # Answer Q1
        await service.answer_question(q1.id, "Answer to Q1", demo_user.id)

        # Compute frontier
        session = await service.get_session(active_session.id)
        frontier = service.compute_frontier(session)

        # Q2 and Q3 should be in frontier (Q1 is answered)
        frontier_numbers = {q.question_number for q in frontier}
        assert 2 in frontier_numbers  # Q2
        assert 3 in frontier_numbers  # Q3
        assert 1 not in frontier_numbers  # Q1 answered

    async def test_pivot_ordering(self, db_session: AsyncSession, demo_user: User, active_session: GrillingSession):
        service = GrillingService(db_session)
        round_obj = await service.start_round(active_session.id)

        # Add detail question first, then pivot
        q1 = await service.add_question(
            rid=round_obj.id,
            qt="Detail question",
            qty=QuestionType.DETAIL,
            pre=[],
        )
        q2 = await service.add_question(
            rid=round_obj.id,
            qt="Pivot question",
            qty=QuestionType.PIVOT,
            pre=[],
        )

        session = await service.get_session(active_session.id)
        frontier = service.compute_frontier(session)

        # Pivot should come first
        assert frontier[0].question_number == 2  # Pivot
        assert frontier[1].question_number == 1  # Detail


class TestDecisionVersioning:
    async def test_decision_version_on_update(self, db_session: AsyncSession, demo_user: User, active_session: GrillingSession):
        service = DecisionService(db_session)
        decision = await service.create(
            sid=active_session.id,
            aid=demo_user.id,
            q="Original question",
            a="Original answer",
            nr="Original requirement",
        )

        # Update decision
        updated = await service.update(
            did=decision.id,
            aid=demo_user.id,
            a="Updated answer",
            r="Changed based on feedback",
        )

        assert updated.version == 2
        assert updated.answer == "Updated answer"

        # Check version history
        result = await db_session.execute(
            select(DecisionVersion).where(DecisionVersion.record_id == decision.id)
        )
        versions = result.scalars().all()
        assert len(versions) == 2  # Original + update
        assert versions[0].version == 1
        assert versions[1].version == 1  # Archived version 1