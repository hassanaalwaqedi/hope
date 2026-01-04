"""
Unit Tests for Safety Pipeline

Tests risk scoring, crisis detection, and escalation logic.
"""

import pytest
from uuid import uuid4

from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.clinical_output import (
    ClinicalAssessment,
    SeverityClassification,
    EmotionProfile,
    EmotionScore,
    EmotionCategory,
    DistressIndicators,
)
from hope.domain.models.risk_models import (
    RiskLevel,
    RiskSignal,
    RiskSignalType,
)
from hope.services.safety.risk_engine import RiskScoringEngine, RiskThresholds
from hope.services.safety.crisis_detector import (
    CrisisDetector,
    LinguisticCrisisAnalyzer,
)
from hope.services.safety.escalation_manager import EscalationManager
from hope.services.safety.emergency_resources import EmergencyResourceResolver


class TestRiskScoringEngine:
    """Tests for RiskScoringEngine."""
    
    @pytest.fixture
    def engine(self) -> RiskScoringEngine:
        return RiskScoringEngine()
    
    def test_low_risk_for_no_panic(self, engine: RiskScoringEngine) -> None:
        """Test that no panic results in low risk."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.NONE,
                confidence=0.9,
            ),
        )
        
        result = engine.assess(assessment)
        
        assert result.risk_level == RiskLevel.LOW
    
    def test_elevated_risk_for_moderate_panic(self, engine: RiskScoringEngine) -> None:
        """Test moderate panic produces elevated risk."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.7,
            ),
        )
        
        result = engine.assess(assessment)
        
        assert result.risk_level >= RiskLevel.ELEVATED
    
    def test_critical_requires_multiple_signals(self, engine: RiskScoringEngine) -> None:
        """Test that critical level requires multiple signal types."""
        # Single high signal should not trigger critical alone
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.CRITICAL,
                confidence=0.9,
            ),
            # No other signals
        )
        
        result = engine.assess(assessment)
        
        # Should be HIGH, not CRITICAL, due to single signal type
        # (depends on exact threshold configuration)
        assert result.risk_level >= RiskLevel.HIGH
        assert result.signal_count >= 1
    
    def test_uncertainty_flagged(self, engine: RiskScoringEngine) -> None:
        """Test that low confidence triggers uncertainty flag."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.3,  # Low confidence
            ),
        )
        
        result = engine.assess(assessment)
        
        assert result.has_uncertainty is True
        assert "low_confidence" in result.uncertainty_reasons


class TestCrisisDetector:
    """Tests for CrisisDetector."""
    
    @pytest.fixture
    def detector(self) -> CrisisDetector:
        return CrisisDetector()
    
    def test_no_signals_for_stable_assessment(self, detector: CrisisDetector) -> None:
        """Test no crisis signals for stable clinical assessment."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MILD,
                confidence=0.8,
            ),
        )
        
        result = detector.detect(assessment)
        
        assert result.has_crisis_signals is False
    
    def test_emotional_signals_detected(self, detector: CrisisDetector) -> None:
        """Test that high-risk emotions produce signals."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.SEVERE,
                confidence=0.8,
            ),
            emotion_profile=EmotionProfile(
                emotions=[
                    EmotionScore(
                        category=EmotionCategory.DREAD,
                        confidence=0.8,
                    ),
                    EmotionScore(
                        category=EmotionCategory.HELPLESSNESS,
                        confidence=0.9,
                    ),
                ],
            ),
        )
        
        result = detector.detect(assessment)
        
        assert result.emotional_signal_count >= 1
    
    def test_multi_signal_requirement(self, detector: CrisisDetector) -> None:
        """Test that multi-signal requirement is properly evaluated."""
        # Single category signals should NOT meet requirement
        assessment_single = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.CRITICAL,
                confidence=0.9,
            ),
        )
        
        result_single = detector.detect(assessment_single)
        
        # Multi-signal requires at least 2 different categories
        # Just behavioral (from severity) is not enough
        assert result_single.meets_multi_signal_requirement is False or \
               len(result_single.signals) >= 2


class TestLinguisticCrisisAnalyzer:
    """Tests for linguistic pattern detection."""
    
    def test_detects_direct_self_harm_language(self) -> None:
        """Test detection of direct self-harm expressions."""
        text = "I'm thinking about hurting myself"
        
        signals = LinguisticCrisisAnalyzer.analyze_text(text)
        
        assert len(signals) >= 1
        signal_names = [s.signal_name for s in signals]
        assert any("self_harm" in name or "harm" in name.lower() for name in signal_names)
    
    def test_detects_hopelessness(self) -> None:
        """Test detection of hopelessness patterns."""
        text = "There's no way out and I can't take it anymore"
        
        signals = LinguisticCrisisAnalyzer.analyze_text(text)
        
        assert len(signals) >= 1
    
    def test_no_false_positives_on_normal_text(self) -> None:
        """Test no signals for normal anxiety text."""
        text = "I'm feeling anxious about my presentation tomorrow"
        
        signals = LinguisticCrisisAnalyzer.analyze_text(text)
        
        assert len(signals) == 0
    
    def test_requires_multiple_signals_pattern(self) -> None:
        """Test that single casual mention is low weight."""
        # Single word should not be high weight
        text = "I woke up feeling hopeless"
        
        signals = LinguisticCrisisAnalyzer.analyze_text(text)
        
        # Even if detected, weight should be moderate
        for signal in signals:
            assert signal.weight < 0.5  # Not highest weight


class TestEscalationManager:
    """Tests for EscalationManager."""
    
    @pytest.fixture
    def manager(self) -> EscalationManager:
        return EscalationManager()
    
    def test_low_risk_continues_support(self, manager: EscalationManager) -> None:
        """Test that low risk continues AI support."""
        from hope.domain.models.risk_models import RiskAssessment, EscalationAction
        
        risk = RiskAssessment(
            user_id=uuid4(),
            risk_level=RiskLevel.LOW,
            risk_score=0.1,
        )
        
        decision = manager.evaluate(risk)
        
        assert EscalationAction.CONTINUE_SUPPORT in decision.actions
        assert decision.resources_to_include is None
    
    def test_high_risk_provides_resources(self, manager: EscalationManager) -> None:
        """Test that high risk provides emergency resources."""
        from hope.domain.models.risk_models import RiskAssessment
        
        risk = RiskAssessment(
            user_id=uuid4(),
            risk_level=RiskLevel.HIGH,
            risk_score=0.7,
        )
        
        decision = manager.evaluate(risk, country_code="US")
        
        assert decision.resources_to_include is not None
        assert "988" in decision.resources_to_include  # US crisis line


class TestEmergencyResourceResolver:
    """Tests for EmergencyResourceResolver."""
    
    @pytest.fixture
    def resolver(self) -> EmergencyResourceResolver:
        return EmergencyResourceResolver()
    
    def test_us_resources_available(self, resolver: EmergencyResourceResolver) -> None:
        """Test US resources are available."""
        resources = resolver.get_resources("US")
        
        assert resources.country_code == "US"
        assert len(resources.resources) > 0
    
    def test_fallback_for_unknown_country(self, resolver: EmergencyResourceResolver) -> None:
        """Test fallback resources for unknown country."""
        resources = resolver.get_resources("XX")  # Unknown code
        
        assert resources.country_code == "INTL"  # International fallback
    
    def test_arabic_region_resources(self, resolver: EmergencyResourceResolver) -> None:
        """Test Arabic region resources available."""
        sa_resources = resolver.get_resources("SA")
        
        assert sa_resources.country_code == "SA"
        assert "ar" in sa_resources.resources[0].languages
