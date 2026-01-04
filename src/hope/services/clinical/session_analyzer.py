"""
Session Analyzer

Tracks panic intensity changes during a session and
produces time-series metrics.

ARCHITECTURE: Maintains in-session state and produces
structured metrics for clinical analysis.

CLINICAL_VALIDATION_REQUIRED: Metric definitions and
effectiveness calculations need clinical validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.session_metrics import (
    SessionMetrics,
    IntensityDataPoint,
    InterventionRecord,
)
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SessionState:
    """
    Current state of the session being analyzed.
    
    Attributes:
        message_count: Number of messages processed
        current_intensity: Current panic intensity
        current_severity: Current severity classification
        is_escalating: Whether intensity is increasing
        trend_direction: Up, down, or stable
    """
    
    message_count: int = 0
    current_intensity: float = 0.0
    current_severity: PanicSeverity = PanicSeverity.NONE
    is_escalating: bool = False
    trend_direction: str = "stable"
    
    def to_dict(self) -> dict:
        return {
            "message_count": self.message_count,
            "current_intensity": round(self.current_intensity, 3),
            "current_severity": self.current_severity.name,
            "is_escalating": self.is_escalating,
            "trend": self.trend_direction,
        }


class SessionAnalyzer:
    """
    Real-time session analysis for panic tracking.
    
    Tracks how panic intensity changes over the course
    of a session and measures intervention effectiveness.
    
    Key Metrics:
    - Peak intensity and when it occurred
    - Time-to-calm (how long to reduce intensity)
    - Intervention effectiveness
    - Session success rate
    
    Usage:
        analyzer = SessionAnalyzer(session_id, user_id)
        analyzer.record_message(intensity, severity, intervention)
        metrics = analyzer.get_metrics()
    
    CLINICAL_VALIDATION_REQUIRED: Metric interpretation and
    "success" definitions need clinical input.
    """
    
    # Window size for trend calculation
    TREND_WINDOW: int = 3
    
    # Escalation threshold
    ESCALATION_THRESHOLD: float = 0.2
    
    def __init__(
        self,
        session_id: UUID,
        user_id: UUID,
    ) -> None:
        """
        Initialize session analyzer.
        
        Args:
            session_id: Session to analyze
            user_id: User in session
        """
        self._session_id = session_id
        self._user_id = user_id
        self._started_at = datetime.utcnow()
        
        self._metrics = SessionMetrics(
            session_id=session_id,
            user_id=user_id,
            started_at=self._started_at,
        )
        self._state = SessionState()
    
    def record_message(
        self,
        intensity: float,
        severity: PanicSeverity,
        intervention: Optional[str] = None,
    ) -> SessionState:
        """
        Record a message and update analysis.
        
        Args:
            intensity: Panic intensity (0.0-1.0)
            severity: Severity classification
            intervention: Intervention applied (if any)
            
        Returns:
            Updated session state
        """
        # Add data point
        self._metrics.add_data_point(
            intensity=intensity,
            severity=severity,
            intervention=intervention,
        )
        
        # Update state
        self._state.message_count = len(self._metrics.intensity_trajectory)
        self._state.current_intensity = intensity
        self._state.current_severity = severity
        
        # Calculate trend
        self._update_trend()
        
        # Check for escalation
        self._check_escalation()
        
        logger.debug(
            "Session message recorded",
            session_id=str(self._session_id),
            intensity=round(intensity, 3),
            trend=self._state.trend_direction,
        )
        
        return self._state
    
    def _update_trend(self) -> None:
        """Calculate intensity trend direction."""
        trajectory = self._metrics.intensity_trajectory
        
        if len(trajectory) < 2:
            self._state.trend_direction = "stable"
            return
        
        # Look at last N data points
        window = trajectory[-self.TREND_WINDOW:]
        
        if len(window) < 2:
            self._state.trend_direction = "stable"
            return
        
        # Calculate average change
        changes = [
            window[i].intensity - window[i-1].intensity
            for i in range(1, len(window))
        ]
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.05:
            self._state.trend_direction = "increasing"
        elif avg_change < -0.05:
            self._state.trend_direction = "decreasing"
        else:
            self._state.trend_direction = "stable"
    
    def _check_escalation(self) -> None:
        """Check if intensity is escalating."""
        trajectory = self._metrics.intensity_trajectory
        
        if len(trajectory) < 2:
            self._state.is_escalating = False
            return
        
        # Compare current to start
        start_intensity = trajectory[0].intensity
        current = self._state.current_intensity
        
        increase = current - start_intensity
        
        self._state.is_escalating = (
            increase > self.ESCALATION_THRESHOLD and
            self._state.trend_direction == "increasing"
        )
        
        if self._state.is_escalating:
            self._metrics.escalation_occurred = True
    
    def mark_intervention(
        self,
        intervention_type: str,
    ) -> None:
        """
        Mark that an intervention was applied.
        
        Call this after intervention is delivered.
        
        Args:
            intervention_type: Type of intervention
        """
        if not self._metrics.intensity_trajectory:
            return
        
        latest = self._metrics.intensity_trajectory[-1]
        
        record = InterventionRecord(
            intervention_type=intervention_type,
            applied_at=datetime.utcnow(),
            intensity_before=latest.intensity,
        )
        
        self._metrics.interventions.append(record)
    
    def get_state(self) -> SessionState:
        """Get current session state."""
        return self._state
    
    def get_metrics(self) -> SessionMetrics:
        """
        Get complete session metrics.
        
        Returns:
            SessionMetrics with all tracked data
        """
        return self._metrics
    
    def get_summary(self) -> dict:
        """
        Get session summary for logging/display.
        
        Returns:
            Dictionary with key metrics
        """
        return self._metrics.to_dict()
    
    def should_escalate(self) -> bool:
        """
        Check if session should trigger escalation.
        
        Based on:
        - Current severity
        - Escalation trend
        - Duration at high intensity
        """
        if self._state.current_severity >= PanicSeverity.CRITICAL:
            return True
        
        if self._state.is_escalating and self._state.current_severity >= PanicSeverity.SEVERE:
            return True
        
        # Check sustained high intensity
        trajectory = self._metrics.intensity_trajectory
        if len(trajectory) >= 3:
            recent = trajectory[-3:]
            if all(p.intensity >= 0.7 for p in recent):
                return True
        
        return False
    
    def get_recommended_strategy(self) -> Optional[str]:
        """
        Get recommended response strategy based on analysis.
        
        CLINICAL_VALIDATION_REQUIRED: Strategy recommendations
        need clinical validation.
        
        Returns:
            Suggested strategy or None
        """
        if self._state.is_escalating:
            return "de-escalation"
        
        if self._state.trend_direction == "decreasing":
            return "continue_current"
        
        if self._state.current_severity >= PanicSeverity.MODERATE:
            # Check what's worked before
            effective = self._metrics.get_most_effective_intervention()
            if effective:
                return f"repeat:{effective}"
            return "active_intervention"
        
        return "supportive"
    
    def finalize(self, summary: Optional[str] = None) -> SessionMetrics:
        """
        Finalize session analysis.
        
        Call when session ends to close out metrics.
        
        Args:
            summary: Optional session summary
            
        Returns:
            Final session metrics
        """
        # Update final intervention effectiveness
        if self._metrics.interventions:
            last = self._metrics.interventions[-1]
            if last.intensity_after is None and self._metrics.intensity_trajectory:
                last.intensity_after = self._metrics.intensity_trajectory[-1].intensity
                last.was_effective = last.intensity_after < last.intensity_before
        
        logger.info(
            "Session analysis finalized",
            session_id=str(self._session_id),
            peak_intensity=round(self._metrics.peak_intensity, 3),
            was_successful=self._metrics.was_session_successful(),
        )
        
        return self._metrics


class SessionAnalyzerRegistry:
    """
    Registry for active session analyzers.
    
    Provides singleton-like access to analyzers by session ID.
    """
    
    _analyzers: dict[UUID, SessionAnalyzer] = {}
    
    @classmethod
    def get_or_create(
        cls,
        session_id: UUID,
        user_id: UUID,
    ) -> SessionAnalyzer:
        """Get existing analyzer or create new one."""
        if session_id not in cls._analyzers:
            cls._analyzers[session_id] = SessionAnalyzer(
                session_id=session_id,
                user_id=user_id,
            )
        return cls._analyzers[session_id]
    
    @classmethod
    def get(cls, session_id: UUID) -> Optional[SessionAnalyzer]:
        """Get analyzer if exists."""
        return cls._analyzers.get(session_id)
    
    @classmethod
    def remove(cls, session_id: UUID) -> Optional[SessionAnalyzer]:
        """Remove and return analyzer."""
        return cls._analyzers.pop(session_id, None)
    
    @classmethod
    def clear(cls) -> None:
        """Clear all analyzers."""
        cls._analyzers.clear()
