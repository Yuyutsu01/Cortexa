"""Health and Readiness Endpoints.

Provides Kubernetes/Docker compatible liveness and readiness probe routes.
"""

import asyncio
from datetime import UTC, datetime

from fastapi import APIRouter, Response, status

from app.core.config import get_settings
from app.core.database import check_database_connection
from app.core.redis import check_redis_connection
from app.schemas.health import ComponentHealth, HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness Probe",
    description="Returns 200 OK if the API server process is alive and receiving requests.",
)
async def get_health() -> HealthResponse:
    """Liveness probe to confirm the API service process is up."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.PROJECT_VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness Probe",
    description="Verifies that all downstream infrastructure components (PostgreSQL, Redis) are healthy.",
    responses={
        200: {"description": "All infrastructure dependencies are healthy and ready."},
        503: {"description": "One or more infrastructure dependencies are unavailable."},
    },
)
async def get_readiness(response: Response) -> ReadinessResponse:
    """Readiness probe checking PostgreSQL and Redis dependencies concurrently."""
    # Execute checks concurrently for low latency
    db_task = check_database_connection()
    redis_task = check_redis_connection()
    (db_ok, db_msg), (redis_ok, redis_msg) = await asyncio.gather(db_task, redis_task)

    components: dict[str, ComponentHealth] = {
        "database": ComponentHealth(
            status="healthy" if db_ok else "unhealthy",
            message=db_msg,
        ),
        "redis": ComponentHealth(
            status="healthy" if redis_ok else "unhealthy",
            message=redis_msg,
        ),
    }

    all_healthy = db_ok and redis_ok
    if not all_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if all_healthy else "not_ready",
        timestamp=datetime.now(UTC),
        components=components,
    )
