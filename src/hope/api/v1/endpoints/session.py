"""
Session Endpoints

Handles therapy session lifecycle and messaging.
Main interaction point for user conversations.
"""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from hope.config.logging_config import get_logger
from hope.infrastructure.database import get_async_session
from hope.domain.models.session import Session, SessionState

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models

class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    
    user_id: UUID = Field(..., description="User ID to create session for")


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    
    session_id: UUID
    state: str
    message: str


class SendMessageRequest(BaseModel):
    """Request to send a message in a session."""
    
    user_id: UUID = Field(..., description="User ID")
    session_id: UUID = Field(..., description="Session ID")
    message: str = Field(..., min_length=1, max_length=4000, description="User message")


class SendMessageResponse(BaseModel):
    """Response with HOPE's reply."""
    
    session_id: UUID
    response: str
    severity: str
    urgency: str
    was_escalated: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "response": "I hear you, and I'm here with you...",
                "severity": "MODERATE",
                "urgency": "high",
                "was_escalated": False,
            }
        }


class SessionStatusResponse(BaseModel):
    """Session status information."""
    
    session_id: UUID
    state: str
    message_count: int
    duration_seconds: int
    created_at: str


# In-memory session storage (for demo - production uses database)
# TODO: Replace with database persistence
_sessions: dict[UUID, Session] = {}


def get_session(session_id: UUID) -> Session:
    """Get session by ID or raise 404."""
    session = _sessions.get(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    return session


@router.post(
    "/create",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new therapy session",
)
async def create_session(
    request: CreateSessionRequest,
) -> CreateSessionResponse:
    """
    Create a new therapy session for a user.
    
    A session maintains conversation context and tracks
    panic events throughout the interaction.
    """
    session = Session(
        user_id=request.user_id,
        state=SessionState.CREATED,
    )
    
    _sessions[session.id] = session
    
    logger.info(
        "Session created",
        session_id=str(session.id),
        user_id=str(request.user_id),
    )
    
    return CreateSessionResponse(
        session_id=session.id,
        state=session.state.value,
        message="Session created successfully. Send a message to begin.",
    )


@router.post(
    "/message",
    response_model=SendMessageResponse,
    summary="Send a message and receive HOPE's response",
)
async def send_message(
    request: SendMessageRequest,
) -> SendMessageResponse:
    """
    Send a message in an active session.
    
    The message is processed through the complete safety pipeline:
    Detection → Decision → Prompt → LLM → Safety Validation
    
    Returns HOPE's validated response with severity classification.
    """
    session = get_session(request.session_id)
    
    # Verify session belongs to user
    if session.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not belong to this user",
        )
    
    # Check session state
    if session.state in (SessionState.COMPLETED, SessionState.ABANDONED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is {session.state.value} and cannot receive messages",
        )
    
    # Resume paused sessions
    if session.state == SessionState.PAUSED:
        session.resume()
    
    try:
        # Import inside function to avoid circular import
        from hope.main import get_orchestrator
        orchestrator = get_orchestrator()
        
        # Process through full pipeline
        result = await orchestrator.process(
            user_message=request.message,
            user_id=request.user_id,
            session=session,
        )
        
        logger.info(
            "Message processed",
            session_id=str(session.id),
            severity=result.detection.severity.name,
        )
        
        return SendMessageResponse(
            session_id=session.id,
            response=result.response_text,
            severity=result.detection.severity.name,
            urgency=result.detection.urgency.value,
            was_escalated=result.detection.requires_escalation,
        )
        
    except Exception as e:
        logger.error(
            "Message processing failed",
            session_id=str(session.id),
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message. Please try again.",
        )


@router.get(
    "/{session_id}",
    response_model=SessionStatusResponse,
    summary="Get session status",
)
async def get_session_status(
    session_id: UUID,
) -> SessionStatusResponse:
    """Get the current status of a session."""
    session = get_session(session_id)
    
    return SessionStatusResponse(
        session_id=session.id,
        state=session.state.value,
        message_count=session.message_count,
        duration_seconds=session.duration_seconds,
        created_at=session.created_at.isoformat(),
    )


@router.post(
    "/{session_id}/complete",
    response_model=SessionStatusResponse,
    summary="Complete a session",
)
async def complete_session(
    session_id: UUID,
    summary: Optional[str] = None,
) -> SessionStatusResponse:
    """
    Mark a session as completed.
    
    Optionally provide a summary for the session.
    """
    session = get_session(session_id)
    
    if session.state in (SessionState.COMPLETED, SessionState.ABANDONED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is already {session.state.value}",
        )
    
    session.complete(summary=summary)
    
    logger.info(
        "Session completed",
        session_id=str(session_id),
        message_count=session.message_count,
        duration=session.duration_seconds,
    )
    
    return SessionStatusResponse(
        session_id=session.id,
        state=session.state.value,
        message_count=session.message_count,
        duration_seconds=session.duration_seconds,
        created_at=session.created_at.isoformat(),
    )
