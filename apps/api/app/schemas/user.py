"""User Schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str | None = Field(default=None, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a user record internally."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating user profile fields."""

    full_name: str | None = Field(default=None, description="Updated full name")
    is_active: bool | None = Field(default=None, description="Activate/deactivate account")


class UserRead(UserBase):
    """Public user profile response representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique user identifier")
    is_active: bool = Field(..., description="Whether user is active")
    is_superuser: bool = Field(..., description="Whether user is superadmin")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
