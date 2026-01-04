"""
Response Orchestrator

Coordinates the complete response pipeline from user input to validated output.

ARCHITECTURE: This is the main orchestration layer that connects:
Detection → Decision → Prompt → LLM → Safety → Response

All user interactions flow through this orchestrator.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from hope.config import get_settings
from hope.config.logging_config import get_logger
from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.session import Session
from hope.services.detection.panic_detection_service import (
    PanicDetectionService,
    DetectionResult,
)
from hope.services.decision.decision_engine import (
    DecisionEngine,
    DecisionContext,
    Decision,
)
from hope.services.prompt.prompt_builder import PromptBuilder, BuiltPrompt
from hope.services.safety.safety_validator import SafetyValidator, SafetyResult
from hope.infrastructure.llm.provider import LLMProvider, LLMResponse, LLMProviderError
from hope.infrastructure.llm.openai_provider import OpenAIProvider
from hope.infrastructure.llm.gemini_provider import GeminiProvider

logger = get_logger(__name__)


@dataclass
class OrchestratedResponse:
    """
    Complete orchestrated response with full pipeline data.
    
    Attributes:
        response_text: Final validated response text
        detection: Detection result
        decision: Decision made
        safety_result: Safety validation result
        llm_response: Raw LLM response
        session_updated: Whether session was updated
        audit_data: Data for audit logging
    """
    
    response_text: str
    detection: DetectionResult
    decision: Decision
    safety_result: SafetyResult
    llm_response: Optional[LLMResponse] = None
    session_updated: bool = False
    audit_data: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Serialize for API response."""
        return {
            "response": self.response_text,
            "severity": self.detection.severity.name,
            "urgency": self.detection.urgency.value,
            "was_escalated": self.detection.requires_escalation,
            "was_modified_by_safety": self.safety_result.was_modified,
        }


class ResponseOrchestrator:
    """
    Main orchestrator for the HOPE response pipeline.
    
    Coordinates all services to produce safe, appropriate responses:
    
    1. Detection: Analyze input for panic indicators
    2. Decision: Determine response strategy
    3. Prompt: Build LLM prompt with constraints
    4. LLM: Generate response
    5. Safety: Validate and filter response
    6. Return: Deliver safe response
    
    SAFETY: Every response passes through the complete pipeline.
    No shortcuts bypass safety validation.
    """
    
    # Fallback response for complete failures
    FALLBACK_RESPONSE: str = (
        "I'm here with you. It seems I'm having some technical difficulties, "
        "but I want you to know that what you're feeling is valid. "
        "If you're in crisis, please reach out to the 988 Suicide & Crisis Lifeline "
        "by calling or texting 988. "
        "They can provide immediate support."
    )
    
    def __init__(
        self,
        detection_service: Optional[PanicDetectionService] = None,
        decision_engine: Optional[DecisionEngine] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        safety_validator: Optional[SafetyValidator] = None,
        primary_llm: Optional[LLMProvider] = None,
        fallback_llm: Optional[LLMProvider] = None,
    ) -> None:
        """
        Initialize orchestrator with services.
        
        Args:
            detection_service: Panic detection service
            decision_engine: Decision engine
            prompt_builder: Prompt builder
            safety_validator: Safety validator
            primary_llm: Primary LLM provider
            fallback_llm: Fallback LLM provider
        """
        self._detection = detection_service or PanicDetectionService()
        self._decision = decision_engine or DecisionEngine()
        self._prompt_builder = prompt_builder or PromptBuilder()
        self._safety = safety_validator or SafetyValidator()
        
        # Initialize LLM providers based on settings
        settings = get_settings()
        
        if primary_llm:
            self._primary_llm = primary_llm
        else:
            if settings.llm_primary_provider == "openai":
                self._primary_llm = OpenAIProvider()
            else:
                self._primary_llm = GeminiProvider()
        
        if fallback_llm:
            self._fallback_llm = fallback_llm
        else:
            # Use alternate provider as fallback
            if settings.llm_primary_provider == "openai":
                self._fallback_llm = GeminiProvider()
            else:
                self._fallback_llm = OpenAIProvider()
    
    async def initialize(self) -> None:
        """
        Initialize all services.
        
        Should be called during application startup.
        """
        logger.info("Initializing response orchestrator")
        await self._detection.load_models()
        logger.info("Response orchestrator initialized")
    
    async def shutdown(self) -> None:
        """
        Shutdown all services.
        
        Should be called during application shutdown.
        """
        logger.info("Shutting down response orchestrator")
        await self._detection.unload_models()
    
    async def process(
        self,
        user_message: str,
        user_id: UUID,
        session: Optional[Session] = None,
        include_embeddings: bool = True,
    ) -> OrchestratedResponse:
        """
        Process user message through complete pipeline.
        
        This is the main entry point for generating responses.
        
        Args:
            user_message: User's input message
            user_id: User ID
            session: Optional session for context
            include_embeddings: Whether to generate embeddings
            
        Returns:
            OrchestratedResponse with validated response
        """
        logger.debug(
            "Processing user message",
            user_id=str(user_id),
            message_length=len(user_message),
        )
        
        # Step 1: Detection
        detection = await self._detection.detect(
            text=user_message,
            user_id=user_id,
            session_id=session.id if session else None,
            include_embeddings=include_embeddings,
        )
        
        logger.info(
            "Detection completed",
            severity=detection.severity.name,
            confidence=detection.confidence,
        )
        
        # Step 2: Decision
        context = DecisionContext(
            user_id=user_id,
            session_id=session.id if session else None,
            detection_result=detection,
            session_message_count=session.message_count if session else 0,
        )
        
        decision = self._decision.decide(context)
        
        # Step 3: Build prompt
        conversation_history = (
            session.get_conversation_context() if session else []
        )
        
        prompt = self._prompt_builder.build(
            decision=decision,
            user_message=user_message,
            conversation_history=conversation_history,
        )
        
        # Validate prompt for injection
        if not self._safety.validate_prompt(prompt.system_prompt + user_message):
            logger.warning("Prompt validation failed - potential injection")
            return self._create_fallback_response(detection, decision)
        
        # Step 4: Generate LLM response
        llm_response = await self._generate_with_fallback(prompt)
        
        if llm_response is None:
            logger.error("All LLM providers failed")
            return self._create_fallback_response(detection, decision)
        
        # Step 5: Safety validation
        is_crisis = decision.escalate_to_crisis
        safety_result = self._safety.validate(
            response=llm_response.content,
            is_crisis_response=is_crisis,
        )
        
        if safety_result.blocked:
            logger.warning("Response blocked by safety validator")
        
        # Step 6: Update session if provided
        session_updated = False
        if session:
            session.add_message("user", user_message)
            session.add_message(
                "assistant",
                safety_result.filtered_response,
                metadata={"severity": detection.severity.name},
            )
            session_updated = True
        
        # Step 7: Build audit data
        audit_data = {
            "user_id": str(user_id),
            "severity": detection.severity.name,
            "decision_strategy": decision.strategy.value,
            "llm_provider": llm_response.provider,
            "llm_model": llm_response.model,
            "safety_modified": safety_result.was_modified,
            "safety_blocked": safety_result.blocked,
        }
        
        logger.info(
            "Response orchestration complete",
            severity=detection.severity.name,
            provider=llm_response.provider,
        )
        
        return OrchestratedResponse(
            response_text=safety_result.filtered_response,
            detection=detection,
            decision=decision,
            safety_result=safety_result,
            llm_response=llm_response,
            session_updated=session_updated,
            audit_data=audit_data,
        )
    
    async def _generate_with_fallback(
        self,
        prompt: BuiltPrompt,
    ) -> Optional[LLMResponse]:
        """
        Generate response with fallback to secondary provider.
        
        Args:
            prompt: Built prompt
            
        Returns:
            LLM response or None if all providers fail
        """
        # Try primary provider
        if self._primary_llm.is_configured():
            try:
                return await self._primary_llm.generate(prompt)
            except LLMProviderError as e:
                logger.warning(
                    "Primary LLM failed, trying fallback",
                    provider=e.provider,
                    error=str(e),
                )
        
        # Try fallback provider
        if self._fallback_llm.is_configured():
            try:
                return await self._fallback_llm.generate(prompt)
            except LLMProviderError as e:
                logger.error(
                    "Fallback LLM also failed",
                    provider=e.provider,
                    error=str(e),
                )
        
        return None
    
    def _create_fallback_response(
        self,
        detection: DetectionResult,
        decision: Decision,
    ) -> OrchestratedResponse:
        """Create response when LLM fails."""
        safety_result = SafetyResult(
            is_safe=True,
            original_response=self.FALLBACK_RESPONSE,
            filtered_response=self.FALLBACK_RESPONSE,
        )
        
        return OrchestratedResponse(
            response_text=self.FALLBACK_RESPONSE,
            detection=detection,
            decision=decision,
            safety_result=safety_result,
            audit_data={"fallback_used": True},
        )
    
    async def health_check(self) -> dict:
        """
        Check health of all components.
        
        Returns:
            Dictionary of component health statuses
        """
        primary_healthy = await self._primary_llm.health_check()
        fallback_healthy = await self._fallback_llm.health_check()
        
        return {
            "orchestrator": True,
            "detection": True,  # Always available (may use fallback)
            "primary_llm": primary_healthy,
            "fallback_llm": fallback_healthy,
            "llm_available": primary_healthy or fallback_healthy,
        }
