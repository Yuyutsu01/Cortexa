"""Main FastAPI Application Entrypoint.

Initializes the FastAPI application with lifespan management, CORS, middleware,
custom exception handling, and modular routes.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.database import close_database_connection
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import register_middlewares
from app.core.redis import close_redis_connection


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager for deterministic startup and teardown."""
    settings = get_settings()
    logger = setup_logging(settings.LOG_LEVEL)
    logger.info(
        "Starting %s [v%s] in %s environment...",
        settings.PROJECT_NAME,
        settings.PROJECT_VERSION,
        settings.ENVIRONMENT,
    )

    yield

    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    # Clean up infrastructure connections
    await close_database_connection()
    await close_redis_connection()
    logger.info("Shutdown complete.")


def create_application() -> FastAPI:
    """FastAPI application factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        description="Production-grade AI-native sales automation platform API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Register Exception Handlers
    register_exception_handlers(app)

    # 2. Register Middleware (Request ID, timing, etc.)
    register_middlewares(app)

    # 3. Configure CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 4. Mount Root Probes (for Docker/Kubernetes probes at root level)
    app.include_router(health_router)

    # 5. Mount API v1 Router
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
