"""
API v1 Router

Aggregates all v1 API endpoints.
"""

from fastapi import APIRouter

from hope.api.v1.endpoints.health import router as health_router
from hope.api.v1.endpoints.session import router as session_router

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    session_router,
    prefix="/session",
    tags=["Session"],
)
