"""
Health Check Endpoints

Provides system health and readiness endpoints for:
- Load balancer health checks
- Kubernetes probes
- Monitoring systems
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from hope.infrastructure.database import get_db_manager

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    """Readiness check response with component health."""
    
    ready: bool
    components: dict


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health check",
    description="Basic health check endpoint for load balancers",
)
async def health_check() -> HealthResponse:
    """
    Basic health check.
    
    Returns 200 if application is running.
    Used by load balancers and basic monitoring.
    """
    from hope.config import get_settings
    settings = get_settings()
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.env,
    )


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    summary="Readiness check",  
    description="Detailed readiness check including all components",
)
async def readiness_check() -> ReadinessResponse:
    """
    Detailed readiness check.
    
    Checks connectivity to all critical components:
    - Database
    - LLM providers
    - ML models
    
    Returns 200 with status of each component.
    """
    components = {}
    
    # Check database
    try:
        db = get_db_manager()
        components["database"] = await db.health_check()
    except Exception:
        components["database"] = False
    
    # Check orchestrator/LLM - import inside function to avoid circular import
    try:
        from hope.main import get_orchestrator
        orchestrator = get_orchestrator()
        orchestrator_health = await orchestrator.health_check()
        components.update(orchestrator_health)
    except Exception:
        components["orchestrator"] = False
        components["llm_available"] = False
    
    # Determine overall readiness
    # We're ready if database is up and at least one LLM is available
    ready = (
        components.get("database", False) and
        components.get("llm_available", False)
    )
    
    return ReadinessResponse(
        ready=ready,
        components=components,
    )


@router.get(
    "/live",
    response_model=HealthResponse,
    summary="Liveness probe",
    description="Kubernetes liveness probe endpoint",
)
async def liveness_check() -> HealthResponse:
    """
    Kubernetes liveness probe.
    
    Returns 200 if application process is alive.
    If this fails, K8s will restart the pod.
    """
    from hope.config import get_settings
    settings = get_settings()
    
    return HealthResponse(
        status="alive",
        version="0.1.0",
        environment=settings.env,
    )
