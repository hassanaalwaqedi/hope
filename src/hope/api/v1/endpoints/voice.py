"""
Voice Transcript API Endpoint

Handles voice-transcribed input from mobile app.
Preserves original transcript, detected language, and confidence score.
Routes through standard ClinicalPipeline + SafetyPipeline.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from hope.config.logging_config import get_logger
from hope.infrastructure.database import get_async_session
from hope.infrastructure.database.repositories.session_repository import SessionRepository
from hope.api.auth.dependencies import get_token_data_optional
from hope.api.auth.service import TokenData

logger = get_logger(__name__)
router = APIRouter()


class VoiceTranscriptRequest(BaseModel):
    """Request containing voice-transcribed text."""
    
    session_id: UUID = Field(..., description="Session ID")
    transcript: str = Field(..., min_length=1, max_length=4000, description="Voice transcript")
    detected_language: str = Field(default="en", description="Detected language code")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Recognition confidence")
    is_panic_mode: bool = Field(default=False, description="Whether in continuous panic listening mode")


class VoiceResponse(BaseModel):
    """Response optimized for voice output (TTS)."""
    
    session_id: UUID
    response_text: str
    spoken_text: str  # TTS-optimized version
    severity: str
    urgency: str
    suggested_action: Optional[str] = None  # e.g., "breathing", "grounding", "crisis"
    crisis_hotline: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "response_text": "I hear you. Let's try a breathing exercise together.",
                "spoken_text": "I hear you. ... Let's try a breathing exercise together.",
                "severity": "MODERATE",
                "urgency": "high",
                "suggested_action": "breathing",
                "crisis_hotline": None,
            }
        }


@router.post(
    "/transcript",
    response_model=VoiceResponse,
    summary="Process voice transcript",
)
async def process_voice_transcript(
    request: VoiceTranscriptRequest,
    db: AsyncSession = Depends(get_async_session),
    token_data: Optional[TokenData] = Depends(get_token_data_optional),
) -> VoiceResponse:
    """
    Process voice-transcribed input through the AI pipeline.
    
    The transcript is processed identically to typed messages,
    but the response is optimized for TTS output with:
    - Short sentences
    - Pauses (ellipses) between phrases
    - Suggested actions for the voice UI
    """
    repo = SessionRepository(db)
    
    # Get session
    session = await repo.get_by_id(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )
    
    # Store user message with voice metadata
    await repo.add_message(
        session_id=request.session_id,
        role="user",
        content=request.transcript,
        metadata={
            "source": "voice",
            "detected_language": request.detected_language,
            "confidence": request.confidence,
            "is_panic_mode": request.is_panic_mode,
        },
    )
    
    try:
        # Import inside function to avoid circular import
        from hope.main import get_orchestrator
        from hope.domain.models.session import Session, SessionState
        
        orchestrator = get_orchestrator()
        
        # Create domain session
        domain_session = Session(
            id=session.id,
            user_id=session.user_id,
            state=SessionState(session.state),
        )
        
        # Load message history
        for msg in session.messages or []:
            domain_session.add_message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                metadata=msg.get("metadata", {}),
            )
        
        # Process through pipeline with voice context
        result = await orchestrator.process(
            user_message=request.transcript,
            user_id=session.user_id,
            session=domain_session,
            context={
                "input_mode": "voice",
                "language": request.detected_language,
                "is_panic_mode": request.is_panic_mode,
            },
        )
        
        # Generate TTS-optimized text
        spoken_text = _optimize_for_speech(result.response_text)
        
        # Determine suggested action from response
        suggested_action = _detect_suggested_action(
            result.response_text,
            result.detection.severity.name,
        )
        
        # Check for crisis situation
        crisis_hotline = None
        if result.detection.requires_escalation:
            crisis_hotline = _get_crisis_hotline(request.detected_language)
        
        # Store assistant response with voice metadata
        await repo.add_message(
            session_id=request.session_id,
            role="assistant",
            content=result.response_text,
            metadata={
                "source": "voice_response",
                "spoken_text": spoken_text,
                "severity": result.detection.severity.name,
                "suggested_action": suggested_action,
            },
        )
        
        await db.commit()
        
        logger.info(
            "Voice transcript processed",
            session_id=str(session.id),
            language=request.detected_language,
            severity=result.detection.severity.name,
        )
        
        return VoiceResponse(
            session_id=session.id,
            response_text=result.response_text,
            spoken_text=spoken_text,
            severity=result.detection.severity.name,
            urgency=result.detection.urgency.value,
            suggested_action=suggested_action,
            crisis_hotline=crisis_hotline,
        )
        
    except Exception as e:
        logger.error(
            "Voice transcript processing failed",
            session_id=str(session.id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process voice input. Please try again.",
        )


def _optimize_for_speech(text: str) -> str:
    """
    Convert text to TTS-optimized format.
    
    - Adds pauses between sentences
    - Shortens long sentences
    - Removes formatting that doesn't translate to speech
    """
    # Add pauses after sentences
    spoken = text.replace(". ", ". ... ")
    spoken = spoken.replace("? ", "? ... ")
    spoken = spoken.replace("! ", "! ... ")
    
    # Remove markdown formatting
    spoken = spoken.replace("**", "")
    spoken = spoken.replace("*", "")
    spoken = spoken.replace("_", "")
    spoken = spoken.replace("#", "")
    
    # Remove URLs (can't speak those)
    import re
    spoken = re.sub(r'https?://\S+', '', spoken)
    
    return spoken.strip()


def _detect_suggested_action(response: str, severity: str) -> Optional[str]:
    """
    Detect if the response suggests a specific action.
    """
    response_lower = response.lower()
    
    # Check for exercise suggestions
    if any(word in response_lower for word in ['breath', 'respir', 'atmen', 'inhale', 'exhale']):
        return "breathing"
    
    if any(word in response_lower for word in ['ground', 'ancrage', 'erdung', 'look around', 'senses']):
        return "grounding"
    
    # Crisis severity
    if severity in ("CRITICAL", "SEVERE"):
        return "crisis"
    
    return None


def _get_crisis_hotline(language: str) -> Optional[str]:
    """
    Get crisis hotline for language/region.
    """
    hotlines = {
        "en": "988 (US) or 116 123 (UK)",
        "fr": "3114",
        "de": "0800 111 0 111",
        "es": "024",
        "ar": "Emergency services",
    }
    return hotlines.get(language, hotlines["en"])


# Voice-specific prompts for Gemini

VOICE_SYSTEM_PROMPT_ADDITION = """
VOICE MODE ACTIVE:
You are responding via voice (text-to-speech).
Critical constraints:
- Keep sentences SHORT (max 15 words each)
- Use SIMPLE words
- Be CALM and SLOW in tone
- No lists or bullet points
- No URLs or technical terms
- Add natural pauses (use "..." between thoughts)
- Be DIRECTIVE when needed ("Let's try breathing together")
- Never diagnose or give medical advice
- If crisis detected, clearly state hotline number

Example good voice response:
"I hear you. ... You're safe right now. ... Let's breathe together. ... Breathe in slowly."

Example bad response (too long, too complex):
"I understand you're experiencing anxiety, and while there are many techniques we could explore including deep breathing, progressive muscle relaxation, and grounding exercises, I think we should start with something simple."
"""
