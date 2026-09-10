"""User Service Module.

Coordinates user registration, credential authentication, and profile updates.
"""

from typing import Any
from uuid import UUID

from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CortexaException
from app.core.security import hash_password, verify_password
from app.domain.enums import AuditAction
from app.domain.events import UserCreatedEvent, event_dispatcher
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserUpdate
from app.services.audit_service import AuditService
from app.services.base import BaseService


class UserAlreadyExistsError(CortexaException):
    """Raised when registering with an existing email."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"A user with email '{email}' is already registered",
            code="USER_ALREADY_EXISTS",
            status_code=status.HTTP_409_CONFLICT,
        )


class UserNotFoundError(CortexaException):
    """Raised when user account is not found."""

    def __init__(self, user_id: UUID | str) -> None:
        super().__init__(
            message=f"User '{user_id}' was not found",
            code="USER_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InvalidCredentialsError(CortexaException):
    """Raised when email or password authentication fails."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UserService(BaseService):
    """Application service for User domain logic."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.user_repo = UserRepository(session)
        self.audit_service = AuditService(session)

    async def register_user(
        self,
        request: RegisterRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        """Register a new user account with hashed credentials."""
        email_clean = request.email.lower().strip()
        if await self.user_repo.email_exists(email_clean):
            raise UserAlreadyExistsError(email_clean)

        hashed = hash_password(request.password)
        new_user = User(
            email=email_clean,
            hashed_password=hashed,
            full_name=request.full_name,
            is_active=True,
            is_superuser=False,
        )

        async with self.transaction():
            user = await self.user_repo.create(new_user)
            await self.audit_service.log_event(
                action=AuditAction.USER_REGISTERED,
                resource_type="user",
                resource_id=str(user.id),
                user_id=user.id,
                changes={"email": user.email, "full_name": user.full_name},
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # Publish domain event
        await event_dispatcher.publish(
            UserCreatedEvent(
                actor_id=user.id,
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
            )
        )
        return user

    async def authenticate(
        self,
        request: LoginRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> User:
        """Verify user credentials and log authentication audit."""
        email_clean = request.email.lower().strip()
        user = await self.user_repo.get_by_email(email_clean)
        if not user or not user.is_active:
            raise InvalidCredentialsError()

        if not verify_password(request.password, user.hashed_password):
            raise InvalidCredentialsError()

        # Record login audit event
        await self.audit_service.log_event(
            action=AuditAction.USER_LOGIN,
            resource_type="user",
            resource_id=str(user.id),
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.commit()

        return user

    async def get_by_id(self, user_id: UUID) -> User:
        """Retrieve user by UUID or raise UserNotFoundError."""
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.is_active:
            raise UserNotFoundError(user_id)
        return user

    async def update_profile(
        self,
        user_id: UUID,
        update_data: UserUpdate,
        ip_address: str | None = None,
    ) -> User:
        """Update user profile attributes."""
        user = await self.get_by_id(user_id)
        changes: dict[str, Any] = {}

        if update_data.full_name is not None:
            changes["full_name"] = {"old": user.full_name, "new": update_data.full_name}
            user.full_name = update_data.full_name

        if update_data.is_active is not None:
            changes["is_active"] = {"old": user.is_active, "new": update_data.is_active}
            user.is_active = update_data.is_active

        async with self.transaction():
            user = await self.user_repo.update(user)
            if changes:
                await self.audit_service.log_event(
                    action=AuditAction.USER_UPDATED,
                    resource_type="user",
                    resource_id=str(user.id),
                    user_id=user.id,
                    changes=changes,
                    ip_address=ip_address,
                )

        return user
