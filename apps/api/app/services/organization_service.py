"""Organization Service Module.

Coordinates tenant creation, ownership assignment, and workspace settings.
"""

from collections.abc import Sequence
from typing import Any
from uuid import UUID

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CortexaException
from app.domain.enums import AuditAction, OrgStatus, UserRole
from app.domain.events import OrganizationCreatedEvent, event_dispatcher
from app.models.membership import Membership
from app.models.organization import Organization
from app.repositories.membership_repository import MembershipRepository
from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrgCreate, OrgUpdate, OrgWithMembershipRead
from app.services.audit_service import AuditService
from app.services.base import BaseService


class SlugAlreadyExistsError(CortexaException):
    """Raised when organization slug is already in use."""

    def __init__(self, slug: str) -> None:
        super().__init__(
            message=f"Organization slug '{slug}' is already taken",
            code="ORG_SLUG_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
        )


class OrganizationNotFoundError(CortexaException):
    """Raised when organization is not found."""

    def __init__(self, org_id: UUID | str) -> None:
        super().__init__(
            message=f"Organization '{org_id}' was not found",
            code="ORGANIZATION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class OrganizationService(BaseService):
    """Application service for Organization tenant management."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.org_repo = OrganizationRepository(session)
        self.membership_repo = MembershipRepository(session)
        self.audit_service = AuditService(session)

    async def create_organization(
        self,
        creator_user_id: UUID,
        request: OrgCreate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Organization:
        """Create a new Organization workspace and atomically assign creator as OWNER."""
        slug_clean = request.slug.lower().strip()
        if await self.org_repo.slug_exists(slug_clean):
            raise SlugAlreadyExistsError(slug_clean)

        new_org = Organization(
            name=request.name.strip(),
            slug=slug_clean,
            status=OrgStatus.ACTIVE,
        )

        async with self.transaction():
            # 1. Create Organization
            org = await self.org_repo.create(new_org)

            # 2. Provision Creator as OWNER
            owner_membership = Membership(
                organization_id=org.id,
                user_id=creator_user_id,
                role=UserRole.OWNER,
                is_active=True,
            )
            await self.membership_repo.create(owner_membership)

            # 3. Record Audit Log
            await self.audit_service.log_event(
                action=AuditAction.ORG_CREATED,
                resource_type="organization",
                resource_id=str(org.id),
                organization_id=org.id,
                user_id=creator_user_id,
                changes={"name": org.name, "slug": org.slug},
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # Publish domain event
        await event_dispatcher.publish(
            OrganizationCreatedEvent(
                actor_id=creator_user_id,
                organization_id=org.id,
                name=org.name,
                slug=org.slug,
                owner_user_id=creator_user_id,
            )
        )
        return org

    async def get_by_id(self, org_id: UUID) -> Organization:
        """Retrieve an organization by its UUID."""
        org = await self.org_repo.get_by_id(org_id)
        if not org or org.is_deleted:
            raise OrganizationNotFoundError(org_id)
        return org

    async def list_user_organizations(self, user_id: UUID) -> list[OrgWithMembershipRead]:
        """List all organizations the user belongs to, including their active role."""
        results: Sequence[
            tuple[Organization, Membership]
        ] = await self.org_repo.list_user_organizations(user_id)
        return [
            OrgWithMembershipRead(
                id=org.id,
                name=org.name,
                slug=org.slug,
                status=org.status,
                created_at=org.created_at,
                updated_at=org.updated_at,
                current_user_role=membership.role,
            )
            for org, membership in results
        ]

    async def update_organization(
        self,
        org_id: UUID,
        actor_id: UUID,
        update_data: OrgUpdate,
        ip_address: str | None = None,
    ) -> Organization:
        """Update organization name or status."""
        org = await self.get_by_id(org_id)
        changes: dict[str, Any] = {}

        if update_data.name is not None and update_data.name.strip() != org.name:
            changes["name"] = {"old": org.name, "new": update_data.name.strip()}
            org.name = update_data.name.strip()

        if update_data.status is not None and update_data.status != org.status:
            changes["status"] = {"old": org.status.value, "new": update_data.status.value}
            org.status = update_data.status

        async with self.transaction():
            org = await self.org_repo.update(org)
            if changes:
                await self.audit_service.log_event(
                    action=AuditAction.ORG_UPDATED,
                    resource_type="organization",
                    resource_id=str(org.id),
                    organization_id=org.id,
                    user_id=actor_id,
                    changes=changes,
                    ip_address=ip_address,
                )

        return org
