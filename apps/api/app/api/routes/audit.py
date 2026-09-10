"""Tenant Audit Trail Routes.

Provides endpoints for querying immutable audit records within an organization.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    TenantContext,
    get_db,
    require_roles,
)
from app.domain.enums import UserRole
from app.schemas.audit import AuditLogRead
from app.schemas.common import PaginatedResponse, PaginationMeta, PaginationParams, SortParams
from app.services.audit_service import AuditService

router = APIRouter(
    prefix="/organizations/{organization_id}/audit-logs",
    tags=["Audit Trail"],
)


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogRead],
    summary="Query Organization Audit Trail",
    description="Returns a paginated list of audit events for the organization. Requires ADMIN or OWNER role.",
)
async def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    tenant: TenantContext = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AuditLogRead]:
    """List tenant audit trail logs."""
    pagination = PaginationParams(page=page, page_size=page_size)
    sort = SortParams(sort_by=sort_by, order=order)

    audit_service = AuditService(session)
    logs, total_items = await audit_service.list_organization_audit_logs(
        organization_id=tenant.organization_id,
        pagination=pagination,
        sort=sort,
    )

    data = [AuditLogRead.model_validate(log) for log in logs]
    meta = PaginationMeta.create(page=page, page_size=page_size, total_items=total_items)
    return PaginatedResponse(data=data, pagination=meta)
