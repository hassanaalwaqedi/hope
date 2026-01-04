"""
User Domain Model

Represents a user in the HOPE system with privacy-first design.
Personal data is separated from behavioral data to support
data minimization principles.

SECURITY: Email and profile data should be encrypted at rest 
in the database layer.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class UserProfile:
    """
    Optional user profile information.
    
    All fields are optional to support progressive profiling.
    Users can use the system without providing personal details.
    
    PRIVACY: This data is encrypted at rest and should only
    be accessed when necessary for personalization.
    """
    
    display_name: Optional[str] = None
    """User-chosen display name (not required to be real name)."""
    
    timezone: Optional[str] = None
    """User's timezone for scheduling and context."""
    
    preferred_language: str = "en"
    """ISO 639-1 language code for localization."""
    
    onboarding_completed: bool = False
    """Whether user has completed initial onboarding."""
    
    # CLINICAL_REVIEW_REQUIRED: Determine what additional profile
    # fields are clinically relevant without being invasive
    
    def to_dict(self) -> dict:
        """Serialize profile to dictionary."""
        return {
            "display_name": self.display_name,
            "timezone": self.timezone,
            "preferred_language": self.preferred_language,
            "onboarding_completed": self.onboarding_completed,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        """Create profile from dictionary."""
        return cls(
            display_name=data.get("display_name"),
            timezone=data.get("timezone"),
            preferred_language=data.get("preferred_language", "en"),
            onboarding_completed=data.get("onboarding_completed", False),
        )


@dataclass
class User:
    """
    Core user entity.
    
    Represents an authenticated user in the HOPE system.
    Designed for minimal data collection while supporting
    necessary functionality.
    
    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address (encrypted at rest)
        email_verified: Whether email has been verified
        is_active: Whether user account is active
        profile: Optional profile information
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login_at: Last login timestamp
        consent_version: Latest consent version accepted
    """
    
    id: UUID = field(default_factory=uuid4)
    email: str = ""
    email_verified: bool = False
    is_active: bool = True
    profile: UserProfile = field(default_factory=UserProfile)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    consent_version: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate user data after initialization."""
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Invalid email format: {self.email}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email format validation."""
        # Note: More thorough validation should happen at API layer
        return "@" in email and "." in email.split("@")[-1]
    
    def has_valid_consent(self, required_version: str) -> bool:
        """
        Check if user has accepted required consent version.
        
        Args:
            required_version: Minimum required consent version
            
        Returns:
            True if user's consent is current
        """
        if not self.consent_version:
            return False
        # Version comparison (semantic versioning)
        return self.consent_version >= required_version
    
    def update_login(self) -> None:
        """Record login timestamp."""
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Serialize user to dictionary.
        
        Note: Does not include password hash - that's handled
        separately in authentication layer.
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "email_verified": self.email_verified,
            "is_active": self.is_active,
            "profile": self.profile.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "consent_version": self.consent_version,
        }
