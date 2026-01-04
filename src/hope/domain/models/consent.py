"""
Consent Domain Model

Manages user consent for data collection and processing.
Supports versioned consent with full audit trail.

LEGAL_REVIEW_REQUIRED: Consent text and versioning should
be reviewed by legal team for compliance with GDPR, HIPAA,
and other applicable regulations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4


class ConsentType(StrEnum):
    """
    Types of consent collected from users.
    
    Each type represents a distinct consent scope
    that can be granted or revoked independently.
    """
    
    TERMS_OF_SERVICE = "terms_of_service"
    """Agreement to platform terms and conditions."""
    
    PRIVACY_POLICY = "privacy_policy"
    """Acknowledgment of privacy practices."""
    
    DATA_PROCESSING = "data_processing"
    """
    Consent for processing personal data.
    
    REQUIRED for core functionality.
    """
    
    EMOTIONAL_HISTORY = "emotional_history"
    """
    Consent to store emotional state history.
    
    Enables personalized responses based on
    past interactions and patterns.
    """
    
    ANALYTICS = "analytics"
    """
    Consent for anonymous usage analytics.
    
    OPTIONAL - does not affect core functionality.
    """
    
    RESEARCH = "research"
    """
    Consent for anonymized data to be used in research.
    
    OPTIONAL - explicit opt-in required.
    
    ETHICAL_REVIEW_REQUIRED: Research consent must
    include clear explanation of data use and
    anonymization procedures.
    """


@dataclass
class ConsentVersion:
    """
    A specific version of consent text.
    
    Consent documents are versioned to track changes
    and ensure users have agreed to current terms.
    
    Attributes:
        version: Semantic version string (e.g., "1.0.0")
        consent_type: Type of consent this version applies to
        effective_date: When this version becomes active
        document_hash: SHA-256 hash of consent document
        summary: Brief description of changes from previous version
    """
    
    version: str
    consent_type: ConsentType
    effective_date: datetime
    document_hash: str
    summary: str = ""
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "version": self.version,
            "consent_type": self.consent_type.value,
            "effective_date": self.effective_date.isoformat(),
            "document_hash": self.document_hash,
            "summary": self.summary,
        }


@dataclass
class Consent:
    """
    User consent record.
    
    Tracks a user's consent decisions with full audit trail.
    Supports granular consent for different data types.
    
    Attributes:
        id: Unique consent record identifier
        user_id: Associated user ID
        consent_type: Type of consent
        version: Consent document version
        granted: Whether consent was granted
        granted_at: When consent was granted/revoked
        ip_address: IP address at time of consent (optional)
        user_agent: User agent string (optional)
        revoked_at: When consent was revoked (if applicable)
        revocation_reason: User-provided reason for revocation
    """
    
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    consent_type: ConsentType = ConsentType.TERMS_OF_SERVICE
    version: str = "1.0.0"
    granted: bool = False
    granted_at: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    
    @property
    def is_active(self) -> bool:
        """Check if consent is currently active (granted and not revoked)."""
        return self.granted and self.revoked_at is None
    
    def revoke(self, reason: Optional[str] = None) -> None:
        """
        Revoke this consent.
        
        Args:
            reason: Optional reason for revocation
            
        Note: Revocation is permanent and creates a new record.
        The original consent record is preserved for audit.
        """
        self.revoked_at = datetime.utcnow()
        self.revocation_reason = reason
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "consent_type": self.consent_type.value,
            "version": self.version,
            "granted": self.granted,
            "granted_at": self.granted_at.isoformat(),
            "is_active": self.is_active,
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
        }


# Required consent types for core functionality
REQUIRED_CONSENTS: frozenset[ConsentType] = frozenset({
    ConsentType.TERMS_OF_SERVICE,
    ConsentType.PRIVACY_POLICY,
    ConsentType.DATA_PROCESSING,
})


def check_required_consents(consents: list[Consent]) -> tuple[bool, list[ConsentType]]:
    """
    Check if all required consents are active.
    
    Args:
        consents: List of user's consent records
        
    Returns:
        Tuple of (all_granted, missing_types)
    """
    active_types = {c.consent_type for c in consents if c.is_active}
    missing = [ct for ct in REQUIRED_CONSENTS if ct not in active_types]
    return len(missing) == 0, missing
