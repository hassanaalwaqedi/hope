"""
Decision Engine

Determines appropriate response strategies based on CLINICAL ASSESSMENT.

ARCHITECTURE: This engine accepts ONLY ClinicalAssessment as input.
This enforces the contract between clinical analysis and decision making.
No raw text or intermediate ML outputs are allowed here.

CLINICAL_REVIEW_REQUIRED: Decision rules and intervention mappings
require clinical validation before production deployment.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Optional, Union
from uuid import UUID

from hope.domain.enums.panic_severity import PanicSeverity, UrgencyLevel
from hope.domain.models.panic_event import PanicIntervention, PanicTrigger
from hope.domain.models.clinical_output import (
    ClinicalAssessment,
    EmotionCategory,
)
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


class ResponseStrategy(StrEnum):
    """
    High-level response strategy types.
    
    Guides prompt construction and intervention selection.
    """
    
    CHECK_IN = "check_in"
    """Standard check-in for no detected panic."""
    
    ACKNOWLEDGE = "acknowledge"
    """Acknowledge mild distress, offer support."""
    
    GROUND = "ground"
    """Active grounding and breathing techniques."""
    
    INTERVENE = "intervene"
    """Direct intervention for severe panic."""
    
    CRISIS = "crisis"
    """Emergency response with resources."""


class ResponseTone(StrEnum):
    """
    Communication tone for responses.
    """
    
    WARM = "warm"
    """Warm, conversational tone."""
    
    CALM = "calm"
    """Calm, steady, reassuring tone."""
    
    DIRECT = "direct"
    """Clear, direct, no-nonsense tone."""
    
    URGENT = "urgent"
    """Urgent but not alarming tone."""


@dataclass
class DecisionContext:
    """
    Context for decision making.
    
    Provides clinical assessment and environmental context
    to inform response decisions.
    
    ARCHITECTURE: The clinical_assessment is the ONLY source of
    clinical information. No raw text or intermediate outputs.
    
    Attributes:
        user_id: Current user ID
        session_id: Current session ID
        clinical_assessment: Clinical assessment (REQUIRED)
        session_message_count: Messages in current session
        previous_panic_count: Historical panic events (24h)
        last_intervention_used: Last intervention that helped
        user_preferences: User-stated preferences
    """
    
    user_id: UUID
    clinical_assessment: ClinicalAssessment  # REQUIRED - enforces contract
    session_id: Optional[UUID] = None
    session_message_count: int = 0
    previous_panic_count: int = 0
    last_intervention_used: Optional[str] = None
    user_preferences: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "user_id": str(self.user_id),
            "session_id": str(self.session_id) if self.session_id else None,
            "severity": self.clinical_assessment.severity.predicted_severity.name,
            "session_message_count": self.session_message_count,
            "previous_panic_count": self.previous_panic_count,
            "last_intervention_used": self.last_intervention_used,
        }


@dataclass
class Decision:
    """
    Decision output from the engine.
    
    Contains strategy, interventions, and constraints
    for response generation.
    
    Attributes:
        strategy: High-level response strategy
        tone: Communication tone
        primary_intervention: Main intervention to offer
        secondary_interventions: Additional options
        response_constraints: Hard constraints on response
        prompt_modifiers: Modifications for prompt building
        escalate_to_crisis: Whether to provide crisis resources
        require_consent_check: Whether to verify consent
    """
    
    strategy: ResponseStrategy
    tone: ResponseTone
    primary_intervention: Optional[PanicIntervention] = None
    secondary_interventions: list[PanicIntervention] = field(default_factory=list)
    response_constraints: list[str] = field(default_factory=list)
    prompt_modifiers: dict = field(default_factory=dict)
    escalate_to_crisis: bool = False
    require_consent_check: bool = False
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "strategy": self.strategy.value,
            "tone": self.tone.value,
            "primary_intervention": self.primary_intervention.value if self.primary_intervention else None,
            "escalate_to_crisis": self.escalate_to_crisis,
        }


class DecisionEngine:
    """
    Decision engine for response strategy selection.
    
    Uses rule-based logic with extensibility for ML-based
    optimization within safe bounds.
    
    Core Safety Rules (non-negotiable):
    1. Crisis indicators ALWAYS trigger crisis response
    2. Severe panic ALWAYS gets intervention
    3. NEVER provide medical advice
    4. ALWAYS offer professional resources at high severity
    
    CLINICAL_REVIEW_REQUIRED: All decision rules need clinical validation.
    """
    
    # Intervention mappings by severity
    # CLINICAL_REVIEW_REQUIRED
    SEVERITY_INTERVENTIONS: dict[PanicSeverity, list[PanicIntervention]] = {
        PanicSeverity.NONE: [],
        PanicSeverity.MILD: [
            PanicIntervention.VALIDATION,
            PanicIntervention.BREATHING_EXERCISE,
        ],
        PanicSeverity.MODERATE: [
            PanicIntervention.BREATHING_EXERCISE,
            PanicIntervention.GROUNDING_TECHNIQUE,
            PanicIntervention.VALIDATION,
        ],
        PanicSeverity.SEVERE: [
            PanicIntervention.GROUNDING_TECHNIQUE,
            PanicIntervention.BREATHING_EXERCISE,
            PanicIntervention.PROGRESSIVE_RELAXATION,
            PanicIntervention.PROFESSIONAL_REFERRAL,
        ],
        PanicSeverity.CRITICAL: [
            PanicIntervention.CRISIS_RESOURCES,
            PanicIntervention.GROUNDING_TECHNIQUE,
            PanicIntervention.PROFESSIONAL_REFERRAL,
        ],
    }
    
    # Strategy mappings
    SEVERITY_STRATEGY: dict[PanicSeverity, ResponseStrategy] = {
        PanicSeverity.NONE: ResponseStrategy.CHECK_IN,
        PanicSeverity.MILD: ResponseStrategy.ACKNOWLEDGE,
        PanicSeverity.MODERATE: ResponseStrategy.GROUND,
        PanicSeverity.SEVERE: ResponseStrategy.INTERVENE,
        PanicSeverity.CRITICAL: ResponseStrategy.CRISIS,
    }
    
    # Tone mappings
    SEVERITY_TONE: dict[PanicSeverity, ResponseTone] = {
        PanicSeverity.NONE: ResponseTone.WARM,
        PanicSeverity.MILD: ResponseTone.WARM,
        PanicSeverity.MODERATE: ResponseTone.CALM,
        PanicSeverity.SEVERE: ResponseTone.CALM,
        PanicSeverity.CRITICAL: ResponseTone.DIRECT,
    }
    
    # Universal response constraints
    UNIVERSAL_CONSTRAINTS: list[str] = [
        "NEVER provide medical diagnosis",
        "NEVER prescribe medication or dosages",
        "NEVER claim to be a replacement for professional help",
        "NEVER minimize user's experience",
        "ALWAYS validate user's feelings",
        "ALWAYS use trauma-informed language",
    ]
    
    def __init__(self) -> None:
        """Initialize decision engine."""
        self._custom_rules: list = []
    
    def decide(self, context: DecisionContext) -> Decision:
        """
        Make a decision based on clinical assessment.
        
        ARCHITECTURE: This method accepts ONLY ClinicalAssessment
        through the DecisionContext. No raw text access.
        
        Args:
            context: Decision context with clinical assessment
            
        Returns:
            Decision with strategy and interventions
        """
        assessment = context.clinical_assessment
        severity = assessment.severity.predicted_severity
        
        # Rule 1: Crisis protocol ALWAYS escalates
        if assessment.requires_crisis_protocol:
            return self._crisis_decision(context)
        
        # Rule 2: Select strategy based on severity
        strategy = self.SEVERITY_STRATEGY[severity]
        tone = self.SEVERITY_TONE[severity]
        
        # Rule 3: Adjust tone based on emotion profile
        tone = self._adjust_tone_for_emotions(tone, assessment)
        
        # Rule 4: Select interventions based on triggers
        triggers = [
            PanicTrigger.UNKNOWN  # Base trigger
        ]
        for trigger in assessment.trigger_analysis.immediate_triggers:
            try:
                triggers.append(PanicTrigger(trigger))
            except ValueError:
                pass
        
        interventions = self._select_interventions(
            severity,
            context.last_intervention_used,
            triggers,
        )
        
        primary = interventions[0] if interventions else None
        secondary = interventions[1:] if len(interventions) > 1 else []
        
        # Rule 5: Build constraints
        constraints = self._build_constraints(severity)
        
        # Rule 6: Build prompt modifiers from clinical assessment
        modifiers = self._build_clinical_modifiers(context)
        
        # Rule 7: Determine if professional referral needed
        escalate = severity >= PanicSeverity.SEVERE
        
        # Rule 8: Flag for human review if uncertain
        require_consent = assessment.requires_human_review
        
        decision = Decision(
            strategy=strategy,
            tone=tone,
            primary_intervention=primary,
            secondary_interventions=secondary,
            response_constraints=constraints,
            prompt_modifiers=modifiers,
            escalate_to_crisis=escalate,
            require_consent_check=require_consent,
        )
        
        logger.debug(
            "Decision made from clinical assessment",
            strategy=strategy.value,
            severity=severity.name,
            confidence=round(assessment.confidence_score, 3),
        )
        
        return decision
    
    def _adjust_tone_for_emotions(
        self,
        base_tone: ResponseTone,
        assessment: ClinicalAssessment,
    ) -> ResponseTone:
        """
        Adjust communication tone based on emotion profile.
        
        CLINICAL_REVIEW_REQUIRED: Tone adjustments need validation.
        """
        emotion_profile = assessment.emotion_profile
        
        if not emotion_profile.dominant_emotion:
            return base_tone
        
        # Dissociation requires more grounded, direct communication
        if emotion_profile.dominant_emotion == EmotionCategory.DISSOCIATION:
            return ResponseTone.DIRECT
        
        # Loss of control benefits from calm reassurance
        if emotion_profile.dominant_emotion == EmotionCategory.LOSS_OF_CONTROL:
            return ResponseTone.CALM
        
        # High volatility needs steady tone
        if emotion_profile.emotional_volatility > 0.7:
            return ResponseTone.CALM
        
        return base_tone
    
    def _build_clinical_modifiers(
        self,
        context: DecisionContext,
    ) -> dict:
        """Build prompt modifiers from clinical assessment."""
        assessment = context.clinical_assessment
        
        modifiers = {
            "severity_level": assessment.severity.predicted_severity.name,
            "confidence_score": assessment.confidence_score,
            "session_message_count": context.session_message_count,
            "is_recurring": context.previous_panic_count > 0,
        }
        
        # Include emotion context
        if assessment.emotion_profile.dominant_emotion:
            modifiers["dominant_emotion"] = assessment.emotion_profile.dominant_emotion.value
        
        # Include trigger context
        if assessment.trigger_analysis.immediate_triggers:
            modifiers["triggers"] = assessment.trigger_analysis.immediate_triggers
        
        # Include distress level
        modifiers["distress_level"] = assessment.distress_indicators.overall_distress_level
        
        # Note uncertainty
        if assessment.uncertainty_flags:
            modifiers["has_uncertainty"] = True
        
        return modifiers
    
    def _default_decision(self) -> Decision:
        """Create default decision for no detection."""
        return Decision(
            strategy=ResponseStrategy.CHECK_IN,
            tone=ResponseTone.WARM,
            response_constraints=self.UNIVERSAL_CONSTRAINTS,
        )
    
    def _crisis_decision(self, context: DecisionContext) -> Decision:
        """
        Create crisis-level decision.
        
        SAFETY_CRITICAL: This decision path is for emergencies.
        Always provides crisis resources.
        """
        logger.warning(
            "Crisis decision triggered",
            user_id=str(context.user_id),
        )
        
        return Decision(
            strategy=ResponseStrategy.CRISIS,
            tone=ResponseTone.DIRECT,
            primary_intervention=PanicIntervention.CRISIS_RESOURCES,
            secondary_interventions=[
                PanicIntervention.GROUNDING_TECHNIQUE,
                PanicIntervention.PROFESSIONAL_REFERRAL,
            ],
            response_constraints=[
                *self.UNIVERSAL_CONSTRAINTS,
                "MUST provide crisis hotline number",
                "MUST recommend immediate professional help",
                "Response MUST be clear and actionable",
            ],
            prompt_modifiers={
                "include_crisis_hotline": True,
                "include_emergency_grounding": True,
            },
            escalate_to_crisis=True,
        )
    
    def _select_interventions(
        self,
        severity: PanicSeverity,
        last_intervention: Optional[str],
        triggers: list[PanicTrigger],
    ) -> list[PanicIntervention]:
        """
        Select appropriate interventions.
        
        Considers severity, what worked before, and triggers.
        
        Args:
            severity: Panic severity
            last_intervention: Last intervention that helped
            triggers: Detected triggers
            
        Returns:
            Ordered list of interventions
        """
        base_interventions = list(self.SEVERITY_INTERVENTIONS.get(severity, []))
        
        # Prioritize last successful intervention
        if last_intervention:
            try:
                last = PanicIntervention(last_intervention)
                if last in base_interventions:
                    base_interventions.remove(last)
                    base_interventions.insert(0, last)
            except ValueError:
                pass
        
        # Adjust based on triggers
        # CLINICAL_REVIEW_REQUIRED: Trigger-intervention mappings
        if PanicTrigger.HEALTH_ANXIETY in triggers:
            # Grounding over breathing for health anxiety
            # (breathing focus can increase symptom awareness)
            if PanicIntervention.GROUNDING_TECHNIQUE in base_interventions:
                base_interventions.remove(PanicIntervention.GROUNDING_TECHNIQUE)
                base_interventions.insert(0, PanicIntervention.GROUNDING_TECHNIQUE)
        
        return base_interventions
    
    def _build_constraints(self, severity: PanicSeverity) -> list[str]:
        """Build response constraints based on severity."""
        constraints = list(self.UNIVERSAL_CONSTRAINTS)
        
        if severity >= PanicSeverity.MODERATE:
            constraints.append("Keep response focused and concise")
            constraints.append("Avoid lengthy explanations during crisis")
        
        if severity >= PanicSeverity.SEVERE:
            constraints.append("Include option for professional help")
            constraints.append("Use simple, clear language")
        
        return constraints
