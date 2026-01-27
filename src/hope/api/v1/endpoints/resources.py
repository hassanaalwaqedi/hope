"""
Resources API Endpoints

AI-personalized mental health resource recommendations.
Uses IntelligenceService for intelligent ranking and explanations.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from hope.services.intelligence import get_intelligence_service

router = APIRouter()


class ResourcesRequest(BaseModel):
    """Request for AI-personalized resources."""
    session_id: str = Field(..., description="Active session ID")
    query: Optional[str] = Field(None, description="Specific resource query")


class ResourcesResponse(BaseModel):
    """AI-generated resource recommendations."""
    recommendations: str
    ai_called: bool
    latency_ms: Optional[int] = None
    fallback: bool = False


@router.post("/personalized", response_model=ResourcesResponse)
async def get_personalized_resources(request: ResourcesRequest) -> ResourcesResponse:
    """
    Get AI-personalized resource recommendations.
    
    The AI ranks and explains resources based on the user's context,
    recent conversations, and emotional state.
    """
    service = get_intelligence_service()
    
    try:
        session_id = UUID(request.session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    result = await service.get_personalized_resources(
        session_id=session_id,
        query=request.query,
    )
    
    return ResourcesResponse(**result)


@router.get("/status")
async def get_resources_ai_status() -> dict:
    """Check if resources AI is available."""
    service = get_intelligence_service()
    return {
        "ai_enabled": service.is_available,
        "feature": "resources",
    }


# Crisis resources endpoints (country-aware)

class CrisisResourcesRequest(BaseModel):
    """Request for crisis resources."""
    country_code: str = Field(..., description="ISO country code (e.g., US, FR, DE)")
    language: str = Field(default="en", description="Preferred language")


class CrisisResource(BaseModel):
    """Single crisis resource."""
    name: str
    type: str
    contact: str
    description: str
    available_24_7: bool


class CrisisResourcesResponse(BaseModel):
    """Country-specific crisis resources."""
    country_code: str
    country_name: str
    emergency_number: str
    resources: list[CrisisResource]
    disclaimer: str


@router.post("/crisis", response_model=CrisisResourcesResponse)
async def get_crisis_resources(request: CrisisResourcesRequest) -> CrisisResourcesResponse:
    """
    Get country-specific crisis resources.
    
    Returns emergency hotlines and mental health resources
    for the user's country. Designed for crisis situations.
    """
    from hope.services.safety.emergency_resources import EmergencyResourceResolver
    
    resolver = EmergencyResourceResolver()
    jurisdiction = resolver.get_resources(request.country_code)
    
    resources = [
        CrisisResource(
            name=r.name,
            type=r.resource_type,
            contact=r.contact,
            description=r.description,
            available_24_7=r.available_24_7,
        )
        for r in jurisdiction.resources
    ]
    
    # Localized disclaimers
    disclaimers = {
        "en": "HOPE is not a substitute for professional mental health care. If you are in immediate danger, please call emergency services.",
        "fr": "HOPE ne remplace pas les soins de santé mentale professionnels. Si vous êtes en danger immédiat, appelez les services d'urgence.",
        "de": "HOPE ersetzt keine professionelle psychische Gesundheitsversorgung. Bei unmittelbarer Gefahr rufen Sie bitte den Notdienst an.",
        "es": "HOPE no sustituye la atención profesional de salud mental. Si está en peligro inmediato, llame a los servicios de emergencia.",
        "ar": "تطبيق HOPE ليس بديلاً عن الرعاية الصحية النفسية المهنية. إذا كنت في خطر فوري، يرجى الاتصال بخدمات الطوارئ.",
    }
    
    return CrisisResourcesResponse(
        country_code=jurisdiction.country_code,
        country_name=jurisdiction.country_name,
        emergency_number=jurisdiction.emergency_number,
        resources=resources,
        disclaimer=disclaimers.get(request.language, disclaimers["en"]),
    )


@router.get("/supported-countries")
async def get_supported_countries() -> dict:
    """Get list of countries with crisis resources."""
    from hope.services.safety.emergency_resources import EmergencyResourceResolver
    
    resolver = EmergencyResourceResolver()
    countries = resolver.list_supported_countries()
    
    return {
        "count": len(countries),
        "countries": sorted(countries),
    }
