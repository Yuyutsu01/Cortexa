"""Tests for Pydantic Application Configuration."""

from app.core.config import Settings


def test_settings_default_values() -> None:
    """Test that default configuration values are populated properly."""
    settings = Settings(
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert settings.PROJECT_NAME == "Cortexa API"
    assert settings.PROJECT_VERSION == "0.1.0"
    assert settings.API_PORT == 8000
    assert not settings.is_production


def test_settings_origins_parsing_comma_separated() -> None:
    """Test parsing of comma-separated CORS origins."""
    settings = Settings(
        ALLOWED_ORIGINS="http://localhost:3000, https://cortexa.ai",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert len(settings.ALLOWED_ORIGINS) == 2
    assert "http://localhost:3000" in settings.ALLOWED_ORIGINS
    assert "https://cortexa.ai" in settings.ALLOWED_ORIGINS


def test_settings_origins_parsing_json_array() -> None:
    """Test parsing of JSON string formatted CORS origins."""
    settings = Settings(
        ALLOWED_ORIGINS='["http://localhost:3000", "http://localhost:8080"]',
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert len(settings.ALLOWED_ORIGINS) == 2
    assert "http://localhost:3000" in settings.ALLOWED_ORIGINS
    assert "http://localhost:8080" in settings.ALLOWED_ORIGINS


def test_environment_flags() -> None:
    """Test is_production and is_testing properties."""
    prod_settings = Settings(
        ENVIRONMENT="production",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert prod_settings.is_production
    assert not prod_settings.is_testing

    test_settings = Settings(
        ENVIRONMENT="testing",
        DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
        REDIS_URL="redis://localhost:6379/0",
    )
    assert not test_settings.is_production
    assert test_settings.is_testing
