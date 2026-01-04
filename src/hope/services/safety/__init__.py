"""Safety services package - Phase 3 Safety Layer."""

from hope.services.safety.safety_validator import SafetyValidator, SafetyResult
from hope.services.safety.risk_engine import RiskScoringEngine, RiskThresholds
from hope.services.safety.crisis_detector import CrisisDetector, LinguisticCrisisAnalyzer
from hope.services.safety.emergency_resources import EmergencyResourceResolver
from hope.services.safety.escalation_manager import EscalationManager, HumanEscalationInterface
from hope.services.safety.safety_pipeline import SafetyPipeline, SafetyEvaluation

__all__ = [
    # Core validator
    "SafetyValidator",
    "SafetyResult",
    # Risk engine
    "RiskScoringEngine",
    "RiskThresholds",
    # Crisis detection
    "CrisisDetector",
    "LinguisticCrisisAnalyzer",
    # Emergency resources
    "EmergencyResourceResolver",
    # Escalation
    "EscalationManager",
    "HumanEscalationInterface",
    # Unified pipeline
    "SafetyPipeline",
    "SafetyEvaluation",
]

