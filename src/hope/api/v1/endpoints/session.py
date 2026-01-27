"""
Session Endpoints

Handles therapy session lifecycle and messaging.
Main interaction point for user conversations.

ARCHITECTURE: All sessions are persisted to PostgreSQL.
No in-memory storage. Crash-safe and restart-safe.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from hope.config.logging_config import get_logger
from hope.infrastructure.database import get_async_session
from hope.infrastructure.database.repositories.session_repository import SessionRepository
from hope.api.auth.dependencies import get_current_user_optional, get_token_data_optional
from hope.api.auth.service import TokenData

logger = get_logger(__name__)
router = APIRouter()


# Request/Response Models

class CreateSessionRequest(BaseModel):
    """Request to create a new session."""
    
    # user_id is now optional - derived from auth token or anonymous
    language: str = Field(default="en", description="Preferred language (en, fr, ar, de, es)")
    country_code: str = Field(default="US", description="User's country for crisis resources")


class CreateSessionResponse(BaseModel):
    """Response for session creation."""
    
    session_id: UUID
    state: str
    message: str


class SendMessageRequest(BaseModel):
    """Request to send a message in a session."""
    
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


# Endpoints

@router.post(
    "/create",
    response_model=CreateSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new therapy session",
)
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_async_session),
    token_data: Optional[TokenData] = Depends(get_token_data_optional),
) -> CreateSessionResponse:
    """
    Create a new therapy session.
    
    A session maintains conversation context and tracks
    panic events throughout the interaction.
    
    Supports both authenticated users and anonymous panic sessions.
    """
    repo = SessionRepository(db)
    
    # Get user_id from token if authenticated, generate for anonymous
    if token_data and token_data.user_id:
        user_id = token_data.user_id
    else:
        # Anonymous session - use session_id from panic token or generate new
        from uuid import uuid4
        user_id = token_data.session_id if token_data else uuid4()
    
    # Create persisted session
    session = await repo.create(
        user_id=user_id,
        state="created",
        metadata={
            "language": request.language,
            "country_code": request.country_code,
            "is_anonymous": token_data.is_anonymous if token_data else True,
        },
    )
    
    await db.commit()
    
    # Localized welcome message
    messages = {
        "en": "Session created successfully. I'm here with you.",
        "fr": "Session créée. Je suis là avec toi.",
        "ar": "تم إنشاء الجلسة. أنا هنا معك.",
        "de": "Sitzung erstellt. Ich bin bei dir.",
        "es": "Sesión creada. Estoy aquí contigo.",
    }
    
    logger.info(
        "Session created",
        session_id=str(session.id),
        user_id=str(user_id),
        is_anonymous=token_data.is_anonymous if token_data else True,
    )
    
    return CreateSessionResponse(
        session_id=session.id,
        state=session.state,
        message=messages.get(request.language, messages["en"]),
    )


@router.post(
    "/message",
    response_model=SendMessageResponse,
    summary="Send a message and receive HOPE's response",
)
async def send_message(
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_async_session),
    token_data: Optional[TokenData] = Depends(get_token_data_optional),
) -> SendMessageResponse:
    """
    Send a message in an active session.
    
    The message is processed through the complete safety pipeline:
    Detection → Decision → Prompt → LLM → Safety Validation
    
    Returns HOPE's validated response with severity classification.
    """
    repo = SessionRepository(db)
    
    # Get session
    session = await repo.get_by_id(request.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {request.session_id} not found",
        )
    
    # Verify session ownership (if authenticated)
    if token_data and token_data.user_id:
        if session.user_id != token_data.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session does not belong to this user",
            )
    
    # Check session state
    if session.state in ("completed", "abandoned"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is {session.state} and cannot receive messages",
        )
    
    # Resume paused sessions
    if session.state == "paused":
        await repo.update_state(request.session_id, "active")
    
    # Store user message
    await repo.add_message(
        session_id=request.session_id,
        role="user",
        content=request.message,
    )
    
    try:
        # Import inside function to avoid circular import
        from hope.main import get_orchestrator
        from hope.domain.models.session import Session, SessionState
        
        orchestrator = get_orchestrator()
        
        # Create domain session from database model
        domain_session = Session(
            id=session.id,
            user_id=session.user_id,
            state=SessionState(session.state),
        )
        
        # Load messages into domain session
        for msg in session.messages or []:
            domain_session.add_message(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
                metadata=msg.get("metadata", {}),
            )
        
        # Process through full pipeline
        result = await orchestrator.process(
            user_message=request.message,
            user_id=session.user_id,
            session=domain_session,
        )
        
        # Store assistant response
        await repo.add_message(
            session_id=request.session_id,
            role="assistant",
            content=result.response_text,
            metadata={
                "severity": result.detection.severity.name,
                "urgency": result.detection.urgency.value,
                "escalated": result.detection.requires_escalation,
            },
        )
        
        # Handle escalation
        if result.detection.requires_escalation:
            await repo.set_escalation(
                session_id=request.session_id,
                reason=f"Severity: {result.detection.severity.name}",
            )
        
        await db.commit()
        
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
    db: AsyncSession = Depends(get_async_session),
) -> SessionStatusResponse:
    """Get the current status of a session."""
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    
    return SessionStatusResponse(
        session_id=session.id,
        state=session.state,
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
    db: AsyncSession = Depends(get_async_session),
) -> SessionStatusResponse:
    """
    Mark a session as completed.
    
    Optionally provide a summary for the session.
    """
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    
    if session.state in ("completed", "abandoned"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session is already {session.state}",
        )
    
    await repo.complete_session(session_id, summary)
    await db.commit()
    
    # Refresh session data
    session = await repo.get_by_id(session_id)
    
    logger.info(
        "Session completed",
        session_id=str(session_id),
        message_count=session.message_count,
        duration=session.duration_seconds,
    )
    
    return SessionStatusResponse(
        session_id=session.id,
        state=session.state,
        message_count=session.message_count,
        duration_seconds=session.duration_seconds,
        created_at=session.created_at.isoformat(),
    )


@router.get(
    "/{session_id}/messages",
    summary="Get session messages",
)
async def get_session_messages(
    session_id: UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_async_session),
) -> dict:
    """
    Get messages from a session.
    
    Returns conversation history for display.
    """
    repo = SessionRepository(db)
    session = await repo.get_by_id(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found",
        )
    
    messages = await repo.get_messages(session_id, limit=limit)
    
    return {
        "session_id": str(session_id),
        "message_count": len(messages),
        "messages": messages,
    }
