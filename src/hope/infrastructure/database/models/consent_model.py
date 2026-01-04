"""
Consent Database Model

SQLAlchemy ORM model for consent record persistence.
Maintains full audit trail of consent decisions.

LEGAL_REVIEW_REQUIRED: Data retention policies for consent
records should be reviewed for compliance.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hope.infrastructure.database.connection import Base


class ConsentModel(Base):
    """
    Consent table ORM model.
    
    Stores user consent records with versioning and
    full audit trail for legal compliance.
    
    Table: consents
    """
    
    __tablename__ = "consents"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Unique consent record identifier"
    )
    
    # User relationship
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated user ID"
    )
    
    # Consent details
    consent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Type of consent (terms_of_service, privacy_policy, data_processing, etc.)"
    )
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Consent document version"
    )
    granted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        doc="Whether consent was granted"
    )
    
    # Audit information
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # Supports IPv6
        nullable=True,
        doc="IP address at time of consent"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User agent string at time of consent"
    )
    
    # Timestamps
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        doc="When consent was granted"
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="When consent was revoked (if applicable)"
    )
    revocation_reason: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User-provided reason for revocation"
    )
    
    # Relationships
    user = relationship("UserModel", back_populates="consents")
    
    # Composite index for efficient queries
    __table_args__ = (
        # Index for finding active consents by user and type
        # Defined in migration for more control
    )
    
    def __repr__(self) -> str:
        return f"<ConsentModel(id={self.id}, type='{self.consent_type}', granted={self.granted})>"
    
    @property
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        return self.granted and self.revoked_at is None
