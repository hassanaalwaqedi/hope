"""
Unit Tests for Clinical Pipeline

Tests the clinical intelligence layer components.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from hope.domain.enums.panic_severity import PanicSeverity
from hope.domain.models.clinical_output import (
    ClinicalAssessment,
    SeverityClassification,
    EmotionProfile,
    EmotionScore,
    EmotionCategory,
    DistressIndicators,
    TriggerAnalysis,
)
from hope.services.decision.decision_engine import (
    DecisionEngine,
    DecisionContext,
    ResponseStrategy,
    ResponseTone,
)


class TestSeverityClassification:
    """Tests for SeverityClassification model."""
    
    def test_uncertainty_flag_low_confidence(self) -> None:
        """Test that low confidence triggers uncertainty flag."""
        classification = SeverityClassification(
            predicted_severity=PanicSeverity.MODERATE,
            confidence=0.4,
        )
        assert classification.uncertainty_flag is True
    
    def test_uncertainty_flag_high_confidence(self) -> None:
        """Test that high confidence does not trigger uncertainty."""
        classification = SeverityClassification(
            predicted_severity=PanicSeverity.MODERATE,
            confidence=0.85,
            probabilities={
                PanicSeverity.NONE: 0.05,
                PanicSeverity.MILD: 0.05,
                PanicSeverity.MODERATE: 0.85,
                PanicSeverity.SEVERE: 0.04,
                PanicSeverity.CRITICAL: 0.01,
            }
        )
        assert classification.uncertainty_flag is False
    
    def test_uncertainty_flag_close_probabilities(self) -> None:
        """Test uncertainty when top probabilities are close."""
        classification = SeverityClassification(
            predicted_severity=PanicSeverity.MODERATE,
            confidence=0.45,
            probabilities={
                PanicSeverity.MILD: 0.40,
                PanicSeverity.MODERATE: 0.45,
            }
        )
        assert classification.uncertainty_flag is True


class TestEmotionProfile:
    """Tests for EmotionProfile model."""
    
    def test_dominant_emotion_auto_set(self) -> None:
        """Test that dominant emotion is auto-set from highest confidence."""
        profile = EmotionProfile(
            emotions=[
                EmotionScore(category=EmotionCategory.FEAR, confidence=0.6),
                EmotionScore(category=EmotionCategory.DREAD, confidence=0.8),
                EmotionScore(category=EmotionCategory.HELPLESSNESS, confidence=0.3),
            ]
        )
        assert profile.dominant_emotion == EmotionCategory.DREAD
    
    def test_get_emotion_score(self) -> None:
        """Test getting score for specific emotion."""
        profile = EmotionProfile(
            emotions=[
                EmotionScore(category=EmotionCategory.FEAR, confidence=0.7),
            ]
        )
        assert profile.get_emotion_score(EmotionCategory.FEAR) == 0.7
        assert profile.get_emotion_score(EmotionCategory.DREAD) == 0.0
    
    def test_high_confidence_detection(self) -> None:
        """Test high confidence threshold check."""
        profile = EmotionProfile(
            emotions=[
                EmotionScore(category=EmotionCategory.FEAR, confidence=0.8),
            ]
        )
        assert profile.has_high_confidence(threshold=0.7) is True
        assert profile.has_high_confidence(threshold=0.9) is False


class TestClinicalAssessment:
    """Tests for ClinicalAssessment model."""
    
    def test_crisis_protocol_auto_set(self) -> None:
        """Test that crisis protocol is auto-set for critical severity."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.CRITICAL,
                confidence=0.9,
            ),
        )
        assert assessment.requires_crisis_protocol is True
    
    def test_human_review_on_uncertainty(self) -> None:
        """Test that human review is flagged on uncertainty."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.4,  # Low confidence triggers uncertainty
            ),
        )
        assert assessment.requires_human_review is True
    
    def test_panic_detected(self) -> None:
        """Test panic detection check."""
        no_panic = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.NONE,
                confidence=0.9,
            ),
        )
        assert no_panic.is_panic_detected() is False
        
        has_panic = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MILD,
                confidence=0.7,
            ),
        )
        assert has_panic.is_panic_detected() is True
    
    def test_serialization(self) -> None:
        """Test to_dict serialization."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.7,
            ),
        )
        data = assessment.to_dict()
        
        assert "assessment_id" in data
        assert "severity" in data
        assert data["severity"]["predicted_severity"] == "MODERATE"


class TestDecisionEngineWithClinicalAssessment:
    """Tests for DecisionEngine using ClinicalAssessment."""
    
    @pytest.fixture
    def engine(self) -> DecisionEngine:
        return DecisionEngine()
    
    @pytest.fixture
    def base_assessment(self) -> ClinicalAssessment:
        return ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.7,
            ),
        )
    
    def test_crisis_protocol_triggers_crisis_decision(self, engine: DecisionEngine) -> None:
        """Test that crisis protocol triggers crisis response."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.CRITICAL,
                confidence=0.9,
            ),
            requires_crisis_protocol=True,
        )
        
        context = DecisionContext(
            user_id=assessment.user_id,
            clinical_assessment=assessment,
        )
        
        decision = engine.decide(context)
        
        assert decision.strategy == ResponseStrategy.CRISIS
        assert decision.escalate_to_crisis is True
    
    def test_severity_maps_to_strategy(self, engine: DecisionEngine) -> None:
        """Test that severity levels map to correct strategies."""
        test_cases = [
            (PanicSeverity.NONE, ResponseStrategy.CHECK_IN),
            (PanicSeverity.MILD, ResponseStrategy.ACKNOWLEDGE),
            (PanicSeverity.MODERATE, ResponseStrategy.GROUND),
            (PanicSeverity.SEVERE, ResponseStrategy.INTERVENE),
        ]
        
        for severity, expected_strategy in test_cases:
            assessment = ClinicalAssessment(
                user_id=uuid4(),
                severity=SeverityClassification(
                    predicted_severity=severity,
                    confidence=0.7,
                ),
            )
            context = DecisionContext(
                user_id=assessment.user_id,
                clinical_assessment=assessment,
            )
            
            decision = engine.decide(context)
            assert decision.strategy == expected_strategy, f"Failed for {severity}"
    
    def test_dissociation_changes_tone(self, engine: DecisionEngine) -> None:
        """Test that dissociation emotion changes tone to direct."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.7,
            ),
            emotion_profile=EmotionProfile(
                emotions=[
                    EmotionScore(
                        category=EmotionCategory.DISSOCIATION,
                        confidence=0.8,
                        is_primary=True,
                    )
                ],
                dominant_emotion=EmotionCategory.DISSOCIATION,
            ),
        )
        
        context = DecisionContext(
            user_id=assessment.user_id,
            clinical_assessment=assessment,
        )
        
        decision = engine.decide(context)
        assert decision.tone == ResponseTone.DIRECT
    
    def test_clinical_modifiers_include_emotion(
        self, 
        engine: DecisionEngine,
    ) -> None:
        """Test that clinical modifiers include emotion context."""
        assessment = ClinicalAssessment(
            user_id=uuid4(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.7,
            ),
            emotion_profile=EmotionProfile(
                emotions=[
                    EmotionScore(
                        category=EmotionCategory.FEAR,
                        confidence=0.8,
                    )
                ],
                dominant_emotion=EmotionCategory.FEAR,
            ),
        )
        
        context = DecisionContext(
            user_id=assessment.user_id,
            clinical_assessment=assessment,
        )
        
        decision = engine.decide(context)
        assert "dominant_emotion" in decision.prompt_modifiers
        assert decision.prompt_modifiers["dominant_emotion"] == "fear"
