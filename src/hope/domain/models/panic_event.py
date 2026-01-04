"""
Panic Event Domain Model

Represents panic attack events detected by the system.
Tracks episodes, triggers, interventions, and outcomes.

CLINICAL_REVIEW_REQUIRED: The classification of panic events
and trigger categories should be validated by mental health
professionals before production use.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4

from hope.domain.enums.panic_severity import PanicSeverity, UrgencyLevel


class PanicTrigger(StrEnum):
    """
    Common panic attack trigger categories.
    
    Used to help identify patterns and personalize
    intervention suggestions.
    
    CLINICAL_REVIEW_REQUIRED: This list should be
    reviewed and expanded by mental health professionals.
    """
    
    UNKNOWN = "unknown"
    """Trigger not identified or specified."""
    
    SOCIAL = "social"
    """Social situations or interactions."""
    
    HEALTH_ANXIETY = "health_anxiety"
    """Concerns about physical health or symptoms."""
    
    WORK_STRESS = "work_stress"
    """Work-related pressure or situations."""
    
    RELATIONSHIP = "relationship"
    """Interpersonal relationship concerns."""
    
    FINANCIAL = "financial"
    """Financial worries or pressures."""
    
    TRAUMA_REMINDER = "trauma_reminder"
    """
    Reminder of past traumatic experience.
    
    SAFETY_NOTE: This trigger category may indicate
    need for professional PTSD support.
    """
    
    PHYSICAL_SYMPTOMS = "physical_symptoms"
    """Physical sensation triggering panic cycle."""
    
    CAFFEINE = "caffeine"
    """Caffeine or stimulant consumption."""
    
    SLEEP_DEPRIVATION = "sleep_deprivation"
    """Lack of adequate sleep."""
    
    CROWDED_SPACE = "crowded_space"
    """Agoraphobic trigger - crowded or confined spaces."""
    
    OTHER = "other"
    """User-specified trigger not in categories."""


class PanicIntervention(StrEnum):
    """
    Types of interventions provided during panic events.
    
    Tracks what strategies were offered and used
    to help measure effectiveness.
    """
    
    GROUNDING_TECHNIQUE = "grounding_technique"
    """5-4-3-2-1 or similar sensory grounding."""
    
    BREATHING_EXERCISE = "breathing_exercise"
    """Structured breathing patterns (4-7-8, box breathing)."""
    
    COGNITIVE_REFRAME = "cognitive_reframe"
    """Thought challenging or reframing."""
    
    PROGRESSIVE_RELAXATION = "progressive_relaxation"
    """Body-based relaxation technique."""
    
    VALIDATION = "validation"
    """Emotional validation and normalization."""
    
    DISTRACTION = "distraction"
    """Attention redirection activities."""
    
    CRISIS_RESOURCES = "crisis_resources"
    """
    Emergency/crisis resource provision.
    
    SAFETY_NOTE: This should always be offered
    at CRITICAL severity levels.
    """
    
    PROFESSIONAL_REFERRAL = "professional_referral"
    """Recommendation to seek professional help."""


@dataclass
class PanicEvent:
    """
    Panic event record.
    
    Tracks a detected or reported panic episode including
    severity, triggers, interventions used, and outcome.
    
    Attributes:
        id: Unique event identifier
        user_id: Associated user ID
        session_id: Associated session ID (if applicable)
        detected_at: When panic was detected
        severity: Classified severity level
        urgency: Response urgency level
        confidence_score: Detection confidence (0.0-1.0)
        triggers: Identified triggers
        symptoms_reported: User-reported symptoms
        interventions_provided: Interventions offered
        interventions_used: Interventions user engaged with
        resolution_time_seconds: Time to resolution (if resolved)
        user_feedback: User feedback on interventions
        escalated: Whether event was escalated to crisis
        resolved_at: When event was considered resolved
        metadata: Additional event data
    """
    
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    session_id: Optional[UUID] = None
    detected_at: datetime = field(default_factory=datetime.utcnow)
    
    # Classification
    severity: PanicSeverity = PanicSeverity.NONE
    urgency: UrgencyLevel = UrgencyLevel.ROUTINE
    confidence_score: float = 0.0
    
    # Triggers and symptoms
    triggers: list[PanicTrigger] = field(default_factory=list)
    symptoms_reported: list[str] = field(default_factory=list)
    
    # Interventions
    interventions_provided: list[PanicIntervention] = field(default_factory=list)
    interventions_used: list[PanicIntervention] = field(default_factory=list)
    
    # Resolution
    resolution_time_seconds: Optional[int] = None
    user_feedback: Optional[str] = None
    feedback_rating: Optional[int] = None  # 1-5 scale
    escalated: bool = False
    resolved_at: Optional[datetime] = None
    
    # Additional context
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate and compute derived fields."""
        # Ensure urgency matches severity
        if self.urgency == UrgencyLevel.ROUTINE and self.severity >= PanicSeverity.MODERATE:
            self.urgency = UrgencyLevel.from_severity(self.severity)
        
        # Validate confidence score
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError(f"Confidence score must be 0.0-1.0, got {self.confidence_score}")
    
    def add_trigger(self, trigger: PanicTrigger) -> None:
        """Add an identified trigger."""
        if trigger not in self.triggers:
            self.triggers.append(trigger)
    
    def add_intervention(self, intervention: PanicIntervention, used: bool = False) -> None:
        """
        Record an intervention.
        
        Args:
            intervention: The intervention type
            used: Whether user engaged with the intervention
        """
        if intervention not in self.interventions_provided:
            self.interventions_provided.append(intervention)
        if used and intervention not in self.interventions_used:
            self.interventions_used.append(intervention)
    
    def resolve(self, feedback: Optional[str] = None, rating: Optional[int] = None) -> None:
        """
        Mark event as resolved.
        
        Args:
            feedback: Optional user feedback
            rating: Optional satisfaction rating (1-5)
        """
        self.resolved_at = datetime.utcnow()
        self.resolution_time_seconds = int(
            (self.resolved_at - self.detected_at).total_seconds()
        )
        self.user_feedback = feedback
        if rating is not None and 1 <= rating <= 5:
            self.feedback_rating = rating
    
    def escalate(self) -> None:
        """
        Mark event as escalated to crisis resources.
        
        SAFETY_NOTE: This should trigger immediate
        provision of crisis hotline and professional resources.
        """
        self.escalated = True
        if PanicIntervention.CRISIS_RESOURCES not in self.interventions_provided:
            self.interventions_provided.append(PanicIntervention.CRISIS_RESOURCES)
    
    @property
    def is_resolved(self) -> bool:
        """Check if event has been resolved."""
        return self.resolved_at is not None
    
    @property
    def is_critical(self) -> bool:
        """Check if event is at critical severity."""
        return self.severity >= PanicSeverity.SEVERE
    
    @property
    def intervention_effectiveness(self) -> float:
        """
        Calculate intervention effectiveness ratio.
        
        Returns:
            Ratio of interventions used vs provided (0.0-1.0)
        """
        if not self.interventions_provided:
            return 0.0
        return len(self.interventions_used) / len(self.interventions_provided)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "session_id": str(self.session_id) if self.session_id else None,
            "detected_at": self.detected_at.isoformat(),
            "severity": self.severity.name,
            "urgency": self.urgency.value,
            "confidence_score": self.confidence_score,
            "triggers": [t.value for t in self.triggers],
            "symptoms_reported": self.symptoms_reported,
            "interventions_provided": [i.value for i in self.interventions_provided],
            "interventions_used": [i.value for i in self.interventions_used],
            "resolution_time_seconds": self.resolution_time_seconds,
            "escalated": self.escalated,
            "is_resolved": self.is_resolved,
            "feedback_rating": self.feedback_rating,
        }
