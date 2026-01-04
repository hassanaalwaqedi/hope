"""
Panic Stability Gate

Determines user's stability state during and after panic episodes.
Used to gate AI features based on clinical safety requirements.

SAFETY CRITICAL: This gate protects vulnerable users from
potentially destabilizing AI interactions during acute panic.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import IntEnum
from typing import Optional, List
from uuid import UUID

from hope.domain.enums.panic_severity import PanicSeverity
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


class PanicStabilityState(IntEnum):
    """
    Panic stability states for AI gating.
    
    Higher values = more stable = more AI allowed.
    """
    PANIC_CRITICAL = 1    # Gemini DISABLED - acute crisis
    PANIC_ACTIVE = 2      # Gemini DISABLED - active panic
    PANIC_STABILIZING = 3 # Gemini LIMITED - showing improvement
    PANIC_RECOVERED = 4   # Gemini ENABLED - post-recovery


@dataclass
class StabilityContext:
    """Context for stability evaluation."""
    session_id: UUID
    user_id: UUID
    started_at: datetime
    
    # Current state
    current_severity: PanicSeverity
    current_intensity: float  # 0.0 - 1.0
    
    # History
    severity_history: List[PanicSeverity] = field(default_factory=list)
    intensity_history: List[float] = field(default_factory=list)
    
    # Exercise tracking
    breathing_cycles_completed: int = 0
    grounding_steps_completed: int = 0
    
    # Crisis signals
    has_crisis_signals: bool = False
    has_self_harm_signals: bool = False
    
    @property
    def elapsed_seconds(self) -> float:
        """Seconds since session started."""
        return (datetime.utcnow() - self.started_at).total_seconds()
    
    @property
    def has_completed_exercise(self) -> bool:
        """Whether user has completed at least one regulation exercise."""
        return (
            self.breathing_cycles_completed >= 3 or
            self.grounding_steps_completed >= 3
        )
    
    @property
    def severity_trend(self) -> float:
        """
        Calculate severity trend.
        Negative = improving, Positive = worsening.
        """
        if len(self.severity_history) < 2:
            return 0.0
        
        recent = self.severity_history[-3:]
        if len(recent) < 2:
            return 0.0
        
        # Compare values
        values = [s.value for s in recent]
        return values[-1] - values[0]
    
    @property
    def intensity_trend(self) -> float:
        """
        Calculate intensity trend.
        Negative = improving, Positive = worsening.
        """
        if len(self.intensity_history) < 2:
            return 0.0
        
        recent = self.intensity_history[-3:]
        if len(recent) < 2:
            return 0.0
        
        return recent[-1] - recent[0]


@dataclass
class StabilityEvaluation:
    """Result of stability evaluation."""
    state: PanicStabilityState
    reason: str
    timestamp: datetime
    
    # Metrics used for evaluation
    elapsed_seconds: float
    severity_trend: float
    intensity_trend: float
    exercise_completed: bool
    
    def to_audit_log(self) -> dict:
        """Create audit log entry (no PII)."""
        return {
            "state": self.state.name,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "elapsed_seconds": round(self.elapsed_seconds, 1),
            "severity_trend": round(self.severity_trend, 3),
            "intensity_trend": round(self.intensity_trend, 3),
            "exercise_completed": self.exercise_completed,
        }


class StabilityGate:
    """
    Evaluates user's stability state for AI gating.
    
    SAFETY: This gate ensures Gemini is NEVER active during
    acute panic or crisis states.
    
    State derivation rules:
    1. PANIC_CRITICAL: Crisis signals OR severity >= CRITICAL
    2. PANIC_ACTIVE: High severity OR not enough time elapsed
    3. PANIC_STABILIZING: Improving trend + exercise completed
    4. PANIC_RECOVERED: Sustained improvement + significant time
    """
    
    # Thresholds (clinically validated values)
    MIN_TIME_FOR_STABILIZING_SECONDS = 60
    MIN_TIME_FOR_RECOVERED_SECONDS = 180
    INTENSITY_IMPROVEMENT_THRESHOLD = 0.2
    
    def evaluate(self, context: StabilityContext) -> StabilityEvaluation:
        """
        Evaluate current stability state.
        
        Args:
            context: Current session context
            
        Returns:
            StabilityEvaluation with state and reason
        """
        now = datetime.utcnow()
        
        # CRITICAL: Crisis signals always override
        if context.has_crisis_signals or context.has_self_harm_signals:
            return StabilityEvaluation(
                state=PanicStabilityState.PANIC_CRITICAL,
                reason="Crisis or self-harm signals detected",
                timestamp=now,
                elapsed_seconds=context.elapsed_seconds,
                severity_trend=context.severity_trend,
                intensity_trend=context.intensity_trend,
                exercise_completed=context.has_completed_exercise,
            )
        
        # CRITICAL: Extreme severity
        if context.current_severity >= PanicSeverity.CRITICAL:
            return StabilityEvaluation(
                state=PanicStabilityState.PANIC_CRITICAL,
                reason=f"Severity at {context.current_severity.name}",
                timestamp=now,
                elapsed_seconds=context.elapsed_seconds,
                severity_trend=context.severity_trend,
                intensity_trend=context.intensity_trend,
                exercise_completed=context.has_completed_exercise,
            )
        
        # ACTIVE: Not enough time elapsed
        if context.elapsed_seconds < self.MIN_TIME_FOR_STABILIZING_SECONDS:
            return StabilityEvaluation(
                state=PanicStabilityState.PANIC_ACTIVE,
                reason=f"Elapsed time {context.elapsed_seconds:.0f}s < {self.MIN_TIME_FOR_STABILIZING_SECONDS}s threshold",
                timestamp=now,
                elapsed_seconds=context.elapsed_seconds,
                severity_trend=context.severity_trend,
                intensity_trend=context.intensity_trend,
                exercise_completed=context.has_completed_exercise,
            )
        
        # ACTIVE: High severity without improvement
        if context.current_severity >= PanicSeverity.SEVERE:
            if context.severity_trend >= 0:  # Not improving
                return StabilityEvaluation(
                    state=PanicStabilityState.PANIC_ACTIVE,
                    reason="Severe panic without improvement trend",
                    timestamp=now,
                    elapsed_seconds=context.elapsed_seconds,
                    severity_trend=context.severity_trend,
                    intensity_trend=context.intensity_trend,
                    exercise_completed=context.has_completed_exercise,
                )
        
        # STABILIZING: Improving but not yet recovered
        if context.has_completed_exercise:
            intensity_improved = (
                len(context.intensity_history) >= 2 and
                context.intensity_history[0] - context.current_intensity >= self.INTENSITY_IMPROVEMENT_THRESHOLD
            )
            
            # Check for RECOVERED
            if (
                context.elapsed_seconds >= self.MIN_TIME_FOR_RECOVERED_SECONDS and
                context.current_severity <= PanicSeverity.MILD and
                intensity_improved and
                context.severity_trend < 0  # Improving
            ):
                return StabilityEvaluation(
                    state=PanicStabilityState.PANIC_RECOVERED,
                    reason="Sustained improvement with exercise completion",
                    timestamp=now,
                    elapsed_seconds=context.elapsed_seconds,
                    severity_trend=context.severity_trend,
                    intensity_trend=context.intensity_trend,
                    exercise_completed=context.has_completed_exercise,
                )
            
            # STABILIZING
            return StabilityEvaluation(
                state=PanicStabilityState.PANIC_STABILIZING,
                reason="Improvement with exercise completion",
                timestamp=now,
                elapsed_seconds=context.elapsed_seconds,
                severity_trend=context.severity_trend,
                intensity_trend=context.intensity_trend,
                exercise_completed=context.has_completed_exercise,
            )
        
        # ACTIVE: No exercise completed yet
        return StabilityEvaluation(
            state=PanicStabilityState.PANIC_ACTIVE,
            reason="No regulation exercise completed",
            timestamp=now,
            elapsed_seconds=context.elapsed_seconds,
            severity_trend=context.severity_trend,
            intensity_trend=context.intensity_trend,
            exercise_completed=context.has_completed_exercise,
        )


# Global instance
stability_gate = StabilityGate()
