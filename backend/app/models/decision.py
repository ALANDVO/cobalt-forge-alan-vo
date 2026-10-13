import enum
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Enum as SQLEnum, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import uuid

class DS(str, enum.Enum):
    DRAFT = "draft"
    RESOLVED = "resolved"
    REVISED = "revised"
    SUPERSEDED = "superseded"

class DecisionRecord(Base):
    __tablename__ = "decision_records"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    stable_id: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_sessions.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_requirement: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tags: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    status: Mapped[DS] = mapped_column(SQLEnum(DS), default=DS.RESOLVED, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    session: Mapped["GrillingSession"] = relationship(back_populates="decisions", lazy="selectin")
    author: Mapped["User"] = relationship(back_populates="decisions", lazy="selectin")
    versions: Mapped[list["DecisionVersion"]] = relationship(back_populates="record", lazy="selectin", cascade="all, delete-orphan")
    prd_mappings: Mapped[list["PRDDecisionMapping"]] = relationship(back_populates="decision", lazy="selectin", cascade="all, delete-orphan")
    verification_evidence: Mapped[list["VerificationEvidence"]] = relationship(back_populates="decision", lazy="selectin", cascade="all, delete-orphan")

class DecisionVersion(Base):
    __tablename__ = "decision_versions"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    record_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("decision_records.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_requirement: Mapped[str] = mapped_column(Text, nullable=False)
    constraints: Mapped[str] = mapped_column(Text, default="", nullable=False)
    tags: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    status: Mapped[DS] = mapped_column(SQLEnum(DS), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    change_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    record: Mapped["DecisionRecord"] = relationship(back_populates="versions", lazy="selectin")