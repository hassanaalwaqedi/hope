"""
Risk Scoring Engine

Calculates risk scores from clinical assessment data.
Consumes ONLY ClinicalAssessment - never raw text.

SAFETY-CRITICAL: This engine determines escalation thresholds.
All scoring logic requires clinical validation.

ARCHITECTURE: The risk engine is a pure function of clinical data.
It has no side effects and produces auditable risk assessments.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from hope.domain.models.clinical_output import ClinicalAssessment, EmotionCategory
from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.risk_models import (
    RiskLevel,
    RiskSignal,
    RiskSignalType,
    RiskAssessment,
    EscalationAction,
)
from hope.config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class RiskThresholds:
    """
    Configurable risk thresholds.
    
    CLINICAL_VALIDATION_REQUIRED: All threshold values
    require clinical validation before production use.
    """
    
    # Risk score thresholds for level classification
    critical_threshold: float = 0.85
    high_threshold: float = 0.65
    elevated_threshold: float = 0.40
    
    # Minimum signals required for escalation
    min_signals_for_critical: int = 3
    min_signals_for_high: int = 2
    
    # Confidence thresholds
    low_confidence_threshold: float = 0.5
    
    # Multi-signal type requirement
    require_multi_signal_types: bool = True


class RiskScoringEngine:
    """
    Multi-factor risk scoring engine.
    
    Consumes ONLY structured clinical assessment data.
    Never accesses raw text or makes external calls.
    
    Scoring Factors:
    1. Panic severity level
    2. Emotion profile (especially dissociation, dread)
    3. Distress indicator intensity
    4. Crisis protocol flags
    5. Uncertainty handling
    
    SAFETY_CRITICAL: This engine determines whether users
    receive escalated responses. All logic must be auditable.
    
    Usage:
        engine = RiskScoringEngine()
        assessment = engine.assess(clinical_assessment)
    """
    
    # Weight factors for different signals
    # CLINICAL_VALIDATION_REQUIRED
    SIGNAL_WEIGHTS = {
        "severity_critical": 0.35,
        "severity_severe": 0.25,
        "severity_moderate": 0.15,
        "emotion_dread": 0.20,
        "emotion_dissociation": 0.25,
        "emotion_helplessness": 0.15,
        "emotion_loss_of_control": 0.20,
        "high_distress": 0.20,
        "crisis_protocol_active": 0.40,
        "high_volatility": 0.15,
        "uncertainty": -0.05,  # Reduces score (conservative)
    }
    
    def __init__(
        self,
        thresholds: Optional[RiskThresholds] = None,
    ) -> None:
        """
        Initialize risk scoring engine.
        
        Args:
            thresholds: Risk threshold configuration
        """
        self.thresholds = thresholds or RiskThresholds()
    
    def assess(
        self,
        clinical: ClinicalAssessment,
        session_history: Optional[list] = None,
    ) -> RiskAssessment:
        """
        Perform risk assessment from clinical data.
        
        ARCHITECTURE: This method consumes ONLY ClinicalAssessment.
        It never accesses raw text.
        
        Args:
            clinical: Clinical assessment from Phase 2
            session_history: Optional historical assessments
            
        Returns:
            RiskAssessment with scored risk level
        """
        signals: list[RiskSignal] = []
        
        # Step 1: Extract signals from severity
        signals.extend(self._extract_severity_signals(clinical))
        
        # Step 2: Extract signals from emotion profile
        signals.extend(self._extract_emotion_signals(clinical))
        
        # Step 3: Extract signals from distress indicators
        signals.extend(self._extract_distress_signals(clinical))
        
        # Step 4: Check for crisis protocol flag
        if clinical.requires_crisis_protocol:
            signals.append(RiskSignal(
                signal_type=RiskSignalType.BEHAVIORAL,
                signal_name="crisis_protocol_active",
                description="Clinical assessment flagged crisis protocol",
                weight=self.SIGNAL_WEIGHTS["crisis_protocol_active"],
                confidence=1.0,
                source="clinical_assessment",
            ))
        
        # Step 5: Add historical signals (if available)
        if session_history:
            signals.extend(self._extract_historical_signals(session_history))
        
        # Step 6: Calculate risk score
        risk_score, confidence = self._calculate_risk_score(signals, clinical)
        
        # Step 7: Classify risk level
        risk_level = self._classify_risk_level(risk_score, signals)
        
        # Step 8: Determine recommended actions
        actions = self._determine_actions(risk_level, signals)
        
        # Step 9: Handle uncertainty
        uncertainty_reasons = []
        has_uncertainty = False
        
        if confidence < self.thresholds.low_confidence_threshold:
            has_uncertainty = True
            uncertainty_reasons.append("low_confidence")
        
        if clinical.severity.uncertainty_flag:
            has_uncertainty = True
            uncertainty_reasons.append("severity_uncertain")
        
        # SAFETY: When uncertain, be conservative
        if has_uncertainty and risk_level < RiskLevel.HIGH:
            # Bump up if uncertain and not already high
            if risk_score > 0.3:
                risk_level = max(risk_level, RiskLevel.ELEVATED)
        
        assessment = RiskAssessment(
            user_id=clinical.user_id,
            session_id=clinical.session_id,
            risk_level=risk_level,
            risk_score=risk_score,
            confidence=confidence,
            signals=signals,
            has_uncertainty=has_uncertainty,
            uncertainty_reasons=uncertainty_reasons,
            recommended_actions=actions,
            thresholds_applied={
                "critical": self.thresholds.critical_threshold,
                "high": self.thresholds.high_threshold,
                "elevated": self.thresholds.elevated_threshold,
            },
        )
        
        logger.info(
            "Risk assessment completed",
            risk_level=risk_level.name,
            risk_score=round(risk_score, 3),
            signal_count=len(signals),
            has_uncertainty=has_uncertainty,
        )
        
        return assessment
    
    def _extract_severity_signals(
        self,
        clinical: ClinicalAssessment,
    ) -> list[RiskSignal]:
        """Extract risk signals from severity classification."""
        signals = []
        severity = clinical.severity.predicted_severity
        
        if severity >= PanicSeverity.CRITICAL:
            signals.append(RiskSignal(
                signal_type=RiskSignalType.BEHAVIORAL,
                signal_name="severity_critical",
                description="Critical panic severity detected",
                weight=self.SIGNAL_WEIGHTS["severity_critical"],
                confidence=clinical.severity.confidence,
                source="panic_classifier",
            ))
        elif severity >= PanicSeverity.SEVERE:
            signals.append(RiskSignal(
                signal_type=RiskSignalType.BEHAVIORAL,
                signal_name="severity_severe",
                description="Severe panic severity detected",
                weight=self.SIGNAL_WEIGHTS["severity_severe"],
                confidence=clinical.severity.confidence,
                source="panic_classifier",
            ))
        elif severity >= PanicSeverity.MODERATE:
            signals.append(RiskSignal(
                signal_type=RiskSignalType.BEHAVIORAL,
                signal_name="severity_moderate",
                description="Moderate panic severity detected",
                weight=self.SIGNAL_WEIGHTS["severity_moderate"],
                confidence=clinical.severity.confidence,
                source="panic_classifier",
            ))
        
        return signals
    
    def _extract_emotion_signals(
        self,
        clinical: ClinicalAssessment,
    ) -> list[RiskSignal]:
        """Extract risk signals from emotion profile."""
        signals = []
        profile = clinical.emotion_profile
        
        # High-risk emotions
        risk_emotions = {
            EmotionCategory.DREAD: "emotion_dread",
            EmotionCategory.DISSOCIATION: "emotion_dissociation",
            EmotionCategory.HELPLESSNESS: "emotion_helplessness",
            EmotionCategory.LOSS_OF_CONTROL: "emotion_loss_of_control",
        }
        
        for emotion in profile.emotions:
            if emotion.category in risk_emotions and emotion.confidence > 0.5:
                signal_name = risk_emotions[emotion.category]
                signals.append(RiskSignal(
                    signal_type=RiskSignalType.EMOTIONAL,
                    signal_name=signal_name,
                    description=f"High {emotion.category.value} detected",
                    weight=self.SIGNAL_WEIGHTS.get(signal_name, 0.1),
                    confidence=emotion.confidence,
                    source="emotion_detector",
                ))
        
        # High emotional volatility
        if profile.emotional_volatility > 0.7:
            signals.append(RiskSignal(
                signal_type=RiskSignalType.EMOTIONAL,
                signal_name="high_volatility",
                description="High emotional volatility detected",
                weight=self.SIGNAL_WEIGHTS["high_volatility"],
                confidence=profile.emotional_volatility,
                source="emotion_detector",
            ))
        
        return signals
    
    def _extract_distress_signals(
        self,
        clinical: ClinicalAssessment,
    ) -> list[RiskSignal]:
        """Extract risk signals from distress indicators."""
        signals = []
        distress = clinical.distress_indicators
        
        if distress.overall_distress_level > 0.7:
            signals.append(RiskSignal(
                signal_type=RiskSignalType.BEHAVIORAL,
                signal_name="high_distress",
                description="High overall distress level",
                weight=self.SIGNAL_WEIGHTS["high_distress"],
                confidence=distress.overall_distress_level,
                source="distress_indicators",
            ))
        
        return signals
    
    def _extract_historical_signals(
        self,
        session_history: list,
    ) -> list[RiskSignal]:
        """Extract risk signals from session history."""
        signals = []
        
        # Look for escalating pattern
        if len(session_history) >= 3:
            recent = session_history[-3:]
            if all(h.get("risk_score", 0) > 0.4 for h in recent):
                # Sustained elevated risk
                signals.append(RiskSignal(
                    signal_type=RiskSignalType.HISTORICAL,
                    signal_name="sustained_risk",
                    description="Sustained elevated risk over session",
                    weight=0.15,
                    confidence=0.8,
                    source="session_history",
                ))
        
        return signals
    
    def _calculate_risk_score(
        self,
        signals: list[RiskSignal],
        clinical: ClinicalAssessment,
    ) -> tuple[float, float]:
        """
        Calculate combined risk score.
        
        Returns:
            Tuple of (risk_score, confidence)
        """
        if not signals:
            return 0.0, 1.0
        
        # Sum weighted contributions
        total_weight = sum(s.weighted_contribution() for s in signals)
        
        # Normalize to [0, 1]
        # Max possible weight is approximately sum of all weights
        max_weight = sum(abs(w) for w in self.SIGNAL_WEIGHTS.values())
        risk_score = min(1.0, total_weight / max_weight)
        
        # Calculate confidence (average of signal confidences)
        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        
        # Weight by clinical confidence
        combined_confidence = (avg_confidence + clinical.confidence_score) / 2
        
        return risk_score, combined_confidence
    
    def _classify_risk_level(
        self,
        risk_score: float,
        signals: list[RiskSignal],
    ) -> RiskLevel:
        """
        Classify risk level from score.
        
        SAFETY_CRITICAL: Uses both score thresholds AND
        multi-signal requirements.
        """
        signal_count = len(signals)
        signal_types = len(set(s.signal_type for s in signals))
        
        # CRITICAL: High score AND multiple signal types AND sufficient signals
        if risk_score >= self.thresholds.critical_threshold:
            if signal_count >= self.thresholds.min_signals_for_critical:
                if not self.thresholds.require_multi_signal_types or signal_types >= 2:
                    return RiskLevel.CRITICAL
                else:
                    # Downgrade if only one signal type
                    return RiskLevel.HIGH
            else:
                return RiskLevel.HIGH
        
        # HIGH: Elevated score AND multiple signals
        if risk_score >= self.thresholds.high_threshold:
            if signal_count >= self.thresholds.min_signals_for_high:
                return RiskLevel.HIGH
            else:
                return RiskLevel.ELEVATED
        
        # ELEVATED: Moderate score
        if risk_score >= self.thresholds.elevated_threshold:
            return RiskLevel.ELEVATED
        
        return RiskLevel.LOW
    
    def _determine_actions(
        self,
        risk_level: RiskLevel,
        signals: list[RiskSignal],
    ) -> list[EscalationAction]:
        """Determine recommended actions based on risk level."""
        actions = []
        
        if risk_level == RiskLevel.LOW:
            actions.append(EscalationAction.CONTINUE_SUPPORT)
        
        elif risk_level == RiskLevel.ELEVATED:
            actions.append(EscalationAction.CONTINUE_SUPPORT)
            actions.append(EscalationAction.LOG_FOR_REVIEW)
        
        elif risk_level == RiskLevel.HIGH:
            actions.append(EscalationAction.ENCOURAGE_HELP)
            actions.append(EscalationAction.PRESENT_RESOURCES)
            actions.append(EscalationAction.LOG_FOR_REVIEW)
        
        elif risk_level == RiskLevel.CRITICAL:
            actions.append(EscalationAction.PRESENT_RESOURCES)
            actions.append(EscalationAction.ENCOURAGE_HELP)
            actions.append(EscalationAction.LOG_FOR_REVIEW)
        
        return actions
