"""
Integration Tests - Panic Flow

Tests the complete panic detection → decision → response pipeline.
Verifies safety validations are applied to all responses.
"""

import pytest
from datetime import datetime
from uuid import uuid4

from hope.domain.models.clinical_output import (
    ClinicalAssessment,
    SeverityClassification,
    EmotionProfile,
    DistressIndicators,
    TriggerAnalysis,
)
from hope.domain.enums.panic_severity import PanicSeverity
from hope.services.safety.safety_pipeline import SafetyPipeline, SafetyEvaluation
from hope.services.safety.risk_engine import RiskScoringEngine
from hope.services.decision.decision_engine import DecisionEngine


class TestPanicFlowIntegration:
    """Integration tests for complete panic flow."""
    
    @pytest.fixture
    def clinical_assessment_low(self) -> ClinicalAssessment:
        """Low severity clinical assessment."""
        return ClinicalAssessment(
            assessment_id=uuid4(),
            user_id=uuid4(),
            session_id=uuid4(),
            timestamp=datetime.utcnow(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MILD,
                confidence=0.85,
                severity_probabilities={
                    PanicSeverity.NONE: 0.1,
                    PanicSeverity.MILD: 0.7,
                    PanicSeverity.MODERATE: 0.15,
                    PanicSeverity.SEVERE: 0.04,
                    PanicSeverity.CRITICAL: 0.01,
                },
            ),
            emotions=EmotionProfile(
                primary_emotion="mild_anxiety",
                emotion_scores={
                    "fear": 0.3,
                    "anxiety": 0.4,
                    "dread": 0.1,
                },
                emotional_intensity=0.35,
            ),
            distress=DistressIndicators(
                overall_distress_level=0.3,
                physical_distress=0.2,
                cognitive_distress=0.3,
                emotional_distress=0.35,
                behavioral_distress=0.2,
            ),
            triggers=TriggerAnalysis(
                detected_triggers=[],
                trigger_confidence=0.0,
            ),
            requires_crisis_protocol=False,
            clinical_uncertainty_flags=[],
        )
    
    @pytest.fixture
    def clinical_assessment_critical(self) -> ClinicalAssessment:
        """Critical severity clinical assessment."""
        return ClinicalAssessment(
            assessment_id=uuid4(),
            user_id=uuid4(),
            session_id=uuid4(),
            timestamp=datetime.utcnow(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.CRITICAL,
                confidence=0.9,
                severity_probabilities={
                    PanicSeverity.NONE: 0.0,
                    PanicSeverity.MILD: 0.02,
                    PanicSeverity.MODERATE: 0.05,
                    PanicSeverity.SEVERE: 0.13,
                    PanicSeverity.CRITICAL: 0.8,
                },
            ),
            emotions=EmotionProfile(
                primary_emotion="severe_dread",
                emotion_scores={
                    "fear": 0.9,
                    "dread": 0.85,
                    "helplessness": 0.8,
                    "dissociation": 0.6,
                },
                emotional_intensity=0.9,
            ),
            distress=DistressIndicators(
                overall_distress_level=0.9,
                physical_distress=0.85,
                cognitive_distress=0.9,
                emotional_distress=0.95,
                behavioral_distress=0.8,
            ),
            triggers=TriggerAnalysis(
                detected_triggers=["trauma_reminder"],
                trigger_confidence=0.85,
            ),
            requires_crisis_protocol=True,
            clinical_uncertainty_flags=[],
        )
    
    @pytest.fixture
    def safety_pipeline(self) -> SafetyPipeline:
        """Safety pipeline instance."""
        return SafetyPipeline()
    
    @pytest.fixture
    def risk_engine(self) -> RiskScoringEngine:
        """Risk scoring engine instance."""
        return RiskScoringEngine()
    
    def test_low_severity_continues_support(
        self,
        clinical_assessment_low: ClinicalAssessment,
        safety_pipeline: SafetyPipeline,
    ):
        """Low severity should continue normal support."""
        response = "I'm here with you. Let's take a moment to breathe together."
        
        evaluation = safety_pipeline.evaluate(
            clinical=clinical_assessment_low,
            proposed_response=response,
        )
        
        assert evaluation.response_valid
        assert not evaluation.requires_crisis_response
        assert evaluation.final_risk_level.name in ["LOW", "ELEVATED"]
    
    def test_critical_severity_includes_resources(
        self,
        clinical_assessment_critical: ClinicalAssessment,
        safety_pipeline: SafetyPipeline,
    ):
        """Critical severity should include crisis resources."""
        response = "I hear you. This sounds really difficult."
        
        evaluation = safety_pipeline.evaluate(
            clinical=clinical_assessment_critical,
            proposed_response=response,
            country_code="US",
        )
        
        # Should either modify response or flag for resources
        assert evaluation.requires_crisis_response or evaluation.response_was_modified
    
    def test_unsafe_response_blocked(
        self,
        clinical_assessment_low: ClinicalAssessment,
        safety_pipeline: SafetyPipeline,
    ):
        """Unsafe responses should be blocked or modified."""
        # This response gives medical advice - should be blocked
        unsafe_response = "You should take some Xanax to calm down."
        
        evaluation = safety_pipeline.evaluate(
            clinical=clinical_assessment_low,
            proposed_response=unsafe_response,
        )
        
        # Response should be modified or blocked
        assert not evaluation.response_valid or evaluation.response_was_modified
        # Original unsafe content should not be in final response
        assert "Xanax" not in evaluation.final_response
    
    def test_risk_scoring_multi_signal(
        self,
        clinical_assessment_critical: ClinicalAssessment,
        risk_engine: RiskScoringEngine,
    ):
        """Critical assessment should produce multiple risk signals."""
        assessment = risk_engine.assess(clinical_assessment_critical)
        
        # Should have multiple signals for critical
        assert len(assessment.signals) >= 2
        # Should have high confidence due to multiple signals
        assert assessment.confidence >= 0.5
    
    def test_escalation_produces_audit_trail(
        self,
        clinical_assessment_critical: ClinicalAssessment,
        safety_pipeline: SafetyPipeline,
    ):
        """Escalations should produce audit trail."""
        response = "I'm here for you."
        
        evaluation = safety_pipeline.evaluate(
            clinical=clinical_assessment_critical,
            proposed_response=response,
        )
        
        # Should have audit trail
        assert len(evaluation.audit_trail) > 0
        # Trail should include risk assessment
        assert any("risk" in entry.lower() for entry in evaluation.audit_trail)


class TestSafetyPipelineIntegration:
    """Integration tests for safety pipeline components."""
    
    def test_pipeline_never_returns_empty(self):
        """Safety pipeline should never return empty response."""
        pipeline = SafetyPipeline()
        
        # Minimal clinical assessment
        clinical = ClinicalAssessment(
            assessment_id=uuid4(),
            user_id=uuid4(),
            session_id=uuid4(),
            timestamp=datetime.utcnow(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MODERATE,
                confidence=0.7,
            ),
            emotions=EmotionProfile(
                primary_emotion="anxiety",
                emotional_intensity=0.5,
            ),
            distress=DistressIndicators(
                overall_distress_level=0.5,
            ),
            triggers=TriggerAnalysis(),
            requires_crisis_protocol=False,
        )
        
        # Even with blocked response, should have fallback
        evaluation = pipeline.evaluate(
            clinical=clinical,
            proposed_response="",  # Empty response
        )
        
        # Should have some response
        assert len(evaluation.final_response) > 0
    
    def test_safety_validation_chain(self):
        """All safety validators should run in sequence."""
        pipeline = SafetyPipeline()
        
        clinical = ClinicalAssessment(
            assessment_id=uuid4(),
            user_id=uuid4(),
            session_id=uuid4(),
            timestamp=datetime.utcnow(),
            severity=SeverityClassification(
                predicted_severity=PanicSeverity.MILD,
                confidence=0.8,
            ),
            emotions=EmotionProfile(
                primary_emotion="worry",
                emotional_intensity=0.3,
            ),
            distress=DistressIndicators(
                overall_distress_level=0.3,
            ),
            triggers=TriggerAnalysis(),
            requires_crisis_protocol=False,
        )
        
        # Safe response
        evaluation = pipeline.evaluate(
            clinical=clinical,
            proposed_response="I understand you're feeling worried. Let's work through this together.",
        )
        
        # Should pass validation
        assert evaluation.response_valid
        # Should have gone through full pipeline
        assert len(evaluation.audit_trail) >= 1
