"""Membership Service Module.

Coordinates tenant member invitations, role mutations, and access revocation.
"""

from collections.abc import Sequence
from uuid import UUID

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CortexaException
from app.domain.enums import AuditAction, UserRole
from app.domain.events import (
    MembershipCreatedEvent,
    MembershipRemovedEvent,
    MembershipRoleUpdatedEvent,
    event_dispatcher,
)
from app.models.membership import Membership
from app.repositories.membership_repository import MembershipRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginationParams, SortParams
from app.schemas.membership import MemberCreate
from app.services.audit_service import AuditService
from app.services.base import BaseService


class MemberAlreadyExistsError(CortexaException):
    """Raised when user is already a member of the organization."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"User '{email}' is already a member of this organization",
            code="MEMBER_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
        )


class MembershipNotFoundError(CortexaException):
    """Raised when membership does not exist."""

    def __init__(self, user_id: UUID | str) -> None:
        super().__init__(
            message=f"Membership for user '{user_id}' was not found in this organization",
            code="MEMBERSHIP_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class LastOwnerConstraintError(CortexaException):
    """Raised when attempting to delete or demote the last remaining OWNER of an organization."""

    def __init__(self) -> None:
        super().__init__(
            message="Cannot remove or demote the last remaining OWNER of the organization",
            code="LAST_OWNER_CANNOT_BE_REMOVED",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class MembershipService(BaseService):
    """Application service for Membership and RBAC management."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.membership_repo = MembershipRepository(session)
        self.user_repo = UserRepository(session)
        self.audit_service = AuditService(session)

    async def add_member(
        self,
        organization_id: UUID,
        actor_id: UUID,
        request: MemberCreate,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> Membership:
        """Add an existing user to an organization with an assigned role."""
        email_clean = request.email.lower().strip()
        target_user = await self.user_repo.get_by_email(email_clean)
        if not target_user:
            raise CortexaException(
                message=f"User with email '{email_clean}' not found. The user must register before being added.",
                code="USER_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        existing_membership = await self.membership_repo.get_membership(
            organization_id, target_user.id
        )
        if existing_membership and existing_membership.is_active:
            raise MemberAlreadyExistsError(email_clean)

        async with self.transaction():
            if existing_membership:
                existing_membership.is_active = True
                existing_membership.role = request.role
                membership = await self.membership_repo.update(existing_membership)
            else:
                new_membership = Membership(
                    organization_id=organization_id,
                    user_id=target_user.id,
                    role=request.role,
                    is_active=True,
                )
                membership = await self.membership_repo.create(new_membership)

            await self.audit_service.log_event(
                action=AuditAction.MEMBER_ADDED,
                resource_type="membership",
                resource_id=str(membership.id),
                organization_id=organization_id,
                user_id=actor_id,
                changes={"target_user_id": str(target_user.id), "role": request.role.value},
                ip_address=ip_address,
                user_agent=user_agent,
            )

        await event_dispatcher.publish(
            MembershipCreatedEvent(
                actor_id=actor_id,
                organization_id=organization_id,
                membership_id=membership.id,
                user_id=target_user.id,
                role=membership.role,
            )
        )
        # Reload with user relation
        reloaded = await self.membership_repo.get_membership(organization_id, target_user.id)
        return reloaded or membership

    async def list_members(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        sort: SortParams | None = None,
    ) -> tuple[Sequence[Membership], int]:
        """List all members of an organization with pagination."""
        return await self.membership_repo.list_by_organization(
            organization_id=organization_id,
            pagination=pagination,
            sort=sort,
        )

    async def update_member_role(
        self,
        organization_id: UUID,
        target_user_id: UUID,
        actor_id: UUID,
        new_role: UserRole,
        ip_address: str | None = None,
    ) -> Membership:
        """Update a member's RBAC role, preventing demotion of the last owner."""
        membership = await self.membership_repo.get_membership(organization_id, target_user_id)
        if not membership:
            raise MembershipNotFoundError(target_user_id)

        if membership.role == UserRole.OWNER and new_role != UserRole.OWNER:
            owner_count = await self.membership_repo.count_owners(organization_id)
            if owner_count <= 1:
                raise LastOwnerConstraintError()

        old_role = membership.role
        membership.role = new_role

        async with self.transaction():
            membership = await self.membership_repo.update(membership)
            await self.audit_service.log_event(
                action=AuditAction.MEMBER_ROLE_CHANGED,
                resource_type="membership",
                resource_id=str(membership.id),
                organization_id=organization_id,
                user_id=actor_id,
                changes={
                    "target_user_id": str(target_user_id),
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                },
                ip_address=ip_address,
            )

        await event_dispatcher.publish(
            MembershipRoleUpdatedEvent(
                actor_id=actor_id,
                organization_id=organization_id,
                membership_id=membership.id,
                user_id=target_user_id,
                old_role=old_role,
                new_role=new_role,
            )
        )
        return membership

    async def remove_member(
        self,
        organization_id: UUID,
        target_user_id: UUID,
        actor_id: UUID,
        ip_address: str | None = None,
    ) -> None:
        """Revoke a member's access from an organization."""
        membership = await self.membership_repo.get_membership(organization_id, target_user_id)
        if not membership:
            raise MembershipNotFoundError(target_user_id)

        if membership.role == UserRole.OWNER:
            owner_count = await self.membership_repo.count_owners(organization_id)
            if owner_count <= 1:
                raise LastOwnerConstraintError()

        async with self.transaction():
            await self.membership_repo.delete(membership)
            await self.audit_service.log_event(
                action=AuditAction.MEMBER_REMOVED,
                resource_type="membership",
                resource_id=str(membership.id),
                organization_id=organization_id,
                user_id=actor_id,
                changes={"target_user_id": str(target_user_id)},
                ip_address=ip_address,
            )

        await event_dispatcher.publish(
            MembershipRemovedEvent(
                actor_id=actor_id,
                organization_id=organization_id,
                membership_id=membership.id,
                user_id=target_user_id,
            )
        )
