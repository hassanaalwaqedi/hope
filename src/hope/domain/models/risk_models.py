"""
Risk Models

Data models for risk assessment, escalation, and safety management.

SAFETY-CRITICAL: This module defines the risk classification system.
All definitions require clinical and legal review.

ARCHITECTURE: Risk models are used exclusively by the safety layer.
They consume ClinicalAssessment and produce escalation decisions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Optional
from uuid import UUID, uuid4


class RiskLevel(IntEnum):
    """
    Risk level classification.
    
    Higher values indicate higher risk requiring more
    immediate intervention.
    
    LEGAL_REVIEW_REQUIRED: Risk level definitions and their
    associated actions have legal and clinical implications.
    """
    
    LOW = 1
    """
    Low risk - Standard supportive interaction.
    - User appears stable
    - No concerning patterns
    - Routine check-in appropriate
    """
    
    ELEVATED = 2
    """
    Elevated risk - Enhanced monitoring needed.
    - Some concerning signals present
    - May benefit from additional support
    - Encourage self-care and coping strategies
    """
    
    HIGH = 3
    """
    High risk - Active intervention required.
    - Multiple concerning signals
    - User may be in distress
    - Strongly encourage professional help
    - Provide crisis resources proactively
    """
    
    CRITICAL = 4
    """
    Critical risk - Immediate safety concern.
    - Active crisis indicators
    - Potential self-harm risk
    - MUST provide emergency resources
    - MUST recommend immediate professional help
    
    SAFETY_NOTE: At this level, every response MUST include
    crisis resources and professional referral.
    """


class EscalationAction(StrEnum):
    """
    Actions taken during escalation.
    """
    
    CONTINUE_SUPPORT = "continue_support"
    """Continue AI-based supportive conversation."""
    
    ENCOURAGE_HELP = "encourage_help"
    """Strongly encourage seeking human/professional help."""
    
    PRESENT_RESOURCES = "present_resources"
    """Present emergency/crisis resources."""
    
    LOG_FOR_REVIEW = "log_for_review"
    """Log event for future human review."""
    
    # Future actions (not implemented)
    # NOTIFY_EMERGENCY_CONTACT = "notify_emergency_contact"
    # ALERT_CLINICAL_TEAM = "alert_clinical_team"


class RiskSignalType(StrEnum):
    """
    Types of signals contributing to risk assessment.
    """
    
    LINGUISTIC = "linguistic"
    """Language patterns suggesting risk."""
    
    EMOTIONAL = "emotional"
    """Emotional state indicators."""
    
    BEHAVIORAL = "behavioral"
    """Behavioral patterns (escalation, etc.)."""
    
    HISTORICAL = "historical"
    """Historical patterns from past sessions."""
    
    CONTEXTUAL = "contextual"
    """Contextual factors (time, triggers, etc.)."""


@dataclass
class RiskSignal:
    """
    A single risk signal detected by the system.
    
    SAFETY_NOTE: No single signal should trigger escalation.
    Signals must be combined for risk assessment.
    
    Attributes:
        signal_type: Type of signal
        signal_name: Identifier for the signal
        description: Human-readable description
        weight: How much this signal contributes to risk
        confidence: Confidence in this signal (0.0-1.0)
        source: What detected this signal
    """
    
    signal_type: RiskSignalType
    signal_name: str
    description: str
    weight: float
    confidence: float = 1.0
    source: str = "unknown"
    
    def weighted_contribution(self) -> float:
        """Calculate weighted contribution to risk score."""
        return self.weight * self.confidence
    
    def to_dict(self) -> dict:
        return {
            "type": self.signal_type.value,
            "name": self.signal_name,
            "description": self.description,
            "weight": round(self.weight, 3),
            "confidence": round(self.confidence, 3),
        }


@dataclass
class RiskAssessment:
    """
    Complete risk assessment result.
    
    Combines multiple signals into a probabilistic risk score
    with confidence and uncertainty handling.
    
    ARCHITECTURE: This is the output of the RiskScoringEngine.
    It is used by the EscalationManager to make decisions.
    
    Attributes:
        assessment_id: Unique identifier
        user_id: User being assessed
        session_id: Current session
        timestamp: When assessment was made
        
        risk_level: Classified risk level
        risk_score: Numeric risk score (0.0-1.0)
        confidence: Confidence in assessment (0.0-1.0)
        
        signals: Contributing risk signals
        signal_count: Number of signals detected
        
        has_uncertainty: Whether assessment is uncertain
        uncertainty_reasons: Reasons for uncertainty
        
        recommended_actions: Suggested escalation actions
        requires_human_review: Whether human should review
    """
    
    assessment_id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Risk classification
    risk_level: RiskLevel = RiskLevel.LOW
    risk_score: float = 0.0
    confidence: float = 0.0
    
    # Contributing signals
    signals: list[RiskSignal] = field(default_factory=list)
    signal_count: int = 0
    
    # Uncertainty
    has_uncertainty: bool = False
    uncertainty_reasons: list[str] = field(default_factory=list)
    
    # Recommendations
    recommended_actions: list[EscalationAction] = field(default_factory=list)
    requires_human_review: bool = False
    
    # Thresholds used (for audit)
    thresholds_applied: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        self.signal_count = len(self.signals)
        
        # Auto-flag for human review at critical level
        if self.risk_level >= RiskLevel.CRITICAL:
            self.requires_human_review = True
        
        # Flag uncertainty for low confidence
        if self.confidence < 0.6:
            self.has_uncertainty = True
            if "low_confidence" not in self.uncertainty_reasons:
                self.uncertainty_reasons.append("low_confidence")
    
    def get_signal_types(self) -> list[RiskSignalType]:
        """Get unique signal types present."""
        return list(set(s.signal_type for s in self.signals))
    
    def has_multiple_signal_types(self) -> bool:
        """Check if multiple signal types are present."""
        return len(self.get_signal_types()) >= 2
    
    def to_dict(self) -> dict:
        return {
            "assessment_id": str(self.assessment_id),
            "timestamp": self.timestamp.isoformat(),
            "risk_level": self.risk_level.name,
            "risk_score": round(self.risk_score, 3),
            "confidence": round(self.confidence, 3),
            "signal_count": self.signal_count,
            "has_uncertainty": self.has_uncertainty,
            "requires_human_review": self.requires_human_review,
            "recommended_actions": [a.value for a in self.recommended_actions],
        }
    
    def to_audit_record(self) -> dict:
        """Create detailed audit record."""
        return {
            "assessment_id": str(self.assessment_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "session_id": str(self.session_id) if self.session_id else None,
            "timestamp": self.timestamp.isoformat(),
            "risk_level": self.risk_level.name,
            "risk_score": round(self.risk_score, 3),
            "confidence": round(self.confidence, 3),
            "signals": [s.to_dict() for s in self.signals],
            "uncertainty_reasons": self.uncertainty_reasons,
            "thresholds_applied": self.thresholds_applied,
            "recommended_actions": [a.value for a in self.recommended_actions],
        }


@dataclass
class EscalationEvent:
    """
    Record of an escalation event.
    
    Used for audit trail and future human review.
    
    LEGAL_REVIEW_REQUIRED: Retention and access policies
    for escalation records need legal review.
    
    Attributes:
        event_id: Unique identifier
        user_id: User involved
        session_id: Session where escalation occurred
        timestamp: When escalation happened
        
        risk_assessment: Risk assessment that triggered escalation
        previous_risk_level: Risk level before escalation
        new_risk_level: Risk level after escalation
        
        actions_taken: What actions were taken
        resources_provided: Emergency resources shown
        
        ai_response_given: What the AI responded with
        human_review_status: Whether human has reviewed
    """
    
    event_id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Risk context
    risk_assessment_id: Optional[UUID] = None
    previous_risk_level: RiskLevel = RiskLevel.LOW
    new_risk_level: RiskLevel = RiskLevel.LOW
    
    # Actions
    actions_taken: list[EscalationAction] = field(default_factory=list)
    resources_provided: list[str] = field(default_factory=list)
    
    # Response tracking
    ai_response_given: str = ""
    response_was_modified: bool = False
    
    # Review status
    human_review_status: str = "pending"  # pending, reviewed, acknowledged
    human_reviewer_id: Optional[str] = None
    review_timestamp: Optional[datetime] = None
    review_notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            "event_id": str(self.event_id),
            "timestamp": self.timestamp.isoformat(),
            "previous_risk_level": self.previous_risk_level.name,
            "new_risk_level": self.new_risk_level.name,
            "actions_taken": [a.value for a in self.actions_taken],
            "human_review_status": self.human_review_status,
        }
    
    def to_audit_record(self) -> dict:
        """Create complete audit record for compliance."""
        return {
            "event_id": str(self.event_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "session_id": str(self.session_id) if self.session_id else None,
            "timestamp": self.timestamp.isoformat(),
            "risk_assessment_id": str(self.risk_assessment_id) if self.risk_assessment_id else None,
            "previous_risk_level": self.previous_risk_level.name,
            "new_risk_level": self.new_risk_level.name,
            "actions_taken": [a.value for a in self.actions_taken],
            "resources_provided": self.resources_provided,
            "response_was_modified": self.response_was_modified,
            "human_review_status": self.human_review_status,
            "human_reviewer_id": self.human_reviewer_id,
            "review_timestamp": self.review_timestamp.isoformat() if self.review_timestamp else None,
        }
