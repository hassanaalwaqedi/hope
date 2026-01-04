"""
HOPE Domain Layer

Core business entities and value objects.
These models represent the domain logic independent of infrastructure.
"""

from hope.domain.models.user import User, UserProfile
from hope.domain.models.session import Session, SessionState, SessionMessage
from hope.domain.models.consent import Consent, ConsentType, ConsentVersion
from hope.domain.models.panic_event import PanicEvent, PanicTrigger, PanicIntervention
from hope.domain.models.emotional_context import EmotionalContext, EmotionalState
from hope.domain.enums.panic_severity import PanicSeverity, UrgencyLevel

__all__ = [
    # User
    "User",
    "UserProfile",
    # Session
    "Session",
    "SessionState",
    "SessionMessage",
    # Consent
    "Consent",
    "ConsentType",
    "ConsentVersion",
    # Panic Event
    "PanicEvent",
    "PanicTrigger",
    "PanicIntervention",
    # Emotional Context
    "EmotionalContext",
    "EmotionalState",
    # Enums
    "PanicSeverity",
    "UrgencyLevel",
]
