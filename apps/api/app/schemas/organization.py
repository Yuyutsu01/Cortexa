"""Organization Schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import OrgStatus, UserRole


class OrgBase(BaseModel):
    """Base organization fields."""

    name: str = Field(..., min_length=2, max_length=150, description="Organization workspace name")
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly unique identifier (lowercase, numbers, dashes)",
    )


class OrgCreate(OrgBase):
    """Payload for creating a new Organization."""

    pass


class OrgUpdate(BaseModel):
    """Payload for updating Organization settings."""

    name: str | None = Field(default=None, min_length=2, max_length=150)
    status: OrgStatus | None = Field(default=None)


class OrgRead(OrgBase):
    """Public organization response representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Unique organization identifier")
    status: OrgStatus = Field(..., description="Organization status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class OrgWithMembershipRead(OrgRead):
    """Organization with caller's membership role attached."""

    current_user_role: UserRole = Field(
        ..., description="Role of the authenticated caller in this org"
    )
