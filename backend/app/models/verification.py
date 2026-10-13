import enum
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import uuid

class ET(str, enum.Enum):
    TEST_RESULT = "test_result"
    CODE_REVIEW = "code_review"
    MANUAL_VERIFICATION = "manual_verification"
    AUTOMATED_CHECK = "automated_check"
    COMMIT = "commit"

class VerificationEvidence(Base):
    __tablename__ = "verification_evidence"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    decision_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("decision_records.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("issues.id", ondelete="SET NULL"), nullable=True, index=True)
    evidence_type: Mapped[ET] = mapped_column(SQLEnum(ET), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    artifact_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    passed: Mapped[bool] = mapped_column(default=False, nullable=False)
    verified_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    decision: Mapped["DecisionRecord"] = relationship(back_populates="verification_evidence", lazy="selectin")
    __table_args__ = (Index("ix_verification_decision_type", "decision_id", "evidence_type"),)