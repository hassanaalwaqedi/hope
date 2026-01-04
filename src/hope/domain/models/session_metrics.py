"""
Session Metrics Model

Time-series metrics for tracking panic intensity changes
during a session and measuring intervention effectiveness.

CLINICAL_VALIDATION_REQUIRED: Metric definitions and
"effectiveness" calculations need clinical validation.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID, uuid4

from hope.domain.enums.panic_severity import PanicSeverity


@dataclass
class IntensityDataPoint:
    """
    Single intensity measurement at a point in time.
    
    Attributes:
        timestamp: When measurement was taken
        intensity: Panic intensity (0.0-1.0)
        severity: Classified severity at this point
        message_index: Index of message in session
        intervention_applied: Intervention used before this point
    """
    
    timestamp: datetime
    intensity: float
    severity: PanicSeverity
    message_index: int
    intervention_applied: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "intensity": round(self.intensity, 3),
            "severity": self.severity.name,
            "message_index": self.message_index,
            "intervention": self.intervention_applied,
        }


@dataclass
class InterventionRecord:
    """
    Record of an intervention and its outcome.
    
    Attributes:
        intervention_type: Type of intervention applied
        applied_at: When intervention was applied
        intensity_before: Intensity before intervention
        intensity_after: Intensity after intervention (if measured)
        messages_to_effect: Messages until intensity dropped
        was_effective: Whether intervention reduced intensity
    """
    
    intervention_type: str
    applied_at: datetime
    intensity_before: float
    intensity_after: Optional[float] = None
    messages_to_effect: Optional[int] = None
    was_effective: Optional[bool] = None
    
    def calculate_effectiveness(self) -> Optional[float]:
        """
        Calculate effectiveness score.
        
        Returns:
            Effectiveness score (0.0-1.0) or None if not calculable
            
        CLINICAL_VALIDATION_REQUIRED: Effectiveness metric
        definition needs clinical input.
        """
        if self.intensity_after is None:
            return None
        
        if self.intensity_before <= 0:
            return None
        
        # Calculate reduction percentage
        reduction = self.intensity_before - self.intensity_after
        effectiveness = max(0, reduction / self.intensity_before)
        
        # Penalize if it took too many messages
        if self.messages_to_effect and self.messages_to_effect > 5:
            effectiveness *= 0.8  # 20% penalty for slow effect
        
        return min(1.0, effectiveness)
    
    def to_dict(self) -> dict:
        return {
            "intervention_type": self.intervention_type,
            "applied_at": self.applied_at.isoformat(),
            "intensity_before": round(self.intensity_before, 3),
            "intensity_after": round(self.intensity_after, 3) if self.intensity_after else None,
            "effectiveness": self.calculate_effectiveness(),
        }


@dataclass
class SessionMetrics:
    """
    Time-series metrics for a therapy session.
    
    Tracks how panic intensity changes during a session
    and measures intervention effectiveness.
    
    Attributes:
        session_id: Session being tracked
        user_id: User in session
        started_at: Session start time
        
        intensity_trajectory: Time series of intensity measurements
        interventions: Record of interventions applied
        
        peak_intensity: Maximum intensity during session
        peak_severity: Maximum severity during session
        peak_timestamp: When peak occurred
        
        time_to_calm: Time from peak to below-threshold intensity
        final_intensity: Intensity at session end
        
        total_messages: Number of messages in session
        escalation_occurred: Whether crisis was triggered
    """
    
    session_id: UUID
    user_id: UUID
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    # Time series data
    intensity_trajectory: list[IntensityDataPoint] = field(default_factory=list)
    interventions: list[InterventionRecord] = field(default_factory=list)
    
    # Peak metrics
    peak_intensity: float = 0.0
    peak_severity: PanicSeverity = PanicSeverity.NONE
    peak_timestamp: Optional[datetime] = None
    
    # Recovery metrics
    time_to_calm: Optional[timedelta] = None
    final_intensity: float = 0.0
    
    # Session summary
    total_messages: int = 0
    escalation_occurred: bool = False
    
    # CALM_THRESHOLD: Intensity below which user is considered "calm"
    # CLINICAL_VALIDATION_REQUIRED
    CALM_THRESHOLD: float = 0.25
    
    def add_data_point(
        self,
        intensity: float,
        severity: PanicSeverity,
        intervention: Optional[str] = None,
    ) -> None:
        """
        Add a new intensity data point.
        
        Args:
            intensity: Current panic intensity
            severity: Current severity classification
            intervention: Intervention applied (if any)
        """
        now = datetime.utcnow()
        
        data_point = IntensityDataPoint(
            timestamp=now,
            intensity=intensity,
            severity=severity,
            message_index=len(self.intensity_trajectory),
            intervention_applied=intervention,
        )
        self.intensity_trajectory.append(data_point)
        self.total_messages = len(self.intensity_trajectory)
        
        # Update peak if this is highest
        if intensity > self.peak_intensity:
            self.peak_intensity = intensity
            self.peak_severity = severity
            self.peak_timestamp = now
        
        # Update final intensity
        self.final_intensity = intensity
        
        # Calculate time to calm if applicable
        self._update_time_to_calm()
        
        # Record intervention
        if intervention:
            self._record_intervention(intervention, intensity)
    
    def _update_time_to_calm(self) -> None:
        """Calculate time from peak to calm."""
        if not self.peak_timestamp:
            return
        
        if self.final_intensity >= self.CALM_THRESHOLD:
            self.time_to_calm = None
            return
        
        # Find first point after peak that dropped below threshold
        for point in self.intensity_trajectory:
            if point.timestamp > self.peak_timestamp:
                if point.intensity < self.CALM_THRESHOLD:
                    self.time_to_calm = point.timestamp - self.peak_timestamp
                    break
    
    def _record_intervention(
        self,
        intervention_type: str,
        intensity_before: float,
    ) -> None:
        """Record a new intervention."""
        record = InterventionRecord(
            intervention_type=intervention_type,
            applied_at=datetime.utcnow(),
            intensity_before=intensity_before,
        )
        self.interventions.append(record)
        
        # Update previous intervention's after-intensity
        if len(self.interventions) > 1:
            prev = self.interventions[-2]
            prev.intensity_after = intensity_before
            prev.messages_to_effect = len(self.intensity_trajectory) - 1
            prev.was_effective = (
                prev.intensity_after < prev.intensity_before
            )
    
    def get_intensity_change(self) -> float:
        """
        Calculate overall intensity change.
        
        Returns:
            Change from first to last measurement
            Negative = improvement, Positive = worsening
        """
        if len(self.intensity_trajectory) < 2:
            return 0.0
        
        first = self.intensity_trajectory[0].intensity
        last = self.intensity_trajectory[-1].intensity
        return last - first
    
    def get_most_effective_intervention(self) -> Optional[str]:
        """Get the intervention with highest effectiveness."""
        effective = [
            (i.intervention_type, i.calculate_effectiveness())
            for i in self.interventions
            if i.calculate_effectiveness() is not None
        ]
        
        if not effective:
            return None
        
        return max(effective, key=lambda x: x[1])[0]
    
    def get_average_intensity(self) -> float:
        """Calculate average intensity across session."""
        if not self.intensity_trajectory:
            return 0.0
        
        total = sum(p.intensity for p in self.intensity_trajectory)
        return total / len(self.intensity_trajectory)
    
    def was_session_successful(self) -> bool:
        """
        Determine if session was successful.
        
        CLINICAL_VALIDATION_REQUIRED: Success criteria
        need clinical definition.
        
        Returns:
            True if final intensity is below threshold
            and lower than peak
        """
        if not self.intensity_trajectory:
            return True  # No distress detected
        
        return (
            self.final_intensity < self.CALM_THRESHOLD and
            self.final_intensity < self.peak_intensity * 0.5
        )
    
    def to_dict(self) -> dict:
        return {
            "session_id": str(self.session_id),
            "started_at": self.started_at.isoformat(),
            "peak_intensity": round(self.peak_intensity, 3),
            "peak_severity": self.peak_severity.name,
            "final_intensity": round(self.final_intensity, 3),
            "time_to_calm_seconds": (
                self.time_to_calm.total_seconds() 
                if self.time_to_calm else None
            ),
            "total_messages": self.total_messages,
            "intensity_change": round(self.get_intensity_change(), 3),
            "average_intensity": round(self.get_average_intensity(), 3),
            "most_effective_intervention": self.get_most_effective_intervention(),
            "was_successful": self.was_session_successful(),
            "escalation_occurred": self.escalation_occurred,
        }
    
    def get_trajectory_summary(self) -> list[dict]:
        """Get simplified trajectory for visualization."""
        return [p.to_dict() for p in self.intensity_trajectory]
