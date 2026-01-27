"""
User Preferences API Endpoints

Handles user settings sync and GDPR data operations.
Endpoints:
- GET/PUT /user/preferences - Sync settings across devices
- GET /user/export - Export all user data (GDPR)
- DELETE /user/data - Delete all user data (right to erasure)
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from hope.config.logging_config import get_logger
from hope.infrastructure.database import get_async_session
from hope.infrastructure.database.models.session_model import SessionModel
from hope.infrastructure.database.models.panic_event_model import PanicEventModel
from hope.api.auth.dependencies import get_current_user_required
from hope.infrastructure.database.models.user_model import UserModel

logger = get_logger(__name__)
router = APIRouter()


class UserPreferences(BaseModel):
    """User preferences stored in backend."""
    
    voice_guidance: bool = Field(default=False)
    haptic_feedback: bool = Field(default=True)
    breathing_speed: str = Field(default="normal")
    daily_check_in: bool = Field(default=True)
    theme_preference: str = Field(default="system")
    analytics_enabled: bool = Field(default=True)
    consent_version: Optional[str] = None
    consent_date: Optional[datetime] = None
    terms_version: Optional[str] = None
    terms_accepted_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class DataExportResponse(BaseModel):
    """GDPR data export response."""
    
    export_date: datetime
    sessions: list
    panic_events: list
    preferences: Optional[dict] = None


class DataDeletionResponse(BaseModel):
    """GDPR data deletion response."""
    
    success: bool
    deleted_sessions: int
    deleted_messages: int
    deleted_panic_events: int


@router.get("/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: UserModel = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_async_session),
) -> UserPreferences:
    """
    Get user preferences.
    
    Returns saved preferences or defaults if none saved.
    """
    # Get from user profile or return defaults
    if current_user.profile and isinstance(current_user.profile, dict):
        prefs = current_user.profile.get("preferences", {})
        return UserPreferences(**prefs)
    
    return UserPreferences()


@router.put("/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: UserModel = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_async_session),
) -> UserPreferences:
    """
    Update user preferences.
    
    Syncs preferences from mobile app to backend.
    """
    # Update user profile with preferences
    if current_user.profile is None:
        current_user.profile = {}
    
    current_user.profile["preferences"] = preferences.model_dump()
    
    await db.commit()
    
    logger.info(
        "User preferences updated",
        user_id=str(current_user.id),
    )
    
    return preferences


@router.get("/export", response_model=DataExportResponse)
async def export_user_data(
    current_user: UserModel = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_async_session),
) -> DataExportResponse:
    """
    Export all user data (GDPR compliance).
    
    Returns:
    - All chat sessions
    - All panic events
    - User preferences
    
    No internal IDs are included.
    """
    # Get all sessions
    sessions_result = await db.execute(
        select(SessionModel).where(SessionModel.user_id == current_user.id)
    )
    sessions = sessions_result.scalars().all()
    
    # Get all panic events
    panic_result = await db.execute(
        select(PanicEventModel).where(PanicEventModel.user_id == current_user.id)
    )
    panic_events = panic_result.scalars().all()
    
    # Format for export (redact internal IDs)
    export_sessions = []
    for session in sessions:
        export_sessions.append({
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "state": session.state,
            "message_count": len(session.messages) if session.messages else 0,
            "messages": [
                {
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "timestamp": msg.get("timestamp"),
                }
                for msg in (session.messages or [])
            ],
        })
    
    export_panic = []
    for event in panic_events:
        export_panic.append({
            "detected_at": event.detected_at.isoformat() if event.detected_at else None,
            "resolved_at": event.resolved_at.isoformat() if event.resolved_at else None,
            "severity": event.severity,
            "interventions_used": event.interventions,
        })
    
    # Get preferences
    prefs = None
    if current_user.profile and isinstance(current_user.profile, dict):
        prefs = current_user.profile.get("preferences")
    
    logger.info(
        "User data exported",
        user_id=str(current_user.id),
        sessions=len(export_sessions),
        panic_events=len(export_panic),
    )
    
    return DataExportResponse(
        export_date=datetime.utcnow(),
        sessions=export_sessions,
        panic_events=export_panic,
        preferences=prefs,
    )


@router.delete("/data", response_model=DataDeletionResponse)
async def delete_user_data(
    current_user: UserModel = Depends(get_current_user_required),
    db: AsyncSession = Depends(get_async_session),
) -> DataDeletionResponse:
    """
    Delete all user data (GDPR right to erasure).
    
    This is IRREVERSIBLE.
    
    Deletes:
    - All chat sessions and messages
    - All panic events
    - Clears user preferences
    """
    # Count before deletion
    sessions_result = await db.execute(
        select(SessionModel).where(SessionModel.user_id == current_user.id)
    )
    sessions = sessions_result.scalars().all()
    session_count = len(sessions)
    message_count = sum(len(s.messages) if s.messages else 0 for s in sessions)
    
    panic_result = await db.execute(
        select(PanicEventModel).where(PanicEventModel.user_id == current_user.id)
    )
    panic_count = len(panic_result.scalars().all())
    
    # Delete sessions
    await db.execute(
        delete(SessionModel).where(SessionModel.user_id == current_user.id)
    )
    
    # Delete panic events
    await db.execute(
        delete(PanicEventModel).where(PanicEventModel.user_id == current_user.id)
    )
    
    # Clear preferences
    if current_user.profile:
        current_user.profile["preferences"] = {}
    
    await db.commit()
    
    logger.info(
        "User data deleted (GDPR erasure)",
        user_id=str(current_user.id),
        sessions=session_count,
        messages=message_count,
        panic_events=panic_count,
    )
    
    return DataDeletionResponse(
        success=True,
        deleted_sessions=session_count,
        deleted_messages=message_count,
        deleted_panic_events=panic_count,
    )
