"""
Escalation Manager

Manages escalation decisions and actions based on risk assessment.
Implements three-tier escalation levels.

SAFETY-CRITICAL: This module controls how the system responds
to high-risk situations. All logic requires clinical review.

ARCHITECTURE: Escalation decisions are made here, but NEVER
instruct users to take specific medical actions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from hope.domain.models.risk_models import (
    RiskLevel,
    RiskAssessment,
    EscalationAction,
    EscalationEvent,
)
from hope.services.safety.emergency_resources import (
    EmergencyResourceResolver,
    JurisdictionResources,
)
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class EscalationDecision:
    """
    Decision made by the escalation manager.
    
    Attributes:
        should_escalate: Whether to escalate from current state
        current_level: Current risk level
        actions: Actions to take
        response_modifications: How to modify AI response
        resources_to_include: Emergency resources to show
        log_event: Escalation event for audit
    """
    
    should_escalate: bool = False
    current_level: RiskLevel = RiskLevel.LOW
    actions: list[EscalationAction] = field(default_factory=list)
    response_modifications: dict = field(default_factory=dict)
    resources_to_include: Optional[str] = None
    log_event: Optional[EscalationEvent] = None
    
    def to_dict(self) -> dict:
        return {
            "should_escalate": self.should_escalate,
            "level": self.current_level.name,
            "actions": [a.value for a in self.actions],
            "has_resources": self.resources_to_include is not None,
        }


class EscalationManager:
    """
    Three-tier escalation management.
    
    Levels:
    1. CONTINUE_SUPPORT - Standard AI support continues
    2. ENCOURAGE_HELP - Strongly recommend professional help
    3. PRESENT_RESOURCES - Show crisis resources immediately
    
    SAFETY_CRITICAL:
    - System NEVER instructs specific medical actions
    - System NEVER attempts to replace professional help
    - At high/critical levels, ALWAYS provide resources
    
    Usage:
        manager = EscalationManager()
        decision = manager.evaluate(risk_assessment, country="US")
    """
    
    def __init__(
        self,
        resource_resolver: Optional[EmergencyResourceResolver] = None,
    ) -> None:
        """
        Initialize escalation manager.
        
        Args:
            resource_resolver: Emergency resource resolver
        """
        self._resources = resource_resolver or EmergencyResourceResolver()
        self._event_log: list[EscalationEvent] = []
    
    def evaluate(
        self,
        risk: RiskAssessment,
        country_code: str = "US",
        previous_level: Optional[RiskLevel] = None,
    ) -> EscalationDecision:
        """
        Evaluate risk and make escalation decision.
        
        Args:
            risk: Risk assessment from risk engine
            country_code: User's country for resources
            previous_level: Previous risk level (for escalation detection)
            
        Returns:
            EscalationDecision with actions and modifications
        """
        current_level = risk.risk_level
        should_escalate = False
        
        # Detect escalation from previous state
        if previous_level:
            should_escalate = current_level > previous_level
        
        # Determine actions based on level
        actions = list(risk.recommended_actions)
        
        # Build response modifications
        modifications = self._build_modifications(current_level, risk)
        
        # Get resources for high/critical levels
        resources_text = None
        if current_level >= RiskLevel.HIGH:
            resources_text = self._resources.format_crisis_message(
                country_code=country_code,
                include_emergency=(current_level >= RiskLevel.CRITICAL),
            )
        
        # Create escalation event for audit
        event = None
        if should_escalate or current_level >= RiskLevel.HIGH:
            event = self._create_event(
                risk=risk,
                previous_level=previous_level or RiskLevel.LOW,
                actions=actions,
                resources_provided=bool(resources_text),
            )
            self._event_log.append(event)
            
            logger.warning(
                "Escalation event created",
                event_id=str(event.event_id),
                previous_level=previous_level.name if previous_level else "NONE",
                new_level=current_level.name,
            )
        
        return EscalationDecision(
            should_escalate=should_escalate,
            current_level=current_level,
            actions=actions,
            response_modifications=modifications,
            resources_to_include=resources_text,
            log_event=event,
        )
    
    def _build_modifications(
        self,
        level: RiskLevel,
        risk: RiskAssessment,
    ) -> dict:
        """Build response modifications based on risk level."""
        modifications = {
            "tone": "supportive",
            "include_resources": False,
            "encourage_professional_help": False,
            "keep_brief": False,
            "crisis_mode": False,
        }
        
        if level == RiskLevel.LOW:
            modifications["tone"] = "warm"
        
        elif level == RiskLevel.ELEVATED:
            modifications["tone"] = "calm"
            modifications["encourage_professional_help"] = True
        
        elif level == RiskLevel.HIGH:
            modifications["tone"] = "calm"
            modifications["include_resources"] = True
            modifications["encourage_professional_help"] = True
            modifications["keep_brief"] = True
        
        elif level == RiskLevel.CRITICAL:
            modifications["tone"] = "direct"
            modifications["include_resources"] = True
            modifications["encourage_professional_help"] = True
            modifications["keep_brief"] = True
            modifications["crisis_mode"] = True
        
        # Add uncertainty handling
        if risk.has_uncertainty:
            modifications["acknowledge_uncertainty"] = True
        
        return modifications
    
    def _create_event(
        self,
        risk: RiskAssessment,
        previous_level: RiskLevel,
        actions: list[EscalationAction],
        resources_provided: bool,
    ) -> EscalationEvent:
        """Create escalation event for audit trail."""
        return EscalationEvent(
            user_id=risk.user_id,
            session_id=risk.session_id,
            risk_assessment_id=risk.assessment_id,
            previous_risk_level=previous_level,
            new_risk_level=risk.risk_level,
            actions_taken=actions,
            resources_provided=["crisis_message"] if resources_provided else [],
        )
    
    def get_events(
        self,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
    ) -> list[EscalationEvent]:
        """
        Get escalation events from log.
        
        Args:
            user_id: Filter by user
            session_id: Filter by session
            
        Returns:
            List of matching events
        """
        events = self._event_log
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        
        if session_id:
            events = [e for e in events if e.session_id == session_id]
        
        return events
    
    def get_response_prefix(
        self,
        level: RiskLevel,
    ) -> str:
        """
        Get appropriate response prefix for risk level.
        
        SAFETY_NOTE: Prefixes are designed to be supportive
        and non-alarming while acknowledging distress.
        """
        prefixes = {
            RiskLevel.LOW: "",
            RiskLevel.ELEVATED: (
                "I hear you, and I want you to know that what you're feeling is valid. "
            ),
            RiskLevel.HIGH: (
                "I'm really glad you're sharing this with me. "
                "What you're going through sounds incredibly difficult, "
                "and I want to make sure you have the support you need. "
            ),
            RiskLevel.CRITICAL: (
                "I hear you, and I'm concerned about what you're sharing. "
                "Your safety matters deeply. "
            ),
        }
        return prefixes.get(level, "")
    
    def get_response_suffix(
        self,
        level: RiskLevel,
        country_code: str = "US",
    ) -> str:
        """
        Get appropriate response suffix for risk level.
        
        Includes professional help encouragement and resources.
        """
        if level < RiskLevel.HIGH:
            return ""
        
        suffix_parts = []
        
        # Encourage professional help
        suffix_parts.append(
            "\n\nPlease consider reaching out to a mental health professional "
            "or someone you trust. You don't have to go through this alone."
        )
        
        # Add resources for high/critical
        if level >= RiskLevel.HIGH:
            resources = self._resources.format_crisis_message(country_code)
            suffix_parts.append(f"\n{resources}")
        
        return "".join(suffix_parts)
    
    def modify_response(
        self,
        response: str,
        decision: EscalationDecision,
        country_code: str = "US",
    ) -> str:
        """
        Modify AI response based on escalation decision.
        
        Adds prefixes, suffixes, and resources as needed.
        
        Args:
            response: Original AI response
            decision: Escalation decision
            country_code: User's country
            
        Returns:
            Modified response
        """
        level = decision.current_level
        
        # Add prefix
        prefix = self.get_response_prefix(level)
        
        # Add suffix with resources
        suffix = self.get_response_suffix(level, country_code)
        
        # Override resources if decision has specific ones
        if decision.resources_to_include:
            suffix = f"\n{decision.resources_to_include}"
        
        modified = prefix + response + suffix
        
        return modified.strip()


class HumanEscalationInterface:
    """
    Interface for future human-in-the-loop escalation.
    
    FUTURE_IMPLEMENTATION: This interface prepares for
    human intervention capabilities without implementing
    automatic outreach (which requires explicit authorization).
    
    Current capabilities:
    - Event logging for human review
    - Webhook stubs (not active)
    - Review queue management
    """
    
    def __init__(self) -> None:
        """Initialize interface."""
        self._review_queue: list[EscalationEvent] = []
        self._webhook_url: Optional[str] = None  # Not implemented
    
    def queue_for_review(
        self,
        event: EscalationEvent,
        priority: str = "normal",
    ) -> str:
        """
        Queue an escalation event for human review.
        
        Args:
            event: Event to queue
            priority: Review priority (low, normal, high, urgent)
            
        Returns:
            Queue ticket ID
        """
        ticket_id = str(uuid4())[:8]
        self._review_queue.append(event)
        
        logger.info(
            "Event queued for human review",
            ticket_id=ticket_id,
            event_id=str(event.event_id),
            priority=priority,
        )
        
        return ticket_id
    
    def get_pending_reviews(self) -> list[EscalationEvent]:
        """Get events pending human review."""
        return [
            e for e in self._review_queue
            if e.human_review_status == "pending"
        ]
    
    def mark_reviewed(
        self,
        event_id: UUID,
        reviewer_id: str,
        notes: str = "",
    ) -> bool:
        """
        Mark an event as reviewed.
        
        Args:
            event_id: Event to mark
            reviewer_id: ID of human reviewer
            notes: Review notes
            
        Returns:
            True if event found and updated
        """
        for event in self._review_queue:
            if event.event_id == event_id:
                event.human_review_status = "reviewed"
                event.human_reviewer_id = reviewer_id
                event.review_timestamp = datetime.utcnow()
                event.review_notes = notes
                return True
        return False
    
    # Future webhook methods (stubs)
    # FUTURE_IMPLEMENTATION: Requires legal review and explicit authorization
    
    # def notify_clinical_team(self, event: EscalationEvent) -> bool:
    #     """Notify clinical team of high-priority event."""
    #     raise NotImplementedError("Requires legal authorization")
    
    # def notify_emergency_contact(self, event: EscalationEvent) -> bool:
    #     """Notify user's emergency contact."""
    #     raise NotImplementedError("Requires user consent and legal authorization")
