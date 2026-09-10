"""Audit Log Schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditLogRead(BaseModel):
    """Audit log entry response representation."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Audit record identifier")
    organization_id: UUID | None = Field(default=None, description="Organization context")
    user_id: UUID | None = Field(default=None, description="Acting user identifier")
    action: str = Field(..., description="Domain action name")
    resource_type: str = Field(..., description="Target resource type")
    resource_id: str | None = Field(default=None, description="Target resource identifier")
    changes: dict[str, Any] | None = Field(default=None, description="Delta changes payload")
    ip_address: str | None = Field(default=None, description="Client IP address")
    user_agent: str | None = Field(default=None, description="Client user agent")
    created_at: datetime = Field(..., description="Timestamp of event")
