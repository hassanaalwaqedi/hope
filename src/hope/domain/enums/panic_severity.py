"""
Panic Severity and Urgency Enumerations

Defines standardized severity levels for panic events and
corresponding urgency levels for response prioritization.

CLINICAL_REVIEW_REQUIRED: These thresholds and definitions
should be validated by mental health professionals before
production deployment.
"""

from enum import IntEnum, StrEnum


class PanicSeverity(IntEnum):
    """
    Panic attack severity classification.
    
    Levels are based on symptom intensity and duration.
    Higher values indicate more severe episodes requiring
    more intensive intervention strategies.
    
    CLINICAL_REVIEW_REQUIRED: Severity thresholds and
    corresponding intervention levels need clinical validation.
    """
    
    NONE = 0
    """No panic indicators detected."""
    
    MILD = 1
    """
    Mild anxiety or early panic signs.
    - Minor physical symptoms (slight tension)
    - Manageable discomfort
    - User remains functional
    """
    
    MODERATE = 2
    """
    Moderate panic symptoms.
    - Noticeable physical symptoms (racing heart, sweating)
    - Significant distress
    - Impaired concentration
    """
    
    SEVERE = 3
    """
    Severe panic attack in progress.
    - Intense physical symptoms
    - Overwhelming fear or dread
    - Significant functional impairment
    """
    
    CRITICAL = 4
    """
    Critical state requiring immediate attention.
    - Extreme symptoms
    - Risk of harm or crisis
    - May require emergency intervention referral
    
    SAFETY_NOTE: At this level, system should provide
    emergency resources and recommend professional help.
    """


class UrgencyLevel(StrEnum):
    """
    Response urgency classification for decision engine.
    
    Maps to response timing and intervention intensity.
    """
    
    ROUTINE = "routine"
    """
    Standard response time acceptable.
    - Normal check-in
    - Preventive content
    """
    
    ELEVATED = "elevated"
    """
    Prioritized response needed.
    - Active monitoring
    - Proactive support offered
    """
    
    HIGH = "high"
    """
    Urgent response required.
    - Immediate intervention strategies
    - Grounding techniques
    """
    
    EMERGENCY = "emergency"
    """
    Emergency response protocols.
    - Safety resources provided immediately
    - Crisis hotline information
    - Professional help recommended
    
    SAFETY_NOTE: System must never attempt to handle
    true emergencies alone. Always provide professional
    resources at this level.
    """
    
    @classmethod
    def from_severity(cls, severity: PanicSeverity) -> "UrgencyLevel":
        """
        Map panic severity to urgency level.
        
        Args:
            severity: Panic severity classification
            
        Returns:
            Corresponding urgency level
        """
        mapping = {
            PanicSeverity.NONE: cls.ROUTINE,
            PanicSeverity.MILD: cls.ELEVATED,
            PanicSeverity.MODERATE: cls.HIGH,
            PanicSeverity.SEVERE: cls.EMERGENCY,
            PanicSeverity.CRITICAL: cls.EMERGENCY,
        }
        return mapping.get(severity, cls.HIGH)
