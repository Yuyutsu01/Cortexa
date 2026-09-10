"""JWT Authentication Utilities.

Handles creation, signing, and decoding of JSON Web Tokens.
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from fastapi import status

from app.core.config import get_settings
from app.core.exceptions import CortexaException


class AuthenticationError(CortexaException):
    """Raised when authentication credentials or tokens are invalid."""

    def __init__(self, message: str = "Invalid authentication credentials") -> None:
        super().__init__(
            message=message,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class PermissionDeniedError(CortexaException):
    """Raised when an authenticated user lacks required permissions."""

    def __init__(self, message: str = "You do not have permission to perform this action") -> None:
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


def create_access_token(
    subject: str | UUID,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Generate a signed JWT access token for a subject (user ID)."""
    settings = get_settings()
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return str(encoded_jwt)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify and decode a signed JWT access token."""
    if is_token_revoked(token):
        raise AuthenticationError("Authentication token has been revoked")

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return dict(payload)
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Authentication token has expired") from None
    except jwt.PyJWTError:
        raise AuthenticationError("Could not validate authentication token") from None


# In-memory revocation cache
_revoked_tokens: set[str] = set()


def revoke_token(token: str) -> None:
    """Add a JWT token to the revoked blacklist."""
    _revoked_tokens.add(token)


def is_token_revoked(token: str) -> bool:
    """Check whether a token has been revoked."""
    return token in _revoked_tokens
