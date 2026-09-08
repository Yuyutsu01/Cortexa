"""API Router Aggregation.

Combines modular API routes under versioned prefixes.
"""

from fastapi import APIRouter

from app.api.routes import health

api_router = APIRouter()

# Include health routes under /api/v1
api_router.include_router(health.router)
