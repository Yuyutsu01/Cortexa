"""Tenant Membership and RBAC Routes.

Provides endpoints for inviting members, modifying roles, and revoking organization access.
"""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    TenantContext,
    get_client_ip,
    get_db,
    get_tenant_context,
    require_roles,
)
from app.domain.enums import UserRole
from app.schemas.common import (
    DataResponse,
    PaginatedResponse,
    PaginationMeta,
    PaginationParams,
    SortParams,
)
from app.schemas.membership import MemberCreate, MemberRead, MemberUpdateRole
from app.services.membership_service import MembershipService

router = APIRouter(
    prefix="/organizations/{organization_id}/members",
    tags=["Organization Memberships"],
)


@router.get(
    "",
    response_model=PaginatedResponse[MemberRead],
    summary="List Organization Members",
    description="Returns a paginated list of all members within the organization.",
)
async def list_members(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    order: Literal["asc", "desc"] = Query(default="desc"),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db),
) -> PaginatedResponse[MemberRead]:
    """List members in the organization."""
    pagination = PaginationParams(page=page, page_size=page_size)
    sort = SortParams(sort_by=sort_by, order=order)

    membership_service = MembershipService(session)
    members, total_items = await membership_service.list_members(
        organization_id=tenant.organization_id,
        pagination=pagination,
        sort=sort,
    )

    data = [MemberRead.model_validate(m) for m in members]
    meta = PaginationMeta.create(page=page, page_size=page_size, total_items=total_items)
    return PaginatedResponse(data=data, pagination=meta)


@router.post(
    "",
    response_model=DataResponse[MemberRead],
    status_code=status.HTTP_201_CREATED,
    summary="Add Member to Organization",
    description="Adds an existing user to the organization with an assigned role. Requires ADMIN or OWNER role.",
)
async def add_member(
    request: MemberCreate,
    tenant: TenantContext = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> DataResponse[MemberRead]:
    """Add user to organization."""
    membership_service = MembershipService(session)
    membership = await membership_service.add_member(
        organization_id=tenant.organization_id,
        actor_id=tenant.current_user.id,
        request=request,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return DataResponse(data=MemberRead.model_validate(membership))


@router.patch(
    "/{user_id}/role",
    response_model=DataResponse[MemberRead],
    summary="Update Member Role",
    description="Modifies a member's RBAC role within the organization. Requires OWNER or ADMIN role.",
)
async def update_member_role(
    role_update: MemberUpdateRole,
    user_id: UUID = Path(..., description="Target user identifier"),
    tenant: TenantContext = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
) -> DataResponse[MemberRead]:
    """Update member's role."""
    membership_service = MembershipService(session)
    updated_membership = await membership_service.update_member_role(
        organization_id=tenant.organization_id,
        target_user_id=user_id,
        actor_id=tenant.current_user.id,
        new_role=role_update.role,
        ip_address=ip_address,
    )
    return DataResponse(data=MemberRead.model_validate(updated_membership))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Member from Organization",
    description="Revokes a user's membership and access to the organization. Requires OWNER or ADMIN role (or self).",
)
async def remove_member(
    user_id: UUID = Path(..., description="Target user identifier"),
    tenant: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
) -> None:
    """Remove member from organization."""
    # Allow self-removal or require ADMIN/OWNER for removing others
    if tenant.current_user.id != user_id and not tenant.is_admin_or_owner:
        from app.core.auth import PermissionDeniedError

        raise PermissionDeniedError("Only ADMIN or OWNER can remove other members")

    membership_service = MembershipService(session)
    await membership_service.remove_member(
        organization_id=tenant.organization_id,
        target_user_id=user_id,
        actor_id=tenant.current_user.id,
        ip_address=ip_address,
    )
