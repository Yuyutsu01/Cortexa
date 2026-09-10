"""Organization Tenant Management Routes.

Provides endpoints for creating, listing, and modifying organization workspaces.
"""

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    TenantContext,
    get_client_ip,
    get_current_active_user,
    get_db,
    get_tenant_context,
    require_roles,
)
from app.domain.enums import UserRole
from app.models.user import User
from app.schemas.common import DataResponse
from app.schemas.organization import (
    OrgCreate,
    OrgRead,
    OrgUpdate,
    OrgWithMembershipRead,
)
from app.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.post(
    "",
    response_model=DataResponse[OrgRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization Workspace",
    description="Provisions a new organization and assigns the caller as OWNER.",
)
async def create_organization(
    request: OrgCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> DataResponse[OrgRead]:
    """Create a new organization workspace."""
    org_service = OrganizationService(session)
    org = await org_service.create_organization(
        creator_user_id=current_user.id,
        request=request,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return DataResponse(data=OrgRead.model_validate(org))


@router.get(
    "",
    response_model=DataResponse[list[OrgWithMembershipRead]],
    summary="List User Organizations",
    description="Returns all organizations the authenticated caller belongs to.",
)
async def list_user_organizations(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> DataResponse[list[OrgWithMembershipRead]]:
    """List organizations for the current user."""
    org_service = OrganizationService(session)
    orgs = await org_service.list_user_organizations(current_user.id)
    return DataResponse(data=orgs)


@router.get(
    "/{organization_id}",
    response_model=DataResponse[OrgRead],
    summary="Get Organization Details",
    description="Retrieves organization information. Caller must be an active member of the tenant.",
)
async def get_organization(
    tenant: TenantContext = Depends(get_tenant_context),
) -> DataResponse[OrgRead]:
    """Retrieve organization details."""
    return DataResponse(data=OrgRead.model_validate(tenant.organization))


@router.patch(
    "/{organization_id}",
    response_model=DataResponse[OrgRead],
    summary="Update Organization Settings",
    description="Modifies organization name or status. Requires ADMIN or OWNER role.",
)
async def update_organization(
    update_data: OrgUpdate,
    tenant: TenantContext = Depends(require_roles(UserRole.OWNER, UserRole.ADMIN)),
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
) -> DataResponse[OrgRead]:
    """Update organization settings."""
    org_service = OrganizationService(session)
    updated_org = await org_service.update_organization(
        org_id=tenant.organization_id,
        actor_id=tenant.current_user.id,
        update_data=update_data,
        ip_address=ip_address,
    )
    return DataResponse(data=OrgRead.model_validate(updated_org))
