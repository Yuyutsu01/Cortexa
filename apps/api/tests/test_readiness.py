"""Tests for Health Readiness Endpoint."""

import pytest
from httpx import AsyncClient
from pytest import MonkeyPatch

import app.api.routes.health as health_module


@pytest.mark.asyncio
async def test_readiness_all_healthy(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    """Verify that GET /health/ready returns 200 OK when both DB and Redis are healthy."""

    async def mock_db_healthy() -> tuple[bool, str]:
        return True, "Mock DB connected"

    async def mock_redis_healthy() -> tuple[bool, str]:
        return True, "Mock Redis connected"

    monkeypatch.setattr(health_module, "check_database_connection", mock_db_healthy)
    monkeypatch.setattr(health_module, "check_redis_connection", mock_redis_healthy)

    response = await client.get("/health/ready")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ready"
    assert data["components"]["database"]["status"] == "healthy"
    assert data["components"]["redis"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_db_down(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    """Verify that GET /health/ready returns 503 Service Unavailable when DB is down."""

    async def mock_db_down() -> tuple[bool, str]:
        return False, "Connection refused"

    async def mock_redis_healthy() -> tuple[bool, str]:
        return True, "Mock Redis connected"

    monkeypatch.setattr(health_module, "check_database_connection", mock_db_down)
    monkeypatch.setattr(health_module, "check_redis_connection", mock_redis_healthy)

    response = await client.get("/health/ready")
    assert response.status_code == 503

    data = response.json()
    assert data["status"] == "not_ready"
    assert data["components"]["database"]["status"] == "unhealthy"
    assert data["components"]["redis"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_redis_down(client: AsyncClient, monkeypatch: MonkeyPatch) -> None:
    """Verify that GET /health/ready returns 503 Service Unavailable when Redis is down."""

    async def mock_db_healthy() -> tuple[bool, str]:
        return True, "Mock DB connected"

    async def mock_redis_down() -> tuple[bool, str]:
        return False, "Redis timeout"

    monkeypatch.setattr(health_module, "check_database_connection", mock_db_healthy)
    monkeypatch.setattr(health_module, "check_redis_connection", mock_redis_down)

    response = await client.get("/health/ready")
    assert response.status_code == 503

    data = response.json()
    assert data["status"] == "not_ready"
    assert data["components"]["database"]["status"] == "healthy"
    assert data["components"]["redis"]["status"] == "unhealthy"
