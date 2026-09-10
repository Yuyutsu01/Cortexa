"""API Router Aggregation.

Combines modular API routes under versioned prefixes.
"""

from fastapi import APIRouter

from app.api.routes import audit, auth, health, members, organizations

api_router = APIRouter()

# Register API v1 routes
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(members.router)
api_router.include_router(audit.router)
