"""
HOPE FastAPI Application Entry Point

Main application initialization with:
- Lifespan management (startup/shutdown)
- CORS configuration
- Error handling middleware
- Router registration
- Health endpoints

This is the production entry point for the HOPE backend.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from hope.config import get_settings
from hope.config.logging_config import configure_logging, get_logger
from hope.infrastructure.database import get_db_manager
from hope.services.orchestration.response_orchestrator import ResponseOrchestrator
from hope.api.v1.router import api_router
from hope.api.middleware.error_handler import ErrorHandlerMiddleware
from hope.api.middleware.rate_limiter import RateLimitMiddleware, RateLimitConfig

# Initialize settings and logging
settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)

# Global orchestrator instance (initialized during startup)
_orchestrator: ResponseOrchestrator | None = None


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        if settings.is_production():
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        return response


def get_orchestrator() -> ResponseOrchestrator:
    """Get the global orchestrator instance."""
    if _orchestrator is None:
        raise RuntimeError("Orchestrator not initialized")
    return _orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown of all services.
    """
    global _orchestrator
    
    logger.info(
        "Starting HOPE application",
        env=settings.env,
        version="0.1.0",
    )
    
    # Startup
    try:
        # Initialize Sentry for production monitoring
        if settings.env != "development":
            try:
                from hope.infrastructure.monitoring.sentry_integration import init_sentry
                import os
                sentry_dsn = os.environ.get("HOPE_SENTRY_DSN", "")
                if sentry_dsn:
                    init_sentry(
                        dsn=sentry_dsn,
                        environment=settings.env,
                        release="hope@0.1.0",
                    )
            except Exception as e:
                logger.warning("Sentry initialization failed", error=str(e))
        
        # Initialize database
        try:
            db = get_db_manager()
            await db.initialize()
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(
                "Database initialization failed - app will start but DB features unavailable",
                error=str(e),
            )
        
        # Initialize orchestrator (and ML models)
        try:
            _orchestrator = ResponseOrchestrator()
            if settings.env != "development":
                # Only pre-load models in non-dev environments
                await _orchestrator.initialize()
            logger.info("Response orchestrator initialized")
        except Exception as e:
            logger.error(
                "Orchestrator initialization failed",
                error=str(e),
            )
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down HOPE application")
        
        if _orchestrator:
            try:
                await _orchestrator.shutdown()
            except Exception:
                pass
        
        try:
            db = get_db_manager()
            await db.close()
        except Exception:
            pass
        
        logger.info("HOPE application shutdown complete")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="HOPE API",
        description="AI-powered panic attack support system - Backend API",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production() else None,
        redoc_url="/redoc" if not settings.is_production() else None,
        openapi_url="/openapi.json" if not settings.is_production() else None,
        lifespan=lifespan,
    )
    
    # --- Middleware stack (order matters: last added = first executed) ---
    
    # GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=500)
    
    # CORS — uses settings, no wildcard in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials="*" not in settings.cors_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        config=RateLimitConfig(
            requests_per_minute=settings.safety.rate_limit_requests_per_minute,
            panic_requests_per_minute=120,
            burst_size=10,
        ),
    )
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Error handling
    app.add_middleware(ErrorHandlerMiddleware)
    
    # Register API routers
    app.include_router(
        api_router,
        prefix=f"/api/{settings.api_version}",
    )
    
    # Register WebSocket endpoints (at root level, not under /api/v1)
    from hope.api.v1.endpoints.websocket import router as ws_router
    app.include_router(ws_router)
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root() -> dict:
        """Root endpoint - basic info."""
        return {
            "name": "HOPE API",
            "version": "0.1.0",
            "status": "operational",
        }
    
    # Root health endpoint for Flutter connectivity check
    @app.get("/health", include_in_schema=False)
    async def health_root() -> dict:
        """Root health endpoint for mobile app connectivity check."""
        return {"status": "ok"}
    
    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "hope.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.env == "development",
        log_level=settings.log_level.lower(),
    )
