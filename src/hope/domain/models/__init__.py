"""Domain models package."""

from hope.domain.models.user import User, UserProfile
from hope.domain.models.session import Session, SessionState, SessionMessage
from hope.domain.models.consent import Consent, ConsentType, ConsentVersion
from hope.domain.models.panic_event import PanicEvent, PanicTrigger, PanicIntervention
from hope.domain.models.emotional_context import EmotionalContext, EmotionalState
from hope.domain.models.clinical_output import (
    ClinicalAssessment,
    SeverityClassification,
    EmotionProfile,
    EmotionScore,
    EmotionCategory,
    DistressIndicators,
    DistressIndicator,
    DistressType,
    TriggerAnalysis,
)
from hope.domain.models.session_metrics import (
    SessionMetrics,
    IntensityDataPoint,
    InterventionRecord,
)

__all__ = [
    # User models
    "User",
    "UserProfile",
    # Session models
    "Session",
    "SessionState",
    "SessionMessage",
    # Consent models
    "Consent",
    "ConsentType",
    "ConsentVersion",
    # Panic event models
    "PanicEvent",
    "PanicTrigger",
    "PanicIntervention",
    # Emotional context
    "EmotionalContext",
    "EmotionalState",
    # Clinical output contract (Phase 2)
    "ClinicalAssessment",
    "SeverityClassification",
    "EmotionProfile",
    "EmotionScore",
    "EmotionCategory",
    "DistressIndicators",
    "DistressIndicator",
    "DistressType",
    "TriggerAnalysis",
    # Session metrics (Phase 2)
    "SessionMetrics",
    "IntensityDataPoint",
    "InterventionRecord",
]

