"""Pytest Fixtures and Global Configuration.

Provides async test clients and mock dependencies for deterministic test execution.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import app


def get_test_settings() -> Settings:
    """Return test-specific settings."""
    return Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/15",
        ALLOWED_ORIGINS=["http://localhost:3000"],
    )


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Specify asyncio backend for pytest-asyncio/anyio."""
    return "asyncio"


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an asynchronous HTTP client bound to the FastAPI ASGI application."""
    # Override settings for tests
    app.dependency_overrides[get_settings] = get_test_settings

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client

    app.dependency_overrides.clear()
