"""
Health Check Endpoints

Kubernetes-style health probes for production deployments.
Checks liveness, readiness, and startup conditions.

ARCHITECTURE: Health checks must never fail the application.
They report status for orchestration decisions.
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel

from hope.config import get_settings
from hope.config.logging_config import get_logger
from hope.infrastructure.llm import get_llm_provider

logger = get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthStatus(BaseModel):
    """Health check response."""
    
    status: str  # healthy, degraded, unhealthy
    timestamp: str
    version: str = "0.1.0"
    checks: dict[str, dict] = {}


class ComponentHealth(BaseModel):
    """Individual component health."""
    
    status: str
    latency_ms: Optional[int] = None
    message: Optional[str] = None


# Startup state tracking
_startup_complete = False
_startup_time: Optional[datetime] = None


def mark_startup_complete() -> None:
    """Mark application startup as complete."""
    global _startup_complete, _startup_time
    _startup_complete = True
    _startup_time = datetime.utcnow()
    logger.info("Application startup complete")


@router.get("/live", response_model=HealthStatus)
async def liveness() -> HealthStatus:
    """
    Liveness probe.
    
    Returns 200 if the process is alive.
    Kubernetes uses this to decide whether to restart the container.
    
    This should ALWAYS return 200 unless the process is deadlocked.
    """
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        checks={
            "process": {"status": "alive"},
        },
    )


@router.get("/ready", response_model=HealthStatus)
async def readiness(response: Response) -> HealthStatus:
    """
    Readiness probe.
    
    Returns 200 if ready to serve traffic.
    Kubernetes uses this to decide whether to route traffic.
    
    Checks:
    - Database connectivity
    - LLM provider availability
    """
    checks = {}
    overall_status = "healthy"
    
    # Check database
    db_status = await _check_database()
    checks["database"] = db_status
    if db_status["status"] != "healthy":
        overall_status = "degraded"
    
    # Check LLM provider
    llm_status = await _check_llm()
    checks["llm"] = llm_status
    if llm_status["status"] != "healthy":
        overall_status = "degraded"
    
    # Set response code
    if overall_status != "healthy":
        response.status_code = 503
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks,
    )


@router.get("/startup", response_model=HealthStatus)
async def startup(response: Response) -> HealthStatus:
    """
    Startup probe.
    
    Returns 200 if startup is complete.
    Kubernetes uses this during initial container startup.
    """
    if not _startup_complete:
        response.status_code = 503
        return HealthStatus(
            status="starting",
            timestamp=datetime.utcnow().isoformat(),
            checks={
                "startup": {
                    "status": "in_progress",
                    "message": "Application is still starting up",
                },
            },
        )
    
    return HealthStatus(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        checks={
            "startup": {
                "status": "complete",
                "started_at": _startup_time.isoformat() if _startup_time else None,
            },
        },
    )


@router.get("/", response_model=HealthStatus)
async def health_summary(response: Response) -> HealthStatus:
    """
    Comprehensive health summary.
    
    Returns detailed status of all components.
    """
    checks = {}
    overall_status = "healthy"
    
    # Database
    db_status = await _check_database()
    checks["database"] = db_status
    
    # LLM
    llm_status = await _check_llm()
    checks["llm"] = llm_status
    
    # Startup
    checks["startup"] = {
        "status": "complete" if _startup_complete else "in_progress",
    }
    
    # Determine overall status
    statuses = [c.get("status", "unknown") for c in checks.values()]
    if any(s == "unhealthy" for s in statuses):
        overall_status = "unhealthy"
        response.status_code = 503
    elif any(s == "degraded" for s in statuses):
        overall_status = "degraded"
    
    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        checks=checks,
    )


async def _check_database() -> dict:
    """Check database connectivity."""
    try:
        from hope.infrastructure.database import get_db_session
        from sqlalchemy import text
        import time
        
        start = time.time()
        async for session in get_db_session():
            await session.execute(text("SELECT 1"))
            break
        latency = int((time.time() - start) * 1000)
        
        return {
            "status": "healthy",
            "latency_ms": latency,
        }
    except Exception as e:
        logger.warning("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "message": "Database connection failed",
        }


async def _check_llm() -> dict:
    """Check LLM provider availability."""
    try:
        import time
        
        provider = get_llm_provider()
        
        if not provider.is_configured():
            return {
                "status": "degraded",
                "message": "LLM provider not configured",
            }
        
        start = time.time()
        is_healthy = await provider.health_check()
        latency = int((time.time() - start) * 1000)
        
        if is_healthy:
            return {
                "status": "healthy",
                "latency_ms": latency,
                "provider": provider.provider_name,
            }
        else:
            return {
                "status": "degraded",
                "message": "LLM health check failed",
                "provider": provider.provider_name,
            }
    except Exception as e:
        logger.warning("LLM health check failed", error=str(e))
        return {
            "status": "degraded",
            "message": f"LLM check error: {str(e)[:50]}",
        }
