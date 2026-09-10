"""API Dependencies Module.

Provides authenticated user injection, database session binding, and strict tenant context resolution.
"""

from collections.abc import AsyncGenerator, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import Depends, Header, Path, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticationError, PermissionDeniedError, decode_access_token
from app.core.database import get_db_session
from app.domain.enums import UserRole
from app.models.organization import Organization
from app.models.user import User
from app.repositories.membership_repository import MembershipRepository
from app.repositories.organization_repository import OrganizationRepository
from app.services.user_service import UserService

# Bearer token extractor
security_scheme = HTTPBearer(auto_error=False)


@dataclass
class TenantContext:
    """Encapsulates validated tenant boundaries for a request."""

    organization: Organization
    current_user: User
    role: UserRole

    @property
    def organization_id(self) -> UUID:
        """Helper property to access organization UUID."""
        return self.organization.id

    @property
    def is_owner(self) -> bool:
        """Check if caller is an organization OWNER."""
        return self.role == UserRole.OWNER

    @property
    def is_admin_or_owner(self) -> bool:
        """Check if caller is an ADMIN or OWNER."""
        return self.role in (UserRole.OWNER, UserRole.ADMIN)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the authenticated user from the JWT Bearer token."""
    if not credentials or not credentials.credentials:
        raise AuthenticationError("Authorization header with Bearer token is required")

    payload = decode_access_token(credentials.credentials)
    sub = payload.get("sub")
    if not sub:
        raise AuthenticationError("Token payload missing subject identifier")

    try:
        user_uuid = UUID(str(sub))
    except ValueError:
        raise AuthenticationError("Invalid user identifier in token") from None

    user_service = UserService(session)
    try:
        return await user_service.get_by_id(user_uuid)
    except Exception:
        raise AuthenticationError("User associated with token does not exist") from None


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure that the authenticated user account is active."""
    if not current_user.is_active:
        raise AuthenticationError("User account has been deactivated")
    return current_user


async def get_tenant_context(
    organization_id: UUID = Path(..., description="Organization tenant identifier"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> TenantContext:
    """Verify that current user is an active member of the target Organization tenant.

    CRITICAL: This dependency guarantees tenant isolation before any tenant endpoint executes.
    """
    org_repo = OrganizationRepository(session)
    membership_repo = MembershipRepository(session)

    org = await org_repo.get_by_id(organization_id)
    if not org or org.is_deleted:
        raise PermissionDeniedError("Organization does not exist or has been deleted")

    membership = await membership_repo.get_membership(organization_id, current_user.id)
    if not membership or not membership.is_active:
        raise PermissionDeniedError("You do not have active membership in this organization")

    return TenantContext(
        organization=org,
        current_user=current_user,
        role=membership.role,
    )


def require_roles(*allowed_roles: UserRole) -> Callable[..., Any]:
    """Dependency factory restricting endpoint access to specific RBAC roles."""

    async def role_checker(
        tenant: TenantContext = Depends(get_tenant_context),
    ) -> TenantContext:
        if tenant.role not in allowed_roles:
            raise PermissionDeniedError(
                f"Action requires one of the following roles: {', '.join(r.value for r in allowed_roles)}"
            )
        return tenant

    return role_checker


def get_client_ip(
    request: Request,
    x_forwarded_for: str | None = Header(default=None, alias="X-Forwarded-For"),
) -> str | None:
    """Helper to safely extract client IP for audit logging."""
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None
