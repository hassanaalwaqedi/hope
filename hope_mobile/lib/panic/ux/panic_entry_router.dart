/// Panic Entry Router
/// 
/// Automatic routing to appropriate intervention screens
/// based on classified panic state. No user choice required.
/// 
/// The system decides first. The user follows.

import 'package:flutter/material.dart';
import 'panic_state_classifier.dart';
import 'panic_analytics.dart';

/// Target screens for panic intervention routing.
enum PanicRoute {
  breathingExercise,
  groundingExercise,
  holdReassurance,
  crisisFlow,
}

/// Routing decision with target and configuration.
@immutable
class PanicRoutingDecision {
  final PanicRoute route;
  final PanicUXState sourceState;
  final Map<String, dynamic> config;
  final String reason;
  
  const PanicRoutingDecision({
    required this.route,
    required this.sourceState,
    required this.config,
    required this.reason,
  });
  
  /// Get screen configuration for adaptive behavior.
  T getConfig<T>(String key, T defaultValue) {
    return config[key] as T? ?? defaultValue;
  }
}

/// Routes panic sessions to appropriate intervention screens.
/// 
/// Routing is automatic and deterministic based on classification.
/// User is not asked to choose - cognitive load is minimized.
class PanicEntryRouter {
  final PanicUXStateClassifier _classifier;
  final PanicAnalytics _analytics;
  
  PanicEntryRouter({
    PanicUXStateClassifier? classifier,
    PanicAnalytics? analytics,
  })  : _classifier = classifier ?? PanicUXStateClassifier(),
        _analytics = analytics ?? PanicAnalytics.instance;
  
  /// Determine initial route based on classification.
  /// 
  /// Returns a routing decision with target screen and configuration.
  PanicRoutingDecision determineInitialRoute(PanicClassificationInput input) {
    final classification = _classifier.classify(input);
    
    // Log classification
    _analytics.logClassification(classification, input.intensity);
    
    final decision = _routeForState(classification.state, classification);
    
    // Log routing decision
    _analytics.logRoutingDecision(
      state: classification.state,
      targetScreen: decision.route.name,
      reason: decision.reason,
    );
    
    return decision;
  }
  
  /// Get next route based on current state and signals.
  /// 
  /// Used for automatic transitions during session.
  PanicRoutingDecision determineTransition({
    required PanicUXState currentState,
    required double currentIntensity,
    required int exerciseDurationMs,
    required String currentExercise,
  }) {
    // Check if intensity has changed significantly
    final reclassification = _classifier.reclassify(
      currentState: currentState,
      newIntensity: currentIntensity,
      sessionDurationMs: exerciseDurationMs,
    );
    
    // If state escalated, route to appropriate screen
    if (reclassification.state != currentState) {
      _analytics.logClassification(reclassification, currentIntensity);
      return _routeForState(reclassification.state, reclassification);
    }
    
    // Auto-escalation logic for no improvement
    if (_shouldAutoEscalate(
      currentState: currentState,
      exerciseDurationMs: exerciseDurationMs,
      currentIntensity: currentIntensity,
      currentExercise: currentExercise,
    )) {
      return _getAutoEscalationRoute(currentState, currentExercise);
    }
    
    // No change needed
    return PanicRoutingDecision(
      route: _routeFromString(currentExercise),
      sourceState: currentState,
      config: {},
      reason: 'Continuing current exercise',
    );
  }
  
  PanicRoutingDecision _routeForState(
    PanicUXState state,
    PanicClassificationResult classification,
  ) {
    switch (state) {
      case PanicUXState.MILD_PANIC:
        return PanicRoutingDecision(
          route: PanicRoute.breathingExercise,
          sourceState: state,
          config: {
            'tempo': 'normal',
            'autoEscalate': false,
            'inhaleDuration': 4,
            'holdDuration': 4,
            'exhaleDuration': 6,
          },
          reason: 'Mild panic - standard breathing exercise',
        );
        
      case PanicUXState.MODERATE_PANIC:
        return PanicRoutingDecision(
          route: PanicRoute.breathingExercise,
          sourceState: state,
          config: {
            'tempo': 'slow',
            'autoEscalate': true,
            'autoEscalateAfterMs': 45000, // 45 seconds
            'inhaleDuration': 5,
            'holdDuration': 5,
            'exhaleDuration': 7,
          },
          reason: 'Moderate panic - slower breathing with auto-escalation',
        );
        
      case PanicUXState.SEVERE_PANIC:
        return PanicRoutingDecision(
          route: PanicRoute.holdReassurance,
          sourceState: state,
          config: {
            'minDurationMs': 30000, // 30 seconds minimum
            'showExerciseOption': true,
            'messageTone': 'minimal',
          },
          reason: 'Severe panic - minimal motion, strong presence',
        );
        
      case PanicUXState.CRITICAL_PANIC:
        return PanicRoutingDecision(
          route: PanicRoute.crisisFlow,
          sourceState: state,
          config: {
            'showHotlines': true,
            'emphasizeHuman': true,
            'allowExerciseFallback': true,
          },
          reason: 'Critical panic - crisis resources emphasis',
        );
    }
  }
  
  bool _shouldAutoEscalate({
    required PanicUXState currentState,
    required int exerciseDurationMs,
    required double currentIntensity,
    required String currentExercise,
  }) {
    // Only auto-escalate from breathing in moderate state
    if (currentState != PanicUXState.MODERATE_PANIC) return false;
    if (currentExercise != 'breathing') return false;
    
    // Check if enough time has passed without improvement
    const autoEscalateThresholdMs = 45000; // 45 seconds
    const noImprovementThreshold = 5.0;
    
    return exerciseDurationMs > autoEscalateThresholdMs &&
           currentIntensity > noImprovementThreshold;
  }
  
  PanicRoutingDecision _getAutoEscalationRoute(
    PanicUXState currentState,
    String currentExercise,
  ) {
    // Auto-escalate from breathing to grounding
    if (currentExercise == 'breathing') {
      _analytics.logExerciseTransition(
        fromExercise: 'breathing',
        toExercise: 'grounding',
        durationMs: 45000,
        wasAutomatic: true,
      );
      
      return PanicRoutingDecision(
        route: PanicRoute.groundingExercise,
        sourceState: currentState,
        config: {
          'transitionType': 'gentle',
          'skipIntro': true,
        },
        reason: 'Auto-escalating to grounding after breathing showed no improvement',
      );
    }
    
    // From grounding, escalate to hold/reassurance
    _analytics.logExerciseTransition(
      fromExercise: currentExercise,
      toExercise: 'holdReassurance',
      durationMs: 45000,
      wasAutomatic: true,
    );
    
    return PanicRoutingDecision(
      route: PanicRoute.holdReassurance,
      sourceState: currentState,
      config: {
        'transitionType': 'gentle',
        'fromExercise': currentExercise,
      },
      reason: 'Escalating to hold/reassurance for stronger support',
    );
  }
  
  PanicRoute _routeFromString(String exercise) {
    switch (exercise) {
      case 'breathing':
        return PanicRoute.breathingExercise;
      case 'grounding':
        return PanicRoute.groundingExercise;
      case 'hold':
        return PanicRoute.holdReassurance;
      case 'crisis':
        return PanicRoute.crisisFlow;
      default:
        return PanicRoute.breathingExercise;
    }
  }
}
