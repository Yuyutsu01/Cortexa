"""Application Configuration Module.

Uses Pydantic Settings for strongly-typed, environment-driven configuration.
"""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings validated at runtime."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application details
    PROJECT_NAME: str = "Cortexa API"
    PROJECT_VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(
        default="development",
        description="Current environment: development, staging, production, testing",
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    LOG_LEVEL: str = Field(
        default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )

    # API Server configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # CORS configuration
    ALLOWED_ORIGINS: list[str] | str = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # PostgreSQL Database configuration
    POSTGRES_USER: str = "cortexa"
    POSTGRES_PASSWORD: str = "cortexa_secret_dev"
    POSTGRES_DB: str = "cortexa_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://cortexa:cortexa_secret_dev@localhost:5432/cortexa_db",
        description="Async SQLAlchemy database connection URI",
    )
    DATABASE_SYNC_URL: str = Field(
        default="postgresql+psycopg2://cortexa:cortexa_secret_dev@localhost:5432/cortexa_db",
        description="Synchronous database connection URI for migrations and sync utilities",
    )

    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = ""
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URI",
    )

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        """Convert comma-separated origin strings into a list if necessary."""
        if isinstance(value, str):
            # Check if it is a JSON array or comma-delimited string
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                import json

                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return [str(item) for item in parsed]
                except Exception:
                    pass
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return list(value)

    @property
    def is_production(self) -> bool:
        """Check if application is running in production mode."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_testing(self) -> bool:
        """Check if application is running in test mode."""
        return self.ENVIRONMENT.lower() == "testing"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance to prevent redundant environment parsing."""
    return Settings()
