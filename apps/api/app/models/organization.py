"""Organization Model.

Represents a multi-tenant workspace account within Cortexa.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import OrgStatus
from app.models.base import BaseEntity, SoftDeleteMixin

if TYPE_CHECKING:
    from app.models.audit import AuditLog
    from app.models.membership import Membership


class Organization(BaseEntity, SoftDeleteMixin):
    """Organization tenant entity."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[OrgStatus] = mapped_column(
        SQLEnum(OrgStatus, name="org_status_enum"),
        default=OrgStatus.ACTIVE,
        nullable=False,
    )

    # Relationships
    memberships: Mapped[list["Membership"]] = relationship(
        "Membership",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="organization",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', slug='{self.slug}')>"
