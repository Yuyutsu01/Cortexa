"""System Audit and Foundation Models.

Provides foundational metadata storage to verify database connectivity and Alembic migrations.
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemAudit(Base):
    """Foundational audit log table for system lifecycle and migration validation."""

    __tablename__ = "system_audits"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SystemAudit(id={self.id}, event_type='{self.event_type}', created_at='{self.created_at}')>"
