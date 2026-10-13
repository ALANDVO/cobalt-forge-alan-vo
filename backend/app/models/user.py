import enum
from sqlalchemy import String, DateTime, func, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from datetime import datetime
import uuid

class UR(str, enum.Enum):
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    keycloak_sub: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UR] = mapped_column(SQLEnum(UR), default=UR.VIEWER, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    sessions: Mapped[list["GrillingSession"]] = relationship(back_populates="owner", lazy="selectin")
    decisions: Mapped[list["DecisionRecord"]] = relationship(back_populates="author", lazy="selectin")
    prds: Mapped[list["PRD"]] = relationship(back_populates="author", lazy="selectin")
    issues: Mapped[list["Issue"]] = relationship(back_populates="assignee", lazy="selectin")