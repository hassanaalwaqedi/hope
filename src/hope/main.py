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
from fastapi.responses import JSONResponse

from hope.config import get_settings
from hope.config.logging_config import configure_logging, get_logger
from hope.infrastructure.database import get_db_manager
from hope.services.orchestration.response_orchestrator import ResponseOrchestrator
from hope.api.v1.router import api_router
from hope.api.middleware.error_handler import ErrorHandlerMiddleware

# Initialize settings and logging
settings = get_settings()
configure_logging(settings)
logger = get_logger(__name__)

# Global orchestrator instance (initialized during startup)
_orchestrator: ResponseOrchestrator | None = None


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
            from hope.infrastructure.monitoring.sentry_integration import init_sentry
            import os
            sentry_dsn = os.environ.get("HOPE_SENTRY_DSN", "")
            if sentry_dsn:
                init_sentry(
                    dsn=sentry_dsn,
                    environment=settings.env,
                    release="hope@0.1.0",
                )
        
        # Initialize database
        db = get_db_manager()
        await db.initialize()
        logger.info("Database connection initialized")
        
        # Initialize orchestrator (and ML models)
        _orchestrator = ResponseOrchestrator()
        if settings.env != "development":
            # Only pre-load models in non-dev environments
            await _orchestrator.initialize()
        logger.info("Response orchestrator initialized")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down HOPE application")
        
        if _orchestrator:
            await _orchestrator.shutdown()
        
        db = get_db_manager()
        await db.close()
        
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
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    # For development, allow all origins (credentials disabled for wildcard compatibility)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all for dev - Flutter web uses dynamic ports
        allow_credentials=False,  # Must be False when using wildcard "*"
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add error handling middleware
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
