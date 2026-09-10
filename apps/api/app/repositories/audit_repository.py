"""Audit Log Repository Module."""

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository
from app.schemas.common import PaginationParams, SortParams


class AuditLogRepository(BaseRepository[AuditLog]):
    """Data access repository for AuditLog records."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(AuditLog, session)

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
        """Create and persist a new audit trail record."""
        audit_entry = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            organization_id=organization_id,
            user_id=user_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.create(audit_entry)

    async def list_by_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        sort: SortParams | None = None,
    ) -> tuple[Sequence[AuditLog], int]:
        """List audit events specifically belonging to an organization."""
        base_query = select(AuditLog).where(AuditLog.organization_id == organization_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        paginated_query = self._apply_sorting(base_query, sort)
        paginated_query = paginated_query.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(paginated_query)
        return result.scalars().all(), total_count
