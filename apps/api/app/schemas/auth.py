"""Authentication API Schemas."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    """User registration payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Plaintext password (min 8 characters)")
    full_name: str | None = Field(default=None, description="User full name")


class LoginRequest(BaseModel):
    """User login credential payload."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """JWT bearer token response."""

    model_config = ConfigDict(from_attributes=True)

    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token validity duration in seconds")
