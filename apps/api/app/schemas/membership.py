"""Membership Schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.enums import UserRole
from app.schemas.user import UserRead


class MemberCreate(BaseModel):
    """Payload for adding a user to an organization."""

    email: EmailStr = Field(..., description="Email address of user to add")
    role: UserRole = Field(default=UserRole.MEMBER, description="Assigned RBAC role")


class MemberUpdateRole(BaseModel):
    """Payload for updating a member's role."""

    role: UserRole = Field(..., description="New RBAC role")


class MemberRead(BaseModel):
    """Membership response representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Membership identifier")
    organization_id: UUID = Field(..., description="Organization identifier")
    user_id: UUID = Field(..., description="User identifier")
    role: UserRole = Field(..., description="Assigned role")
    is_active: bool = Field(..., description="Membership active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    user: UserRead | None = Field(default=None, description="Attached user profile")
