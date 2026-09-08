"""Health and Readiness Data Schemas.

Defines Pydantic response models for liveness and readiness probes.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe response model."""

    status: Literal["ok", "degraded", "unhealthy"] = Field(
        ..., description="Overall system health status"
    )
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Running environment")
    timestamp: datetime = Field(..., description="Current UTC timestamp")


class ComponentHealth(BaseModel):
    """Detailed status of a specific infrastructure dependency."""

    status: Literal["healthy", "unhealthy"] = Field(..., description="Status of the dependency")
    message: str = Field(..., description="Diagnostic detail or error message")


class ReadinessResponse(BaseModel):
    """Readiness probe response model."""

    status: Literal["ready", "not_ready"] = Field(..., description="Overall readiness status")
    timestamp: datetime = Field(..., description="Current UTC timestamp")
    components: dict[str, ComponentHealth] = Field(..., description="Dependency breakdown")
