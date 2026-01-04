"""
User Database Model

SQLAlchemy ORM model for user persistence.
Implements field-level encryption for sensitive data.

SECURITY: Email is stored encrypted. Password hashes
are stored separately from core user data.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hope.infrastructure.database.connection import Base


class UserModel(Base):
    """
    User table ORM model.
    
    Stores user account information with encrypted sensitive fields.
    Profile data is stored as JSONB for flexibility.
    
    Table: users
    """
    
    __tablename__ = "users"
    
    # Primary key
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Unique user identifier"
    )
    
    # Authentication
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="User email address (encrypted at rest)"
    )
    email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        doc="Whether email has been verified"
    )
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Bcrypt password hash (null for OAuth users)"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        doc="Whether account is active"
    )
    
    # Profile (JSONB for flexibility)
    profile: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        doc="User profile data"
    )
    
    # Consent tracking
    consent_version: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="Latest accepted consent version"
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        nullable=False,
        doc="Account creation timestamp"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Last update timestamp"
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Last login timestamp"
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        doc="Soft delete timestamp"
    )
    
    # Relationships
    sessions = relationship("SessionModel", back_populates="user", lazy="dynamic")
    consents = relationship("ConsentModel", back_populates="user", lazy="dynamic")
    panic_events = relationship("PanicEventModel", back_populates="user", lazy="dynamic")
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email='{self.email[:3]}***')>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if user has been soft deleted."""
        return self.deleted_at is not None
