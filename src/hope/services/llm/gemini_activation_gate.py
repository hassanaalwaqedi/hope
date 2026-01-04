"""
Gemini Activation Gate

Controls when Gemini Flash can be invoked.
Implements strict safety rules to protect vulnerable users.

SAFETY CRITICAL: Gemini is ONLY allowed when ALL conditions pass.
Any failure results in immediate fallback to rule-based responses.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

from hope.services.safety.stability_gate import (
    StabilityContext,
    StabilityEvaluation,
    PanicStabilityState,
    stability_gate,
)
from hope.config import get_settings
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


class ActivationDenialReason(Enum):
    """Reasons for denying Gemini activation."""
    STABILITY_TOO_LOW = "stability_too_low"
    CRISIS_SIGNALS = "crisis_signals"
    NO_EXERCISE_COMPLETED = "no_exercise_completed"
    TIME_THRESHOLD_NOT_MET = "time_threshold_not_met"
    GEMINI_DISABLED = "gemini_disabled"
    ERROR_THRESHOLD_EXCEEDED = "error_threshold_exceeded"


@dataclass
class ActivationDecision:
    """Result of activation gate evaluation."""
    allowed: bool
    reason: str
    denial_reason: Optional[ActivationDenialReason] = None
    stability_state: Optional[PanicStabilityState] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_audit_log(self) -> dict:
        """Create audit log entry (no PII)."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "denial_reason": self.denial_reason.value if self.denial_reason else None,
            "stability_state": self.stability_state.name if self.stability_state else None,
            "timestamp": self.timestamp.isoformat(),
        }


class GeminiActivationGate:
    """
    Gate controlling Gemini activation.
    
    Gemini may ONLY be called when ALL conditions are true:
    1. Stability state >= PANIC_STABILIZING
    2. No crisis/self-harm signals detected
    3. User has completed at least one regulation exercise
    4. Time since panic entry >= threshold (60s)
    5. Gemini not disabled via config/kill-switch
    6. Error threshold not exceeded
    
    If ANY condition fails → fallback to rule-based responses.
    """
    
    # Safety thresholds
    MIN_STABILITY_STATE = PanicStabilityState.PANIC_STABILIZING
    MIN_TIME_SECONDS = 60
    ERROR_THRESHOLD = 3
    
    def __init__(self):
        self._session_error_counts: dict[str, int] = {}
        settings = get_settings()
        self._gemini_disabled = getattr(settings, 'gemini_disabled', False)
    
    def is_allowed(
        self,
        context: StabilityContext,
        stability_eval: Optional[StabilityEvaluation] = None,
    ) -> ActivationDecision:
        """
        Check if Gemini is allowed for this context.
        
        Args:
            context: Current session context
            stability_eval: Pre-computed stability evaluation (optional)
            
        Returns:
            ActivationDecision with allowed status and reason
        """
        session_key = str(context.session_id)
        
        # Check 1: Kill-switch
        if self._gemini_disabled:
            return ActivationDecision(
                allowed=False,
                reason="Gemini disabled via configuration",
                denial_reason=ActivationDenialReason.GEMINI_DISABLED,
            )
        
        # Check 2: Error threshold
        if self._session_error_counts.get(session_key, 0) >= self.ERROR_THRESHOLD:
            return ActivationDecision(
                allowed=False,
                reason=f"Error threshold ({self.ERROR_THRESHOLD}) exceeded for session",
                denial_reason=ActivationDenialReason.ERROR_THRESHOLD_EXCEEDED,
            )
        
        # Check 3: Crisis signals (highest priority safety check)
        if context.has_crisis_signals or context.has_self_harm_signals:
            return ActivationDecision(
                allowed=False,
                reason="Crisis or self-harm signals detected",
                denial_reason=ActivationDenialReason.CRISIS_SIGNALS,
            )
        
        # Check 4: Time threshold
        if context.elapsed_seconds < self.MIN_TIME_SECONDS:
            return ActivationDecision(
                allowed=False,
                reason=f"Time threshold not met ({context.elapsed_seconds:.0f}s < {self.MIN_TIME_SECONDS}s)",
                denial_reason=ActivationDenialReason.TIME_THRESHOLD_NOT_MET,
            )
        
        # Check 5: Exercise completion
        if not context.has_completed_exercise:
            return ActivationDecision(
                allowed=False,
                reason="No regulation exercise completed",
                denial_reason=ActivationDenialReason.NO_EXERCISE_COMPLETED,
            )
        
        # Check 6: Stability state
        if stability_eval is None:
            stability_eval = stability_gate.evaluate(context)
        
        if stability_eval.state < self.MIN_STABILITY_STATE:
            return ActivationDecision(
                allowed=False,
                reason=f"Stability state {stability_eval.state.name} < required {self.MIN_STABILITY_STATE.name}",
                denial_reason=ActivationDenialReason.STABILITY_TOO_LOW,
                stability_state=stability_eval.state,
            )
        
        # ALL CHECKS PASSED
        logger.info(
            "Gemini activation ALLOWED",
            session_id=session_key,
            stability_state=stability_eval.state.name,
            elapsed_seconds=context.elapsed_seconds,
        )
        
        return ActivationDecision(
            allowed=True,
            reason=f"All conditions met (state: {stability_eval.state.name})",
            stability_state=stability_eval.state,
        )
    
    def record_error(self, session_id: str) -> None:
        """Record an error for session-level tracking."""
        if session_id not in self._session_error_counts:
            self._session_error_counts[session_id] = 0
        self._session_error_counts[session_id] += 1
        
        logger.warning(
            "Gemini error recorded",
            session_id=session_id,
            count=self._session_error_counts[session_id],
        )
    
    def clear_session(self, session_id: str) -> None:
        """Clear error count for session."""
        if session_id in self._session_error_counts:
            del self._session_error_counts[session_id]
    
    def disable(self) -> None:
        """Disable Gemini globally (kill-switch)."""
        self._gemini_disabled = True
        logger.warning("Gemini DISABLED via kill-switch")
    
    def enable(self) -> None:
        """Re-enable Gemini (use with caution)."""
        self._gemini_disabled = False
        logger.warning("Gemini RE-ENABLED via kill-switch")


# Global instance
gemini_activation_gate = GeminiActivationGate()
