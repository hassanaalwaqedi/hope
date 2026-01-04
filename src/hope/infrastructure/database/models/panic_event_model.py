"""
Panic Event Database Model

SQLAlchemy ORM model for panic event persistence.
Tracks all detected/reported panic episodes.

CLINICAL_REVIEW_REQUIRED: Data retention and analysis
policies should be reviewed clinically and legally.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hope.infrastructure.database.connection import Base


class PanicEventModel(Base):
    """
    Panic event table ORM model.
    
    Stores panic episode data including detection, intervention,
    and resolution information.
    
    Table: panic_events
    """
    
    __tablename__ = "panic_events"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Unique event identifier"
    )
    
    # Relationships
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated user ID"
    )
    session_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        doc="Associated session ID"
    )
    
    # Classification
    severity: Mapped[int] = mapped_column(
        Integer,
        default=0,
        index=True,
        doc="Panic severity level (0-4)"
    )
    urgency: Mapped[str] = mapped_column(
        String(20),
        default="routine",
        doc="Urgency level (routine, elevated, high, emergency)"
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        doc="Detection confidence (0.0-1.0)"
    )
    
    # Triggers and symptoms (stored as arrays)
    triggers: Mapped[list] = mapped_column(
        ARRAY(String(50)),
        default=list,
        doc="Identified triggers"
    )
    symptoms_reported: Mapped[list] = mapped_column(
        ARRAY(String(100)),
        default=list,
        doc="User-reported symptoms"
    )
    
    # Interventions
    interventions_provided: Mapped[list] = mapped_column(
        ARRAY(String(50)),
        default=list,
        doc="Interventions offered"
    )
    interventions_used: Mapped[list] = mapped_column(
        ARRAY(String(50)),
        default=list,
        doc="Interventions user engaged with"
    )
    
    # Resolution
    resolution_time_seconds: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Time to resolution in seconds"
    )
    user_feedback: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        doc="User feedback on interventions"
    )
    feedback_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="User satisfaction rating (1-5)"
    )
    escalated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        doc="Whether event was escalated to crisis resources"
    )
    
    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        index=True,
        doc="When panic was detected"
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="When event was resolved"
    )
    
    # Additional data
    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        doc="Additional event metadata"
    )
    
    # Relationships
    user = relationship("UserModel", back_populates="panic_events")
    session = relationship("SessionModel", back_populates="panic_events")
    
    def __repr__(self) -> str:
        return f"<PanicEventModel(id={self.id}, severity={self.severity}, escalated={self.escalated})>"
    
    @property
    def is_resolved(self) -> bool:
        """Check if event has been resolved."""
        return self.resolved_at is not None
    
    @property
    def intervention_effectiveness(self) -> float:
        """Calculate intervention effectiveness ratio."""
        if not self.interventions_provided:
            return 0.0
        return len(self.interventions_used) / len(self.interventions_provided)
