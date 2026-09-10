"""Pytest Test Configuration and Global Fixtures.

Configures an isolated in-memory SQLite database for async tests, provides auth headers,
test users, and organization fixtures.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.auth import create_access_token
from app.core.config import Settings, get_settings
from app.core.database import Base
from app.main import app
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services.user_service import UserService

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def get_test_settings() -> Settings:
    """Return test-specific application settings."""
    return Settings(
        ENVIRONMENT="testing",
        DEBUG=True,
        LOG_LEVEL="DEBUG",
        DATABASE_URL=TEST_DATABASE_URL,
        REDIS_URL="redis://localhost:6379/15",
        ALLOWED_ORIGINS=["http://localhost:3000"],
        JWT_SECRET_KEY="test_secret_jwt_key_32_bytes_long_here",
        ACCESS_TOKEN_EXPIRE_MINUTES=60,
    )


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """Specify asyncio backend for pytest-asyncio/anyio."""
    return "asyncio"


@pytest.fixture
async def test_engine():
    """Create isolated test database engine and initialize tables."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated database session for testing."""
    session_factory = async_sessionmaker(
        bind=test_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async test client with database dependency overrides."""
    app.dependency_overrides[get_settings] = get_test_settings
    app.dependency_overrides[get_db] = lambda: db_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create and return a sample registered user."""
    user_service = UserService(db_session)
    return await user_service.register_user(
        RegisterRequest(
            email="developer@cortexa.ai",
            password="SecurePassword123!",
            full_name="Lead Architect",
        )
    )


@pytest.fixture
async def test_user_two(db_session: AsyncSession) -> User:
    """Create a second test user."""
    user_service = UserService(db_session)
    return await user_service.register_user(
        RegisterRequest(
            email="engineer@cortexa.ai",
            password="SecurePassword123!",
            full_name="Software Engineer",
        )
    )


@pytest.fixture
def auth_headers(test_user: User) -> dict[str, str]:
    """Generate authorization headers for test_user."""
    token = create_access_token(
        subject=test_user.id,
        extra_claims={"email": test_user.email},
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_two(test_user_two: User) -> dict[str, str]:
    """Generate authorization headers for test_user_two."""
    token = create_access_token(
        subject=test_user_two.id,
        extra_claims={"email": test_user_two.email},
    )
    return {"Authorization": f"Bearer {token}"}
