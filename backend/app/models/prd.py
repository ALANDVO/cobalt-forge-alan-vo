import enum
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import uuid

class PS(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    ARCHIVED = "archived"

class PRD(Base):
    __tablename__ = "prds"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("grilling_sessions.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PS] = mapped_column(SQLEnum(PS), default=PS.DRAFT, nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    decision_coverage: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    session: Mapped["GrillingSession"] = relationship(lazy="selectin")
    author: Mapped["User"] = relationship(back_populates="prds", lazy="selectin")
    mappings: Mapped[list["PRDDecisionMapping"]] = relationship(back_populates="prd", lazy="selectin", cascade="all, delete-orphan")
    issues: Mapped[list["Issue"]] = relationship(back_populates="prd", lazy="selectin", cascade="all, delete-orphan")

class PRDDecisionMapping(Base):
    __tablename__ = "prd_decision_mappings"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prd_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prds.id", ondelete="CASCADE"), nullable=False, index=True)
    decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("decision_records.id", ondelete="CASCADE"), nullable=False, index=True)
    user_story_refs: Mapped[str] = mapped_column(Text, default="", nullable=False)
    constraint_refs: Mapped[str] = mapped_column(Text, default="", nullable=False)
    acceptance_criteria_refs: Mapped[str] = mapped_column(Text, default="", nullable=False)
    coverage_status: Mapped[str] = mapped_column(String(20), default="covered", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    prd: Mapped["PRD"] = relationship(back_populates="mappings", lazy="selectin")
    decision: Mapped["DecisionRecord"] = relationship(back_populates="prd_mappings", lazy="selectin")
    __table_args__ = (Index("ix_prd_decision_mapping", "prd_id", "decision_id", unique=True),)