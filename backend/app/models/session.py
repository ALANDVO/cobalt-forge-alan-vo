import enum
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Enum as SQLEnum, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import uuid

class SS(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class QT(str, enum.Enum):
    PIVOT = "pivot"
    DETAIL = "detail"

class QS(str, enum.Enum):
    PENDING = "pending"
    ANSWERED = "answered"
    DEFERRED = "deferred"

class GrillingSession(Base):
    __tablename__ = "grilling_sessions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[SS] = mapped_column(SQLEnum(SS), default=SS.ACTIVE, nullable=False)
    current_round: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    question_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assumption_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    design_tree: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    owner: Mapped["User"] = relationship(back_populates="sessions", lazy="selectin")
    rounds: Mapped[list["GrillingRound"]] = relationship(back_populates="session", lazy="selectin", cascade="all, delete-orphan", order_by="GrillingRound.round_number")
    decisions: Mapped[list["DecisionRecord"]] = relationship(back_populates="session", lazy="selectin", cascade="all, delete-orphan")

class GrillingRound(Base):
    __tablename__ = "grilling_rounds"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    frontier_questions: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    pivot_order: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session: Mapped["GrillingSession"] = relationship(back_populates="rounds", lazy="selectin")
    questions: Mapped[list["GrillingQuestion"]] = relationship(back_populates="round", lazy="selectin", cascade="all, delete-orphan")
    assumptions: Mapped[list["GrillingAssumption"]] = relationship(back_populates="round", lazy="selectin", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_round_session_number", "session_id", "round_number", unique=True),)

class GrillingQuestion(Base):
    __tablename__ = "grilling_questions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_rounds.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_sessions.id"), nullable=False, index=True)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    detailed_explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    question_type: Mapped[QT] = mapped_column(SQLEnum(QT), default=QT.DETAIL, nullable=False)
    prerequisites: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    options: Mapped[str] = mapped_column(Text, default="[]", nullable=False)
    recommended_option: Mapped[str] = mapped_column(String(10), default="", nullable=False)
    recommended_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[QS] = mapped_column(SQLEnum(QS), default=QS.PENDING, nullable=False)
    answer: Mapped[str] = mapped_column(Text, default="", nullable=False)
    decision_record_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("decision_records.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    round: Mapped["GrillingRound"] = relationship(back_populates="questions", lazy="selectin")
    decision_record: Mapped["DecisionRecord | None"] = relationship(lazy="selectin")
    __table_args__ = (Index("ix_question_session_number", "session_id", "question_number", unique=True),)

class GrillingAssumption(Base):
    __tablename__ = "grilling_assumptions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    round_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_rounds.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_sessions.id"), nullable=False, index=True)
    assumption_number: Mapped[int] = mapped_column(Integer, nullable=False)
    assumption_text: Mapped[str] = mapped_column(Text, nullable=False)
    vetoed: Mapped[bool] = mapped_column(default=False, nullable=False)
    vetoed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    round: Mapped["GrillingRound"] = relationship(back_populates="assumptions", lazy="selectin")
    __table_args__ = (Index("ix_assumption_session_number", "session_id", "assumption_number", unique=True),)