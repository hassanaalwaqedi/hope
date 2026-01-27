"""
AI Status Debug Endpoint

Provides real-time visibility into AI coverage across all features.
Shows which features call Gemini, latency metrics, and coverage percentage.
"""

from fastapi import APIRouter

from hope.services.intelligence import get_intelligence_service

router = APIRouter()


@router.get("/ai-status")
async def get_ai_status() -> dict:
    """
    Get real-time AI status across all features.
    
    Returns:
        AI coverage metrics including:
        - ai_enabled: Whether Gemini is configured
        - model: Current model being used
        - features: Per-feature AI call statistics
        - coverage_percentage: Percentage of calls using AI
    """
    service = get_intelligence_service()
    return service.get_ai_status()


@router.get("/ai-health")
async def get_ai_health() -> dict:
    """Quick health check for AI service."""
    service = get_intelligence_service()
    return {
        "status": "healthy" if service.is_available else "degraded",
        "ai_enabled": service.is_available,
        "model": service.MODEL_NAME,
    }
