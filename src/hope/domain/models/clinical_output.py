"""
Clinical Output Contract

Defines the strict, typed data structure that is the ONLY input
allowed to the Decision Engine. This ensures all clinical analysis
passes through validated, structured output.

ARCHITECTURE: This module defines the contract between the
Clinical Intelligence Layer and the Decision Engine.

CLINICAL_VALIDATION_REQUIRED: All thresholds, classifications,
and interpretive boundaries require psychologist review.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from hope.domain.enums.panic_severity import PanicSeverity, UrgencyLevel


class EmotionCategory(StrEnum):
    """
    Clinical emotion categories relevant to panic attacks.
    
    These categories are specifically chosen for panic/anxiety
    assessment, not general emotion detection.
    
    CLINICAL_VALIDATION_REQUIRED: Category definitions and
    clinical significance need psychologist input.
    """
    
    FEAR = "fear"
    """Acute fear response, fight-or-flight activation."""
    
    DREAD = "dread"
    """Anticipatory anxiety, sense of impending doom."""
    
    LOSS_OF_CONTROL = "loss_of_control"
    """Feeling unable to control thoughts, body, or situation."""
    
    DISSOCIATION = "dissociation"
    """Derealization, depersonalization, feeling disconnected."""
    
    HELPLESSNESS = "helplessness"
    """Feeling unable to cope or change the situation."""
    
    HYPERVIGILANCE = "hypervigilance"
    """Heightened alertness, scanning for threats."""
    
    SHAME = "shame"
    """Self-directed negative emotions about the panic."""
    
    CONFUSION = "confusion"
    """Cognitive disorientation, racing thoughts."""


class DistressType(StrEnum):
    """Types of distress indicators."""
    
    PHYSIOLOGICAL = "physiological"
    """Physical symptoms: heart racing, breathing difficulty, etc."""
    
    COGNITIVE = "cognitive"
    """Thought patterns: catastrophizing, rumination, etc."""
    
    BEHAVIORAL = "behavioral"
    """Actions: avoidance, freezing, escape behaviors."""
    
    EMOTIONAL = "emotional"
    """Emotional state: overwhelm, numbness, etc."""


@dataclass
class EmotionScore:
    """
    Single emotion classification with confidence.
    
    Attributes:
        category: Emotion category
        confidence: ML confidence score (0.0-1.0)
        intensity: Estimated intensity (0.0-1.0)
        is_primary: Whether this is the dominant emotion
    """
    
    category: EmotionCategory
    confidence: float
    intensity: float = 0.0
    is_primary: bool = False
    
    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "confidence": round(self.confidence, 3),
            "intensity": round(self.intensity, 3),
            "is_primary": self.is_primary,
        }


@dataclass
class EmotionProfile:
    """
    Complete emotion analysis profile.
    
    Multi-label emotion classification with confidence scores.
    Designed to capture the complex emotional state during panic.
    
    Attributes:
        emotions: List of detected emotions with scores
        dominant_emotion: Primary detected emotion
        emotional_volatility: Measure of emotional instability (0.0-1.0)
        timestamp: When analysis was performed
    """
    
    emotions: list[EmotionScore] = field(default_factory=list)
    dominant_emotion: Optional[EmotionCategory] = None
    emotional_volatility: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self) -> None:
        # Set dominant emotion from highest confidence if not set
        if not self.dominant_emotion and self.emotions:
            primary = max(self.emotions, key=lambda e: e.confidence)
            self.dominant_emotion = primary.category
            primary.is_primary = True
    
    def get_emotion_score(self, category: EmotionCategory) -> float:
        """Get confidence score for a specific emotion."""
        for emotion in self.emotions:
            if emotion.category == category:
                return emotion.confidence
        return 0.0
    
    def has_high_confidence(self, threshold: float = 0.7) -> bool:
        """Check if any emotion has high confidence."""
        return any(e.confidence >= threshold for e in self.emotions)
    
    def to_dict(self) -> dict:
        return {
            "emotions": [e.to_dict() for e in self.emotions],
            "dominant_emotion": self.dominant_emotion.value if self.dominant_emotion else None,
            "emotional_volatility": round(self.emotional_volatility, 3),
        }


@dataclass
class DistressIndicator:
    """
    Single distress indicator with clinical context.
    
    Attributes:
        indicator_type: Type of distress
        description: What was detected
        severity: Indicator severity (0.0-1.0)
        source_text: Text that triggered detection
        clinical_notes: Notes for clinical review
    """
    
    indicator_type: DistressType
    description: str
    severity: float
    source_text: str = ""
    clinical_notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            "type": self.indicator_type.value,
            "description": self.description,
            "severity": round(self.severity, 3),
        }


@dataclass
class DistressIndicators:
    """
    Collection of distress indicators by type.
    
    Separates physiological, cognitive, behavioral, and
    emotional indicators for structured analysis.
    
    Attributes:
        physiological: Physical symptom indicators
        cognitive: Thought pattern indicators
        behavioral: Behavioral indicators
        emotional: Emotional state indicators
        overall_distress_level: Combined distress score
    """
    
    physiological: list[DistressIndicator] = field(default_factory=list)
    cognitive: list[DistressIndicator] = field(default_factory=list)
    behavioral: list[DistressIndicator] = field(default_factory=list)
    emotional: list[DistressIndicator] = field(default_factory=list)
    overall_distress_level: float = 0.0
    
    def all_indicators(self) -> list[DistressIndicator]:
        """Get all indicators as flat list."""
        return self.physiological + self.cognitive + self.behavioral + self.emotional
    
    def indicator_count(self) -> int:
        """Total number of detected indicators."""
        return len(self.all_indicators())
    
    def highest_severity(self) -> float:
        """Get highest severity among all indicators."""
        all_ind = self.all_indicators()
        if not all_ind:
            return 0.0
        return max(ind.severity for ind in all_ind)
    
    def to_dict(self) -> dict:
        return {
            "physiological": [i.to_dict() for i in self.physiological],
            "cognitive": [i.to_dict() for i in self.cognitive],
            "behavioral": [i.to_dict() for i in self.behavioral],
            "emotional": [i.to_dict() for i in self.emotional],
            "overall_distress_level": round(self.overall_distress_level, 3),
            "indicator_count": self.indicator_count(),
        }


@dataclass
class SeverityClassification:
    """
    Probabilistic severity classification.
    
    Contains class probabilities for each severity level,
    not just a single classification.
    
    Attributes:
        predicted_severity: Most likely severity level
        probabilities: Probability for each severity class
        confidence: Confidence in prediction
        uncertainty_flag: True if prediction is uncertain
        model_version: Version of classifier model
    """
    
    predicted_severity: PanicSeverity
    probabilities: dict[PanicSeverity, float] = field(default_factory=dict)
    confidence: float = 0.0
    uncertainty_flag: bool = False
    model_version: str = "1.0.0"
    
    def __post_init__(self) -> None:
        # Flag uncertainty if confidence is low or probabilities are close
        if self.confidence < 0.6:
            self.uncertainty_flag = True
        elif self.probabilities:
            sorted_probs = sorted(self.probabilities.values(), reverse=True)
            if len(sorted_probs) >= 2:
                # If top two are close, flag uncertainty
                if sorted_probs[0] - sorted_probs[1] < 0.15:
                    self.uncertainty_flag = True
    
    def get_probability(self, severity: PanicSeverity) -> float:
        """Get probability for specific severity level."""
        return self.probabilities.get(severity, 0.0)
    
    def to_dict(self) -> dict:
        return {
            "predicted_severity": self.predicted_severity.name,
            "probabilities": {k.name: round(v, 3) for k, v in self.probabilities.items()},
            "confidence": round(self.confidence, 3),
            "uncertainty_flag": self.uncertainty_flag,
            "model_version": self.model_version,
        }


@dataclass
class TriggerAnalysis:
    """
    Trigger pattern analysis results.
    
    Attributes:
        immediate_triggers: Triggers detected in current message
        historical_triggers: Recurring triggers from history
        temporal_patterns: Time-based patterns (e.g., morning anxiety)
        context_factors: Environmental/situational factors
    """
    
    immediate_triggers: list[str] = field(default_factory=list)
    historical_triggers: list[str] = field(default_factory=list)
    temporal_patterns: list[str] = field(default_factory=list)
    context_factors: list[str] = field(default_factory=list)
    
    def all_triggers(self) -> list[str]:
        """Get all unique triggers."""
        return list(set(
            self.immediate_triggers + 
            self.historical_triggers
        ))
    
    def to_dict(self) -> dict:
        return {
            "immediate": self.immediate_triggers,
            "historical": self.historical_triggers,
            "temporal_patterns": self.temporal_patterns,
            "context_factors": self.context_factors,
        }


@dataclass
class ClinicalAssessment:
    """
    THE CLINICAL OUTPUT CONTRACT
    
    This is the ONLY data structure that may be passed to the
    Decision Engine. All clinical analysis must flow through
    this structured output.
    
    ARCHITECTURE: This contract enforces separation between
    the Clinical Intelligence Layer and the Decision Engine.
    The Decision Engine must NEVER access raw text or ML outputs
    directly.
    
    Attributes:
        assessment_id: Unique identifier for this assessment
        user_id: User being assessed
        session_id: Current session (if applicable)
        message_id: Message that triggered assessment
        timestamp: When assessment was generated
        
        severity: Probabilistic severity classification
        emotion_profile: Multi-label emotion analysis
        distress_indicators: Structured distress markers
        trigger_analysis: Trigger pattern analysis
        urgency: Response urgency level
        
        requires_crisis_protocol: Whether to activate crisis response
        requires_human_review: Whether human review is recommended
        confidence_score: Overall assessment confidence
        uncertainty_flags: List of uncertainty reasons
        
        raw_text_hash: Hash of input (for audit, not analysis)
        model_versions: Versions of models used
    """
    
    # Identifiers
    assessment_id: UUID = field(default_factory=uuid4)
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    message_id: Optional[UUID] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Core clinical outputs
    severity: SeverityClassification = field(
        default_factory=lambda: SeverityClassification(PanicSeverity.NONE)
    )
    emotion_profile: EmotionProfile = field(default_factory=EmotionProfile)
    distress_indicators: DistressIndicators = field(default_factory=DistressIndicators)
    trigger_analysis: TriggerAnalysis = field(default_factory=TriggerAnalysis)
    urgency: UrgencyLevel = UrgencyLevel.ROUTINE
    
    # Safety flags
    requires_crisis_protocol: bool = False
    requires_human_review: bool = False
    
    # Confidence and uncertainty
    confidence_score: float = 0.0
    uncertainty_flags: list[str] = field(default_factory=list)
    
    # Audit trail
    raw_text_hash: str = ""
    model_versions: dict[str, str] = field(default_factory=dict)
    embeddings: Optional[list[float]] = None
    
    def __post_init__(self) -> None:
        # Auto-set crisis protocol for critical severity
        if self.severity.predicted_severity >= PanicSeverity.CRITICAL:
            self.requires_crisis_protocol = True
        
        # Auto-set urgency from severity
        self.urgency = UrgencyLevel.from_severity(self.severity.predicted_severity)
        
        # Flag for human review if uncertain
        if self.severity.uncertainty_flag:
            self.requires_human_review = True
            if "severity_uncertainty" not in self.uncertainty_flags:
                self.uncertainty_flags.append("severity_uncertainty")
    
    def is_panic_detected(self) -> bool:
        """Check if panic is detected."""
        return self.severity.predicted_severity > PanicSeverity.NONE
    
    def get_primary_emotion(self) -> Optional[EmotionCategory]:
        """Get primary detected emotion."""
        return self.emotion_profile.dominant_emotion
    
    def to_dict(self) -> dict:
        """Serialize for logging/storage."""
        return {
            "assessment_id": str(self.assessment_id),
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.to_dict(),
            "emotion_profile": self.emotion_profile.to_dict(),
            "distress_indicators": self.distress_indicators.to_dict(),
            "trigger_analysis": self.trigger_analysis.to_dict(),
            "urgency": self.urgency.value,
            "requires_crisis_protocol": self.requires_crisis_protocol,
            "requires_human_review": self.requires_human_review,
            "confidence_score": round(self.confidence_score, 3),
            "uncertainty_flags": self.uncertainty_flags,
        }
    
    def to_audit_record(self) -> dict:
        """Create audit record for compliance."""
        return {
            "assessment_id": str(self.assessment_id),
            "user_id": str(self.user_id) if self.user_id else None,
            "session_id": str(self.session_id) if self.session_id else None,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity.predicted_severity.name,
            "urgency": self.urgency.value,
            "crisis_protocol": self.requires_crisis_protocol,
            "human_review": self.requires_human_review,
            "raw_text_hash": self.raw_text_hash,
            "model_versions": self.model_versions,
        }
