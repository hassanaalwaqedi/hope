"""
Chat API Endpoints

Production endpoints for AI chat functionality:
- POST /chat/message - Send message with optional image
- POST /chat/message/stream - Send message with SSE streaming response
- POST /chat/session/start - Start new chat session
- GET /chat/history/{session_id} - Get session history

All responses come from real Gemini API calls - no mocks.
"""

import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from hope.config.logging_config import get_logger
from hope.services.chat.ai_chat_service import AIChatService
from hope.infrastructure.metrics.chat_metrics import (
    increment_chat_requests,
    increment_image_requests,
    observe_chat_latency,
)

logger = get_logger(__name__)
router = APIRouter()

# Singleton service instance
_chat_service: Optional[AIChatService] = None


def get_chat_service() -> AIChatService:
    """Get or create chat service instance."""
    global _chat_service
    if _chat_service is None:
        _chat_service = AIChatService()
    return _chat_service


# ============================================================================
# Request/Response Models
# ============================================================================

class StartSessionRequest(BaseModel):
    """Request to start a new chat session."""
    language: str = Field(default="fr", description="Language: 'fr' or 'en'")
    user_id: Optional[str] = Field(default=None, description="Optional user ID")


class StartSessionResponse(BaseModel):
    """Response with new session info."""
    session_id: str
    language: str
    created_at: str


class SendMessageRequest(BaseModel):
    """Request to send a chat message."""
    session_id: str = Field(..., description="Active session ID")
    text: str = Field(..., min_length=1, max_length=2000, description="Message text")
    image: Optional[str] = Field(default=None, description="Base64 encoded image")
    language: str = Field(default="fr", description="Language: 'fr' or 'en'")


class SendMessageResponse(BaseModel):
    """Response from AI chat."""
    text_answer: str
    safety_flags: list[str]
    confidence_score: float
    escalated: bool
    session_id: str
    message_id: Optional[str]
    latency_ms: int
    ai_called: bool  # Audit flag proving AI was actually called


class SessionHistoryResponse(BaseModel):
    """Response with session history."""
    session_id: str
    language: str
    message_count: int
    is_crisis_mode: bool
    created_at: str
    messages: list[dict]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/session/start", response_model=StartSessionResponse)
async def start_chat_session(request: StartSessionRequest) -> StartSessionResponse:
    """
    Start a new chat session.
    
    Creates a new session for the user to have a conversation with the AI.
    Sessions track message history and crisis state.
    """
    service = get_chat_service()
    
    if not service.is_available:
        raise HTTPException(
            status_code=503,
            detail="AI chat is not available - service not configured",
        )
    
    session = await service.start_session(
        language=request.language,
        user_id=request.user_id,
    )
    
    return StartSessionResponse(
        session_id=str(session.id),
        language=session.language.value,
        created_at=session.created_at.isoformat(),
    )


@router.post("/message", response_model=SendMessageResponse)
async def send_chat_message(request: SendMessageRequest) -> SendMessageResponse:
    """
    Send a message to the AI chatbot.
    
    This endpoint:
    1. Validates the session exists
    2. Calls Gemini Flash API (REAL call, no mock)
    3. Returns AI response with safety flags
    
    The `ai_called` field in response proves the AI was actually invoked.
    """
    service = get_chat_service()
    
    if not service.is_available:
        raise HTTPException(
            status_code=503,
            detail="AI chat is not available - Gemini API not configured",
        )
    
    try:
        session_id = UUID(request.session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format",
        )
    
    # Track metrics
    increment_chat_requests()
    if request.image:
        increment_image_requests()
    
    try:
        response = await service.send_message(
            session_id=session_id,
            text=request.text,
            image_data=request.image,
        )
        
        # Record latency
        observe_chat_latency(response.latency_ms / 1000.0)
        
        return SendMessageResponse(
            text_answer=response.text_answer,
            safety_flags=response.safety_flags,
            confidence_score=response.confidence_score,
            escalated=response.escalated,
            session_id=str(response.session_id),
            message_id=str(response.message_id) if response.message_id else None,
            latency_ms=response.latency_ms,
            ai_called=response.ai_called,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Chat message failed", error=str(e))
        raise HTTPException(status_code=500, detail="Chat service error")


@router.post("/message/stream")
async def stream_chat_message(request: SendMessageRequest):
    """
    Stream a chat message response via Server-Sent Events (SSE).
    
    Returns text tokens as they are generated by Gemini,
    enabling real-time word-by-word display in the frontend.
    
    SSE event format:
      data: {"type": "token", "text": "Hello"}
      data: {"type": "done", "session_id": "...", "latency_ms": ...}
    """
    service = get_chat_service()
    
    if not service.is_available:
        raise HTTPException(
            status_code=503,
            detail="AI chat is not available - Gemini API not configured",
        )
    
    try:
        session_id = UUID(request.session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format",
        )
    
    increment_chat_requests()
    if request.image:
        increment_image_requests()
    
    async def event_generator():
        try:
            async for chunk in service.send_message_stream(
                session_id=session_id,
                text=request.text,
                image_data=request.image,
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error("Stream failed", error=str(e))
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history/{session_id}", response_model=SessionHistoryResponse)
async def get_chat_history(session_id: str) -> SessionHistoryResponse:
    """
    Get chat session history.
    
    Returns all messages in a session for display in the history screen.
    No mock data - returns real session history or error.
    """
    service = get_chat_service()
    
    try:
        uuid_session_id = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid session ID format",
        )
    
    session = await service.get_session_history(uuid_session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )
    
    return SessionHistoryResponse(
        session_id=str(session.id),
        language=session.language.value,
        message_count=len(session.messages),
        is_crisis_mode=session.is_crisis_mode,
        created_at=session.created_at.isoformat(),
        messages=[msg.to_dict() for msg in session.messages],
    )
