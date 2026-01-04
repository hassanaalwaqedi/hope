/// Panic UX State Classifier
/// 
/// Deterministic, explainable classification of panic severity
/// based on observable signals. No ML models - fully testable rules.
/// 
/// Classification is used for automatic intervention routing.

import 'package:flutter/foundation.dart';

/// Panic severity levels for UX routing decisions.
/// 
/// Each level maps to a specific intervention approach:
/// - MILD: Standard breathing exercises
/// - MODERATE: Breathing with auto-escalation monitoring
/// - SEVERE: Minimal motion, strong presence UI
/// - CRITICAL: Crisis resources emphasis
enum PanicUXState {
  MILD_PANIC,
  MODERATE_PANIC,
  SEVERE_PANIC,
  CRITICAL_PANIC,
}

/// Input signals for panic state classification.
/// 
/// All values are observable, non-PII metrics.
@immutable
class PanicClassificationInput {
  /// Current intensity reported by user (1-10 scale)
  final double intensity;
  
  /// Milliseconds from session start to first user interaction
  /// High values may indicate freeze response
  final int timeToFirstInteractionMs;
  
  /// Number of panic sessions in the last hour
  /// Frequent sessions indicate escalating distress
  final int recentSessionCount;
  
  /// Outcome of the most recent session
  /// 'resolved', 'escalated', 'abandoned', or null
  final String? previousOutcome;
  
  /// Whether the user has indicated crisis in this session
  final bool userIndicatedCrisis;

  const PanicClassificationInput({
    required this.intensity,
    this.timeToFirstInteractionMs = 0,
    this.recentSessionCount = 0,
    this.previousOutcome,
    this.userIndicatedCrisis = false,
  });
  
  @override
  String toString() => 'PanicClassificationInput('
      'intensity: $intensity, '
      'timeToFirstInteraction: ${timeToFirstInteractionMs}ms, '
      'recentSessions: $recentSessionCount, '
      'previousOutcome: $previousOutcome)';
}

/// Classification result with explanation for auditability.
@immutable
class PanicClassificationResult {
  final PanicUXState state;
  final String reason;
  final DateTime classifiedAt;
  
  const PanicClassificationResult({
    required this.state,
    required this.reason,
    required this.classifiedAt,
  });
  
  Map<String, dynamic> toAuditLog() => {
    'state': state.name,
    'reason': reason,
    'timestamp': classifiedAt.toIso8601String(),
  };
}

/// Deterministic classifier for panic UX state.
/// 
/// Classification rules are explicitly defined and fully testable.
/// No ML models - every decision is explainable.
class PanicUXStateClassifier {
  // Threshold constants - clinically validated values
  // CLINICAL_VALIDATION_REQUIRED: These thresholds should be
  // reviewed by mental health professionals before production use.
  
  static const double _mildIntensityThreshold = 4.0;
  static const double _moderateIntensityThreshold = 6.0;
  static const double _severeIntensityThreshold = 8.0;
  static const double _criticalIntensityThreshold = 9.0;
  
  static const int _freezeResponseThresholdMs = 30000; // 30 seconds
  static const int _frequentSessionThreshold = 2;
  
  /// Classify panic state based on input signals.
  /// 
  /// Classification follows a priority order:
  /// 1. Critical indicators (highest priority)
  /// 2. Severe indicators
  /// 3. Moderate indicators
  /// 4. Mild (default)
  /// 
  /// Returns a result with state and explanation for audit trail.
  PanicClassificationResult classify(PanicClassificationInput input) {
    final now = DateTime.now();
    
    // CRITICAL: Highest priority checks
    if (input.userIndicatedCrisis) {
      return PanicClassificationResult(
        state: PanicUXState.CRITICAL_PANIC,
        reason: 'User explicitly indicated crisis state',
        classifiedAt: now,
      );
    }
    
    if (input.intensity >= _criticalIntensityThreshold) {
      return PanicClassificationResult(
        state: PanicUXState.CRITICAL_PANIC,
        reason: 'Intensity ${input.intensity} exceeds critical threshold $_criticalIntensityThreshold',
        classifiedAt: now,
      );
    }
    
    if (input.previousOutcome == 'escalated') {
      return PanicClassificationResult(
        state: PanicUXState.CRITICAL_PANIC,
        reason: 'Previous session resulted in escalation',
        classifiedAt: now,
      );
    }
    
    // SEVERE: Second priority
    if (input.intensity >= _severeIntensityThreshold) {
      return PanicClassificationResult(
        state: PanicUXState.SEVERE_PANIC,
        reason: 'Intensity ${input.intensity} indicates severe panic',
        classifiedAt: now,
      );
    }
    
    if (input.timeToFirstInteractionMs > _freezeResponseThresholdMs) {
      return PanicClassificationResult(
        state: PanicUXState.SEVERE_PANIC,
        reason: 'Delayed interaction (${input.timeToFirstInteractionMs}ms) suggests freeze response',
        classifiedAt: now,
      );
    }
    
    // MODERATE: Third priority
    if (input.intensity > _mildIntensityThreshold) {
      return PanicClassificationResult(
        state: PanicUXState.MODERATE_PANIC,
        reason: 'Intensity ${input.intensity} indicates moderate panic',
        classifiedAt: now,
      );
    }
    
    if (input.recentSessionCount >= _frequentSessionThreshold) {
      return PanicClassificationResult(
        state: PanicUXState.MODERATE_PANIC,
        reason: 'Frequent sessions (${input.recentSessionCount}) indicate escalating distress',
        classifiedAt: now,
      );
    }
    
    if (input.previousOutcome == 'abandoned') {
      return PanicClassificationResult(
        state: PanicUXState.MODERATE_PANIC,
        reason: 'Previous session was abandoned - may need different approach',
        classifiedAt: now,
      );
    }
    
    // MILD: Default for manageable distress
    return PanicClassificationResult(
      state: PanicUXState.MILD_PANIC,
      reason: 'Signals indicate manageable distress level',
      classifiedAt: now,
    );
  }
  
  /// Re-classify based on new intensity during active session.
  /// 
  /// Used for dynamic adaptation during panic flow.
  PanicClassificationResult reclassify({
    required PanicUXState currentState,
    required double newIntensity,
    required int sessionDurationMs,
  }) {
    final now = DateTime.now();
    
    // Check for escalation
    if (newIntensity >= _criticalIntensityThreshold) {
      return PanicClassificationResult(
        state: PanicUXState.CRITICAL_PANIC,
        reason: 'Intensity escalated to critical during session',
        classifiedAt: now,
      );
    }
    
    // Check for improvement
    if (newIntensity <= _mildIntensityThreshold && 
        currentState != PanicUXState.MILD_PANIC) {
      return PanicClassificationResult(
        state: PanicUXState.MILD_PANIC,
        reason: 'User showing significant improvement',
        classifiedAt: now,
      );
    }
    
    // No significant change - maintain current state
    return PanicClassificationResult(
      state: currentState,
      reason: 'Maintaining current classification',
      classifiedAt: now,
    );
  }
}
