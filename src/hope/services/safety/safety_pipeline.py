"""
Safety Pipeline

Orchestrates all safety components into a unified pipeline.
This is the main entry point for safety evaluation.

ARCHITECTURE: The safety pipeline consumes ClinicalAssessment
and produces SafetyEvaluation with risk scoring, crisis detection,
escalation decisions, and response validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID

from hope.domain.models.clinical_output import ClinicalAssessment
from hope.domain.models.risk_models import (
    RiskLevel,
    RiskAssessment,
    EscalationEvent,
)
from hope.services.safety.risk_engine import RiskScoringEngine, RiskThresholds
from hope.services.safety.crisis_detector import (
    CrisisDetector,
    CrisisDetectionResult,
    LinguisticCrisisAnalyzer,
)
from hope.services.safety.escalation_manager import (
    EscalationManager,
    EscalationDecision,
)
from hope.services.safety.emergency_resources import EmergencyResourceResolver
from hope.services.safety.safety_validator import SafetyValidator, SafetyResult
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SafetyEvaluation:
    """
    Complete safety evaluation result.
    
    Combines all safety checks into a single result
    for the response pipeline.
    
    Attributes:
        evaluation_id: Unique identifier
        timestamp: When evaluation was performed
        
        risk_assessment: Risk scoring result
        crisis_detection: Crisis signal detection result
        escalation_decision: Escalation decision made
        
        final_risk_level: Determined risk level
        requires_crisis_response: Whether crisis response needed
        requires_human_review: Whether human should review
        
        response_valid: Whether AI response passed validation
        response_was_modified: Whether response was modified
        final_response: The final safe response
        
        audit_trail: Complete audit data
    """
    
    evaluation_id: UUID = field(default_factory=lambda: UUID(int=0))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Component results
    risk_assessment: Optional[RiskAssessment] = None
    crisis_detection: Optional[CrisisDetectionResult] = None
    escalation_decision: Optional[EscalationDecision] = None
    
    # Final determinations
    final_risk_level: RiskLevel = RiskLevel.LOW
    requires_crisis_response: bool = False
    requires_human_review: bool = False
    
    # Response handling
    response_valid: bool = True
    response_was_modified: bool = False
    final_response: str = ""
    
    # Audit
    audit_trail: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "evaluation_id": str(self.evaluation_id),
            "timestamp": self.timestamp.isoformat(),
            "risk_level": self.final_risk_level.name,
            "requires_crisis_response": self.requires_crisis_response,
            "requires_human_review": self.requires_human_review,
            "response_valid": self.response_valid,
            "response_was_modified": self.response_was_modified,
        }


class SafetyPipeline:
    """
    Unified safety evaluation pipeline.
    
    Orchestrates:
    1. Risk scoring (from clinical assessment)
    2. Crisis detection
    3. Escalation management
    4. Response validation
    
    ARCHITECTURE: This pipeline is the FINAL authority on
    response safety. It can modify or block any response.
    
    Usage:
        pipeline = SafetyPipeline()
        evaluation = pipeline.evaluate(
            clinical_assessment=assessment,
            proposed_response="I understand...",
            country_code="US",
        )
        safe_response = evaluation.final_response
    """
    
    def __init__(
        self,
        risk_thresholds: Optional[RiskThresholds] = None,
        strict_mode: bool = True,
    ) -> None:
        """
        Initialize safety pipeline.
        
        Args:
            risk_thresholds: Risk scoring thresholds
            strict_mode: If True, any violation blocks response
        """
        self._risk_engine = RiskScoringEngine(risk_thresholds)
        self._crisis_detector = CrisisDetector()
        self._escalation_manager = EscalationManager()
        self._response_validator = SafetyValidator(strict_mode)
        
        # Track previous risk for escalation detection
        self._session_risk_cache: dict[UUID, RiskLevel] = {}
    
    def evaluate(
        self,
        clinical: ClinicalAssessment,
        proposed_response: str,
        country_code: str = "US",
        raw_text: Optional[str] = None,
    ) -> SafetyEvaluation:
        """
        Perform complete safety evaluation.
        
        Args:
            clinical: Clinical assessment from Phase 2
            proposed_response: AI-generated response to validate
            country_code: User's country for resources
            raw_text: Optional raw text for additional checks
            
        Returns:
            SafetyEvaluation with final safe response
        """
        from uuid import uuid4
        
        evaluation_id = uuid4()
        audit = {
            "evaluation_id": str(evaluation_id),
            "timestamp": datetime.utcnow().isoformat(),
            "clinical_assessment_id": str(clinical.assessment_id),
        }
        
        # Step 1: Risk scoring
        risk_assessment = self._risk_engine.assess(clinical)
        audit["risk_score"] = round(risk_assessment.risk_score, 3)
        audit["risk_level"] = risk_assessment.risk_level.name
        
        # Step 2: Crisis detection
        crisis_result = self._crisis_detector.detect(clinical)
        audit["crisis_signals"] = len(crisis_result.signals)
        audit["multi_signal_met"] = crisis_result.meets_multi_signal_requirement
        
        # Step 3: Merge crisis signals into risk
        if crisis_result.has_crisis_signals:
            # Add crisis signals to risk assessment
            crisis_signals = crisis_result.to_risk_signals()
            risk_assessment.signals.extend(crisis_signals)
            
            # Potentially upgrade risk level if multi-signal met
            if crisis_result.meets_multi_signal_requirement:
                if risk_assessment.risk_level < RiskLevel.HIGH:
                    risk_assessment.risk_level = RiskLevel.HIGH
                    audit["risk_upgraded_by_crisis"] = True
        
        # Step 4: Get previous risk level for session
        previous_level = None
        if clinical.session_id:
            previous_level = self._session_risk_cache.get(clinical.session_id)
            self._session_risk_cache[clinical.session_id] = risk_assessment.risk_level
        
        # Step 5: Escalation decision
        escalation = self._escalation_manager.evaluate(
            risk=risk_assessment,
            country_code=country_code,
            previous_level=previous_level,
        )
        audit["escalated"] = escalation.should_escalate
        
        # Step 6: Linguistic crisis check (additional safety layer)
        if raw_text:
            linguistic_signals = LinguisticCrisisAnalyzer.analyze_text(raw_text)
            if linguistic_signals:
                audit["linguistic_crisis_signals"] = len(linguistic_signals)
                # If linguistic signals found but not in crisis mode, flag for review
                if not escalation.should_escalate and len(linguistic_signals) >= 2:
                    risk_assessment.requires_human_review = True
                    audit["flagged_for_review"] = True
        
        # Step 7: Validate proposed response
        is_crisis_response = risk_assessment.risk_level >= RiskLevel.HIGH
        validation = self._response_validator.validate(
            response=proposed_response,
            is_crisis_response=is_crisis_response,
        )
        audit["response_blocked"] = validation.blocked
        audit["response_modified"] = validation.was_modified
        
        # Step 8: Build final response
        if validation.blocked:
            # Use fallback response and add resources
            final_response = self._escalation_manager.modify_response(
                response=validation.filtered_response,
                decision=escalation,
                country_code=country_code,
            )
        else:
            # Use validated response (possibly modified)
            final_response = self._escalation_manager.modify_response(
                response=validation.filtered_response,
                decision=escalation,
                country_code=country_code,
            )
        
        # Step 9: Determine final states
        requires_crisis = (
            risk_assessment.risk_level >= RiskLevel.CRITICAL or
            clinical.requires_crisis_protocol or
            crisis_result.meets_multi_signal_requirement
        )
        
        requires_review = (
            risk_assessment.requires_human_review or
            escalation.log_event is not None
        )
        
        evaluation = SafetyEvaluation(
            evaluation_id=evaluation_id,
            risk_assessment=risk_assessment,
            crisis_detection=crisis_result,
            escalation_decision=escalation,
            final_risk_level=risk_assessment.risk_level,
            requires_crisis_response=requires_crisis,
            requires_human_review=requires_review,
            response_valid=validation.is_safe,
            response_was_modified=validation.was_modified or escalation.should_escalate,
            final_response=final_response,
            audit_trail=audit,
        )
        
        logger.info(
            "Safety evaluation complete",
            risk_level=risk_assessment.risk_level.name,
            crisis_response=requires_crisis,
            response_modified=evaluation.response_was_modified,
        )
        
        return evaluation
    
    def validate_response_only(
        self,
        response: str,
        is_crisis_response: bool = False,
    ) -> SafetyResult:
        """
        Validate a response without full pipeline.
        
        Use for quick response checking.
        """
        return self._response_validator.validate(response, is_crisis_response)
    
    def get_escalation_events(
        self,
        session_id: UUID,
    ) -> list[EscalationEvent]:
        """Get escalation events for a session."""
        return self._escalation_manager.get_events(session_id=session_id)
