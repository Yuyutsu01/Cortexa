"""Redis Infrastructure Module.

Provides asynchronous Redis connection pooling, client retrieval, and health verification.
"""

import logging

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Redis | None = None


def get_redis_client() -> Redis:
    """Retrieve or initialize the global async Redis client."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
        )
    return _redis_client


async def check_redis_connection() -> tuple[bool, str]:
    """Ping Redis to verify connectivity for readiness checks."""
    try:
        client = get_redis_client()
        pong = await client.ping()
        if bool(pong):
            return True, "Redis connected and responsive"
        return False, f"Unexpected ping response: {pong}"
    except Exception as exc:
        logger.warning("Redis health check failed: %s", exc)
        return False, f"Redis connection error: {str(exc)}"


async def close_redis_connection() -> None:
    """Close active Redis connections during application shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
        logger.info("Redis client connection pool closed.")
