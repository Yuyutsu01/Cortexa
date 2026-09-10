"""Audit Service Module.

Coordinates recording and retrieval of audit events.
"""

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.audit_repository import AuditLogRepository
from app.schemas.common import PaginationParams, SortParams
from app.services.base import BaseService


class AuditService(BaseService):
    """Application service for domain audit operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.audit_repo = AuditLogRepository(session)

    async def log_event(
        self,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        organization_id: UUID | None = None,
        user_id: UUID | None = None,
        changes: dict[str, Any] | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """Record an audit trail event."""
        return await self.audit_repo.log_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            organization_id=organization_id,
            user_id=user_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def list_organization_audit_logs(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        sort: SortParams | None = None,
    ) -> tuple[Sequence[AuditLog], int]:
        """List audit records for a tenant organization."""
        return await self.audit_repo.list_by_organization(
            organization_id=organization_id,
            pagination=pagination,
            sort=sort,
        )
