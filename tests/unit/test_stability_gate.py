"""
Unit Tests for Stability Gate

Tests all stability state derivation rules.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from hope.services.safety.stability_gate import (
    PanicStabilityState,
    StabilityContext,
    StabilityGate,
    StabilityEvaluation,
)
from hope.domain.enums.panic_severity import PanicSeverity


@pytest.fixture
def stability_gate():
    return StabilityGate()


@pytest.fixture
def base_context():
    """Create a base context for testing."""
    return StabilityContext(
        session_id=uuid4(),
        user_id=uuid4(),
        started_at=datetime.utcnow() - timedelta(seconds=30),
        current_severity=PanicSeverity.MODERATE,
        current_intensity=0.5,
        severity_history=[PanicSeverity.SEVERE, PanicSeverity.MODERATE],
        intensity_history=[0.7, 0.5],
        breathing_cycles_completed=0,
        grounding_steps_completed=0,
        has_crisis_signals=False,
        has_self_harm_signals=False,
    )


class TestPanicCriticalState:
    """Tests for PANIC_CRITICAL state detection."""
    
    def test_crisis_signals_yields_critical(self, stability_gate, base_context):
        """Crisis signals should always yield CRITICAL."""
        base_context.has_crisis_signals = True
        base_context.current_severity = PanicSeverity.MILD
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_CRITICAL
        assert "Crisis" in result.reason
    
    def test_self_harm_signals_yields_critical(self, stability_gate, base_context):
        """Self-harm signals should always yield CRITICAL."""
        base_context.has_self_harm_signals = True
        base_context.current_severity = PanicSeverity.MILD
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_CRITICAL
    
    def test_critical_severity_yields_critical(self, stability_gate, base_context):
        """CRITICAL severity should yield CRITICAL state."""
        base_context.current_severity = PanicSeverity.CRITICAL
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_CRITICAL


class TestPanicActiveState:
    """Tests for PANIC_ACTIVE state detection."""
    
    def test_insufficient_time_yields_active(self, stability_gate, base_context):
        """Under 60 seconds should yield ACTIVE."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=30)
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_ACTIVE
        assert "60s" in result.reason
    
    def test_no_exercise_yields_active(self, stability_gate, base_context):
        """No exercise completion should yield ACTIVE."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=120)
        base_context.breathing_cycles_completed = 0
        base_context.grounding_steps_completed = 0
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_ACTIVE
        assert "exercise" in result.reason.lower()
    
    def test_severe_without_improvement_yields_active(self, stability_gate, base_context):
        """SEVERE severity without improvement should yield ACTIVE."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=120)
        base_context.current_severity = PanicSeverity.SEVERE
        base_context.severity_history = [PanicSeverity.SEVERE, PanicSeverity.SEVERE]
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_ACTIVE


class TestPanicStabilizingState:
    """Tests for PANIC_STABILIZING state detection."""
    
    def test_exercise_completed_yields_stabilizing(self, stability_gate, base_context):
        """Exercise completion with time should yield STABILIZING."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=90)
        base_context.breathing_cycles_completed = 4
        base_context.current_severity = PanicSeverity.MODERATE
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_STABILIZING
    
    def test_grounding_completed_yields_stabilizing(self, stability_gate, base_context):
        """Grounding completion should yield STABILIZING."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=90)
        base_context.grounding_steps_completed = 5
        base_context.current_severity = PanicSeverity.MODERATE
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_STABILIZING


class TestPanicRecoveredState:
    """Tests for PANIC_RECOVERED state detection."""
    
    def test_full_recovery_yields_recovered(self, stability_gate, base_context):
        """Full recovery criteria should yield RECOVERED."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=200)
        base_context.breathing_cycles_completed = 5
        base_context.current_severity = PanicSeverity.MILD
        base_context.current_intensity = 0.3
        base_context.intensity_history = [0.7, 0.5, 0.3]
        base_context.severity_history = [
            PanicSeverity.SEVERE, 
            PanicSeverity.MODERATE, 
            PanicSeverity.MILD
        ]
        
        result = stability_gate.evaluate(base_context)
        
        assert result.state == PanicStabilityState.PANIC_RECOVERED


class TestAuditLog:
    """Tests for audit log generation."""
    
    def test_audit_log_no_pii(self, stability_gate, base_context):
        """Audit log should not contain PII."""
        result = stability_gate.evaluate(base_context)
        audit = result.to_audit_log()
        
        # Should have state but no user identifying info
        assert "state" in audit
        assert "timestamp" in audit
        assert "user_id" not in audit
        assert "session_id" not in audit


class TestContextProperties:
    """Tests for StabilityContext computed properties."""
    
    def test_elapsed_seconds(self, base_context):
        """elapsed_seconds should calculate correctly."""
        base_context.started_at = datetime.utcnow() - timedelta(seconds=60)
        
        # Allow small margin for test execution
        assert 59 <= base_context.elapsed_seconds <= 61
    
    def test_has_completed_exercise_breathing(self, base_context):
        """has_completed_exercise should detect breathing."""
        base_context.breathing_cycles_completed = 3
        assert base_context.has_completed_exercise is True
    
    def test_has_completed_exercise_grounding(self, base_context):
        """has_completed_exercise should detect grounding."""
        base_context.grounding_steps_completed = 3
        assert base_context.has_completed_exercise is True
    
    def test_has_completed_exercise_none(self, base_context):
        """has_completed_exercise should be False if none completed."""
        base_context.breathing_cycles_completed = 0
        base_context.grounding_steps_completed = 0
        assert base_context.has_completed_exercise is False
    
    def test_severity_trend_improving(self, base_context):
        """severity_trend should be negative when improving."""
        base_context.severity_history = [
            PanicSeverity.SEVERE, 
            PanicSeverity.MODERATE, 
            PanicSeverity.MILD
        ]
        
        assert base_context.severity_trend < 0
    
    def test_severity_trend_worsening(self, base_context):
        """severity_trend should be positive when worsening."""
        base_context.severity_history = [
            PanicSeverity.MILD, 
            PanicSeverity.MODERATE, 
            PanicSeverity.SEVERE
        ]
        
        assert base_context.severity_trend > 0
