"""Tests for API Error Handling and Middleware."""

import pytest
from httpx import AsyncClient

from app.core.exceptions import CortexaException
from app.main import app


@pytest.mark.asyncio
async def test_custom_exception_handling(client: AsyncClient) -> None:
    """Verify that CortexaException produces a structured JSON error response."""

    # Temporarily mount a test route raising CortexaException
    @app.get("/api/test-error")
    async def trigger_error() -> None:
        raise CortexaException(
            message="Test custom failure",
            code="TEST_ERROR",
            status_code=400,
            details={"field": "test"},
        )

    response = await client.get("/api/test-error")
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TEST_ERROR"
    assert data["error"]["message"] == "Test custom failure"
    assert data["error"]["details"] == {"field": "test"}


@pytest.mark.asyncio
async def test_not_found_error_handling(client: AsyncClient) -> None:
    """Verify standard 404 response for nonexistent routes."""
    response = await client.get("/nonexistent-route-404")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_404"
