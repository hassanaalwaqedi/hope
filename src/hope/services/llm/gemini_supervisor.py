"""
Gemini Supervisor

Manages Gemini Flash invocations with timeout, fallback, and error handling.
Ensures Gemini failures never block user support.

SAFETY CRITICAL: This supervisor protects the user experience.
Any Gemini failure results in immediate fallback to static responses.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from hope.infrastructure.llm.gemini_flash_provider import GeminiFlashProvider
from hope.services.prompt.recovery_prompt_templates import (
    RecoveryPromptType,
    get_recovery_prompt,
    get_fallback_response,
)
from hope.services.prompt.prompt_builder import BuiltPrompt
from hope.services.llm.gemini_activation_gate import gemini_activation_gate
from hope.config import get_settings
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GeminiResponse:
    """Response from Gemini supervisor."""
    text: str
    source: str  # "gemini" or "fallback"
    latency_ms: float
    prompt_type: RecoveryPromptType
    error: Optional[str] = None


class GeminiSupervisor:
    """
    Supervised Gemini invocation with safety guarantees.
    
    Features:
    - Hard timeout (2 seconds)
    - Automatic fallback on error
    - Error counting for session-level disable
    - Structured logging (no PII)
    """
    
    TIMEOUT_SECONDS = 2.0  # Hard timeout for latency
    
    def __init__(self):
        settings = get_settings()
        self._provider: Optional[GeminiFlashProvider] = None
        self._initialized = False
        
        # Check if Gemini is configured
        gemini_key = getattr(settings.gemini, 'api_key', None)
        self._gemini_available = gemini_key is not None and str(gemini_key) != ''
    
    async def initialize(self) -> None:
        """Initialize Gemini provider."""
        if not self._gemini_available:
            logger.warning("Gemini API key not configured - supervisor disabled")
            return
        
        try:
            self._provider = GeminiFlashProvider()
            self._initialized = True
            logger.info("Gemini supervisor initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {e}")
            self._initialized = False
    
    @property
    def is_available(self) -> bool:
        """Check if Gemini is available for use."""
        return self._initialized and self._provider is not None
    
    async def generate_recovery_message(
        self,
        prompt_type: RecoveryPromptType,
        session_id: str,
    ) -> GeminiResponse:
        """
        Generate a recovery message using Gemini.
        
        If Gemini fails or times out, returns fallback response.
        
        Args:
            prompt_type: Type of recovery prompt
            session_id: Session ID for error tracking
            
        Returns:
            GeminiResponse with text and metadata
        """
        start_time = datetime.utcnow()
        
        # Check if Gemini is available
        if not self.is_available:
            return self._create_fallback_response(
                prompt_type=prompt_type,
                start_time=start_time,
                reason="Gemini not available",
            )
        
        # Get the prompt
        recovery_prompt = get_recovery_prompt(prompt_type)
        
        # Build the prompt for Gemini
        built_prompt = BuiltPrompt(
            system_prompt=recovery_prompt.system_prompt,
            user_messages=[recovery_prompt.user_context],
            conversation_history=[],
            constraints=[
                "Maximum 2 sentences",
                "No questions",
                "No advice",
            ],
        )
        
        try:
            # Call Gemini with timeout
            response = await asyncio.wait_for(
                self._provider.generate(
                    prompt=built_prompt,
                    max_tokens=100,  # Very limited for safety
                    temperature=0.3,  # Low creativity
                ),
                timeout=self.TIMEOUT_SECONDS,
            )
            
            latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Validate response
            text = self._validate_response(response.content)
            
            logger.info(
                "Gemini recovery message generated",
                prompt_type=prompt_type.value,
                latency_ms=round(latency_ms, 1),
            )
            
            return GeminiResponse(
                text=text,
                source="gemini",
                latency_ms=latency_ms,
                prompt_type=prompt_type,
            )
            
        except asyncio.TimeoutError:
            logger.warning(
                "Gemini timeout - using fallback",
                session_id=session_id,
                timeout=self.TIMEOUT_SECONDS,
            )
            gemini_activation_gate.record_error(session_id)
            return self._create_fallback_response(
                prompt_type=prompt_type,
                start_time=start_time,
                reason="Timeout",
            )
            
        except Exception as e:
            logger.error(
                "Gemini error - using fallback",
                session_id=session_id,
                error=str(e),
            )
            gemini_activation_gate.record_error(session_id)
            return self._create_fallback_response(
                prompt_type=prompt_type,
                start_time=start_time,
                reason=str(e),
            )
    
    def _validate_response(self, text: str) -> str:
        """
        Validate and sanitize Gemini response.
        
        Ensures response meets safety requirements.
        """
        if not text:
            return get_fallback_response(RecoveryPromptType.RECOVERY_ENCOURAGEMENT)
        
        # Truncate if too long (safety bound)
        lines = text.strip().split('.')
        if len(lines) > 3:
            text = '.'.join(lines[:2]) + '.'
        
        # Remove any question marks (no questions allowed)
        text = text.replace('?', '.')
        
        return text.strip()
    
    def _create_fallback_response(
        self,
        prompt_type: RecoveryPromptType,
        start_time: datetime,
        reason: str,
    ) -> GeminiResponse:
        """Create fallback response."""
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        return GeminiResponse(
            text=get_fallback_response(prompt_type),
            source="fallback",
            latency_ms=latency_ms,
            prompt_type=prompt_type,
            error=reason,
        )


# Global instance
gemini_supervisor = GeminiSupervisor()
