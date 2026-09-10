"""Authentication and Identity Routes.

Provides endpoints for user registration, credential authentication, and profile retrieval.
"""

from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_active_user, get_db
from app.core.auth import create_access_token
from app.core.config import get_settings
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.common import DataResponse
from app.schemas.user import UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=DataResponse[UserRead],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User Account",
    description="Creates a new user profile with secure password hashing.",
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> DataResponse[UserRead]:
    """Register a new user account."""
    user_service = UserService(session)
    user = await user_service.register_user(
        request=request,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    return DataResponse(data=UserRead.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate User Credentials",
    description="Authenticates email and password, returning a signed JWT access token.",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> TokenResponse:
    """Authenticate and obtain JWT bearer token."""
    user_service = UserService(session)
    user = await user_service.authenticate(
        request=request,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    settings = get_settings()
    access_token = create_access_token(
        subject=user.id,
        extra_claims={"email": user.email},
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=DataResponse[UserRead],
    summary="Get Authenticated User Profile",
    description="Returns the profile details of the authenticated caller.",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> DataResponse[UserRead]:
    """Retrieve current authenticated user profile."""
    return DataResponse(data=UserRead.model_validate(current_user))


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout and Invalidate Session",
    description="Revokes the active JWT access token and logs an audit record.",
)
async def logout(
    current_user: User = Depends(get_current_active_user),
    credentials: str | None = Header(default=None, alias="Authorization"),
    session: AsyncSession = Depends(get_db),
    ip_address: str | None = Depends(get_client_ip),
    user_agent: str | None = Header(default=None, alias="User-Agent"),
) -> dict[str, str]:
    """Logout current user and invalidate the session token."""
    if credentials and credentials.startswith("Bearer "):
        token = credentials[7:].strip()
        from app.core.auth import revoke_token

        revoke_token(token)

    from app.domain.enums import AuditAction
    from app.services.audit_service import AuditService

    audit_service = AuditService(session)
    await audit_service.log_event(
        action=AuditAction.USER_LOGOUT,
        resource_type="user",
        resource_id=str(current_user.id),
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await session.commit()
    return {"message": "Successfully logged out"}
