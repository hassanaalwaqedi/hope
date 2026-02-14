"""
API v1 Router

Aggregates all v1 API endpoints.
"""

from fastapi import APIRouter

from hope.api.auth.endpoints import router as auth_router
from hope.api.v1.endpoints.health import router as health_router
from hope.api.v1.endpoints.session import router as session_router
from hope.api.v1.endpoints.chat import router as chat_router
from hope.api.v1.endpoints.breathing import router as breathing_router
from hope.api.v1.endpoints.resources import router as resources_router
from hope.api.v1.endpoints.consent import router as consent_router
from hope.api.v1.endpoints.voice import router as voice_router
from hope.api.v1.endpoints.user import router as user_router

api_router = APIRouter()

# Auth endpoints (no prefix - at /api/v1/auth/...)
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"],
)

# Consent endpoints
api_router.include_router(
    consent_router,
    prefix="/consent",
    tags=["Consent"],
)

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

api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"],
)

api_router.include_router(
    breathing_router,
    prefix="/breathing",
    tags=["Breathing"],
)

api_router.include_router(
    resources_router,
    prefix="/resources",
    tags=["Resources"],
)

from hope.config import get_settings as _get_router_settings

_router_settings = _get_router_settings()

# Debug endpoints - only available in non-production
if not _router_settings.is_production():
    from hope.api.v1.endpoints.ai_status import router as ai_status_router
    api_router.include_router(
        ai_status_router,
        prefix="/debug",
        tags=["Debug"],
    )

# Voice AI endpoints
api_router.include_router(
    voice_router,
    prefix="/voice",
    tags=["Voice AI"],
)

# User data & preferences endpoints
api_router.include_router(
    user_router,
    prefix="/user",
    tags=["User"],
)
