"""
Session Database Model

SQLAlchemy ORM model for therapy session persistence.
Messages are stored as JSONB array for efficient retrieval.

PRIVACY: Session messages may contain sensitive content
and should be encrypted at rest.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hope.infrastructure.database.connection import Base


class SessionModel(Base):
    """
    Session table ORM model.
    
    Stores therapy session data including messages and state.
    
    Table: sessions
    """
    
    __tablename__ = "sessions"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Unique session identifier"
    )
    
    # User relationship
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated user ID"
    )
    
    # Session state
    state: Mapped[str] = mapped_column(
        String(20),
        default="created",
        index=True,
        doc="Session state (created, active, paused, completed, escalated, abandoned)"
    )
    
    # Messages stored as JSONB array
    messages: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        doc="Array of session messages"
    )
    
    # Session metadata
    summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Session summary (generated after completion)"
    )
    escalation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Reason for escalation if applicable"
    )
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        doc="Additional session metadata"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        index=True,
        doc="Session start timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last activity timestamp"
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Session end timestamp"
    )
    
    # Relationships
    user = relationship("UserModel", back_populates="sessions")
    panic_events = relationship("PanicEventModel", back_populates="session", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<SessionModel(id={self.id}, user_id={self.user_id}, state='{self.state}')>"
    
    @property
    def message_count(self) -> int:
        """Get number of messages in session."""
        return len(self.messages) if self.messages else 0
    
    @property
    def duration_seconds(self) -> int:
        """Calculate session duration in seconds."""
        end = self.ended_at or datetime.utcnow()
        return int((end - self.created_at).total_seconds())
