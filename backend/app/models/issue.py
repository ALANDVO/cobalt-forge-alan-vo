import enum
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import uuid

class IS(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    READY_FOR_REVIEW = "ready_for_review"
    DONE = "done"
    WONT_FIX = "wont_fix"

class IT(str, enum.Enum):
    LOCAL = "local"
    GITHUB = "github"
    GITLAB = "gitlab"

class Issue(Base):
    __tablename__ = "issues"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prd_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prds.id", ondelete="CASCADE"), nullable=False, index=True)
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    tracker_type: Mapped[IT] = mapped_column(SQLEnum(IT), default=IT.LOCAL, nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IS] = mapped_column(SQLEnum(IS), default=IS.OPEN, nullable=False)
    priority: Mapped[int] = mapped_column(default=0, nullable=False)
    acceptance_criteria: Mapped[str] = mapped_column(Text, default="", nullable=False)
    decision_refs: Mapped[str] = mapped_column(Text, default="", nullable=False)
    blockers: Mapped[str] = mapped_column(Text, default="", nullable=False)
    commit_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    prd: Mapped["PRD"] = relationship(back_populates="issues", lazy="selectin")
    assignee: Mapped["User | None"] = relationship(back_populates="issues", lazy="selectin")
    __table_args__ = (Index("ix_issue_prd_status", "prd_id", "status"),)