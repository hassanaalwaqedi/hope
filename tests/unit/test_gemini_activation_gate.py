"""
Unit Tests for Gemini Activation Gate

Tests all activation rules and safety constraints.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from hope.services.llm.gemini_activation_gate import (
    GeminiActivationGate,
    ActivationDecision,
    ActivationDenialReason,
)
from hope.services.safety.stability_gate import (
    StabilityContext,
    PanicStabilityState,
)
from hope.domain.enums.panic_severity import PanicSeverity


@pytest.fixture
def activation_gate():
    return GeminiActivationGate()


@pytest.fixture
def allowed_context():
    """Create a context that should ALLOW Gemini activation."""
    return StabilityContext(
        session_id=uuid4(),
        user_id=uuid4(),
        started_at=datetime.utcnow() - timedelta(seconds=120),  # 2 minutes
        current_severity=PanicSeverity.MILD,
        current_intensity=0.3,
        severity_history=[PanicSeverity.MODERATE, PanicSeverity.MILD],
        intensity_history=[0.6, 0.3],
        breathing_cycles_completed=4,  # Exercise completed
        grounding_steps_completed=0,
        has_crisis_signals=False,
        has_self_harm_signals=False,
    )


@pytest.fixture
def blocked_context():
    """Create a context that should BLOCK Gemini activation."""
    return StabilityContext(
        session_id=uuid4(),
        user_id=uuid4(),
        started_at=datetime.utcnow() - timedelta(seconds=30),  # Only 30 seconds
        current_severity=PanicSeverity.SEVERE,
        current_intensity=0.8,
        severity_history=[PanicSeverity.SEVERE],
        intensity_history=[0.8],
        breathing_cycles_completed=0,
        grounding_steps_completed=0,
        has_crisis_signals=False,
        has_self_harm_signals=False,
    )


class TestActivationBlocking:
    """Tests for Gemini activation being BLOCKED."""
    
    def test_crisis_signals_blocks(self, activation_gate, allowed_context):
        """Crisis signals should block activation."""
        allowed_context.has_crisis_signals = True
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is False
        assert decision.denial_reason == ActivationDenialReason.CRISIS_SIGNALS
    
    def test_self_harm_signals_blocks(self, activation_gate, allowed_context):
        """Self-harm signals should block activation."""
        allowed_context.has_self_harm_signals = True
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is False
        assert decision.denial_reason == ActivationDenialReason.CRISIS_SIGNALS
    
    def test_time_threshold_blocks(self, activation_gate, allowed_context):
        """Insufficient time should block activation."""
        allowed_context.started_at = datetime.utcnow() - timedelta(seconds=30)
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is False
        assert decision.denial_reason == ActivationDenialReason.TIME_THRESHOLD_NOT_MET
    
    def test_no_exercise_blocks(self, activation_gate, allowed_context):
        """No exercise completion should block activation."""
        allowed_context.breathing_cycles_completed = 0
        allowed_context.grounding_steps_completed = 0
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is False
        assert decision.denial_reason == ActivationDenialReason.NO_EXERCISE_COMPLETED


class TestActivationAllowing:
    """Tests for Gemini activation being ALLOWED."""
    
    def test_all_conditions_met_allows(self, activation_gate, allowed_context):
        """All conditions met should allow activation."""
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is True
        assert decision.denial_reason is None
    
    def test_grounding_counts_as_exercise(self, activation_gate, allowed_context):
        """Grounding completion should count as exercise."""
        allowed_context.breathing_cycles_completed = 0
        allowed_context.grounding_steps_completed = 5
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is True


class TestKillSwitch:
    """Tests for Gemini kill-switch."""
    
    def test_disable_blocks_all(self, activation_gate, allowed_context):
        """Disable should block all activation."""
        activation_gate.disable()
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is False
        assert decision.denial_reason == ActivationDenialReason.GEMINI_DISABLED
    
    def test_enable_allows_again(self, activation_gate, allowed_context):
        """Enable should allow activation again."""
        activation_gate.disable()
        activation_gate.enable()
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is True


class TestErrorThreshold:
    """Tests for error threshold auto-disable."""
    
    def test_errors_accumulate(self, activation_gate, allowed_context):
        """Errors should accumulate per session."""
        session_id = str(allowed_context.session_id)
        
        activation_gate.record_error(session_id)
        activation_gate.record_error(session_id)
        
        # Still below threshold
        decision = activation_gate.is_allowed(allowed_context)
        assert decision.allowed is True
    
    def test_error_threshold_blocks(self, activation_gate, allowed_context):
        """Exceeding error threshold should block."""
        session_id = str(allowed_context.session_id)
        
        # Exceed threshold
        for _ in range(4):
            activation_gate.record_error(session_id)
        
        decision = activation_gate.is_allowed(allowed_context)
        
        assert decision.allowed is False
        assert decision.denial_reason == ActivationDenialReason.ERROR_THRESHOLD_EXCEEDED
    
    def test_clear_session_resets_errors(self, activation_gate, allowed_context):
        """Clearing session should reset error count."""
        session_id = str(allowed_context.session_id)
        
        # Exceed threshold
        for _ in range(4):
            activation_gate.record_error(session_id)
        
        activation_gate.clear_session(session_id)
        
        decision = activation_gate.is_allowed(allowed_context)
        assert decision.allowed is True


class TestAuditLog:
    """Tests for audit log generation."""
    
    def test_decision_to_audit_log(self, activation_gate, allowed_context):
        """Decision should generate proper audit log."""
        decision = activation_gate.is_allowed(allowed_context)
        audit = decision.to_audit_log()
        
        assert "allowed" in audit
        assert "reason" in audit
        assert "timestamp" in audit
        # No PII
        assert "user_id" not in str(audit)
        assert "session_id" not in str(audit)


class TestPriorityOrder:
    """Tests for condition check priority."""
    
    def test_crisis_checked_before_time(self, activation_gate, blocked_context):
        """Crisis should be checked before time threshold."""
        blocked_context.has_crisis_signals = True
        
        decision = activation_gate.is_allowed(blocked_context)
        
        # Should report crisis, not time
        assert decision.denial_reason == ActivationDenialReason.CRISIS_SIGNALS
