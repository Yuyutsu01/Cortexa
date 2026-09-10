"""Unit Tests for Password Hashing and JWT Token Management."""

from datetime import timedelta
from uuid import uuid4

import pytest

from app.core.auth import AuthenticationError, create_access_token, decode_access_token
from app.core.security import hash_password, verify_password


def test_password_hashing_and_verification() -> None:
    """Verify that password hashing is secure and verifies correctly."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123!", hashed) is False


def test_jwt_token_generation_and_decoding() -> None:
    """Verify JWT access token creation and payload extraction."""
    user_id = uuid4()
    token = create_access_token(
        subject=user_id,
        extra_claims={"email": "developer@cortexa.ai"},
    )
    assert token is not None

    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == "developer@cortexa.ai"
    assert "exp" in payload


def test_expired_jwt_token_raises_error() -> None:
    """Verify that an expired token raises an AuthenticationError."""
    user_id = uuid4()
    # Create token expired 1 minute ago
    expired_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(seconds=-60),
    )

    with pytest.raises(AuthenticationError) as exc_info:
        decode_access_token(expired_token)
    assert "expired" in str(exc_info.value.message).lower()
