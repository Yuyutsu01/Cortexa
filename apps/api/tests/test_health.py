"""Tests for Health Liveness Endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_liveness_endpoint(client: AsyncClient) -> None:
    """Verify that GET /health returns 200 OK and valid health payload."""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data

    # Verify request correlation header is attached
    assert "x-request-id" in response.headers
    assert "x-process-time-ms" in response.headers


@pytest.mark.asyncio
async def test_health_liveness_api_v1(client: AsyncClient) -> None:
    """Verify that GET /api/v1/health is also routed and functional."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
