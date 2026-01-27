"""
Breathing API Endpoints

AI-powered breathing exercise guidance.
Uses IntelligenceService to adapt techniques based on user state.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hope.services.intelligence import get_intelligence_service

router = APIRouter()


class BreathingRequest(BaseModel):
    """Request for AI-adapted breathing guidance."""
    session_id: str = Field(..., description="Active session ID")
    user_request: Optional[str] = Field(None, description="Optional specific request")
    anxiety_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Current anxiety level 0-1")


class BreathingResponse(BaseModel):
    """AI-generated breathing guidance."""
    guidance: str
    ai_called: bool
    latency_ms: Optional[int] = None
    fallback: bool = False


@router.post("/adapted", response_model=BreathingResponse)
async def get_adapted_breathing(request: BreathingRequest) -> BreathingResponse:
    """
    Get AI-adapted breathing technique and guidance.
    
    The AI selects the best technique based on the user's current state
    and provides personalized step-by-step guidance.
    """
    service = get_intelligence_service()
    
    try:
        session_id = UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Update context with anxiety level if provided
    if request.anxiety_level is not None:
        service.update_context(session_id, anxiety_level=request.anxiety_level)
    
    result = await service.get_adapted_breathing_technique(
        session_id=session_id,
        user_request=request.user_request,
    )
    
    # Update context that exercise was started
    service.update_context(session_id, exercise_completed="breathing")
    
    return BreathingResponse(**result)


@router.get("/status")
async def get_breathing_ai_status() -> dict:
    """Check if breathing AI is available."""
    service = get_intelligence_service()
    return {
        "ai_enabled": service.is_available,
        "feature": "breathing",
    }
