/// Panic Analytics - Structured observability for panic UX
/// 
/// Emits structured events for auditability and monitoring.
/// NO PII is logged - only structured metrics and decisions.

import 'package:flutter/foundation.dart';
import 'panic_state_classifier.dart';

/// Structured event types for panic flow observability.
enum PanicEventType {
  stateClassified,
  routingDecision,
  exerciseStarted,
  exerciseTransition,
  exerciseCompleted,
  crisisFlowEntered,
  crisisResourceUsed,
  sessionOutcome,
  intensityChange,
  offlineFallbackActivated,
}

/// A structured panic analytics event.
@immutable
class PanicAnalyticsEvent {
  final PanicEventType type;
  final Map<String, dynamic> data;
  final DateTime timestamp;
  
  const PanicAnalyticsEvent({
    required this.type,
    required this.data,
    required this.timestamp,
  });
  
  Map<String, dynamic> toJson() => {
    'type': type.name,
    'data': data,
    'timestamp': timestamp.toIso8601String(),
  };
  
  @override
  String toString() => 'PanicEvent(${type.name}, $data)';
}

/// Callback for analytics event consumers.
typedef PanicEventCallback = void Function(PanicAnalyticsEvent event);

/// Panic analytics service for structured event emission.
/// 
/// All events are non-PII and safe for logging/monitoring.
class PanicAnalytics {
  static PanicAnalytics? _instance;
  static PanicAnalytics get instance => _instance ??= PanicAnalytics._();
  
  PanicAnalytics._();
  
  final List<PanicEventCallback> _listeners = [];
  
  /// Register a listener for analytics events.
  void addListener(PanicEventCallback callback) {
    _listeners.add(callback);
  }
  
  /// Remove a listener.
  void removeListener(PanicEventCallback callback) {
    _listeners.remove(callback);
  }
  
  void _emit(PanicAnalyticsEvent event) {
    // Debug logging in development
    if (kDebugMode) {
      debugPrint('[PanicAnalytics] ${event.type.name}: ${event.data}');
    }
    
    for (final listener in _listeners) {
      try {
        listener(event);
      } catch (e) {
        // Never let listener errors propagate
        if (kDebugMode) {
          debugPrint('[PanicAnalytics] Listener error: $e');
        }
      }
    }
  }
  
  /// Log panic state classification.
  void logClassification(PanicClassificationResult result, double intensity) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.stateClassified,
      data: {
        'state': result.state.name,
        'reason': result.reason,
        'intensity': intensity,
      },
      timestamp: result.classifiedAt,
    ));
  }
  
  /// Log routing decision to a specific screen.
  void logRoutingDecision({
    required PanicUXState state,
    required String targetScreen,
    required String reason,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.routingDecision,
      data: {
        'panicState': state.name,
        'targetScreen': targetScreen,
        'reason': reason,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log exercise start.
  void logExerciseStarted({
    required String exerciseType,
    required PanicUXState panicState,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.exerciseStarted,
      data: {
        'exerciseType': exerciseType,
        'panicState': panicState.name,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log exercise transition (auto-escalation or user-triggered).
  void logExerciseTransition({
    required String fromExercise,
    required String toExercise,
    required int durationMs,
    required bool wasAutomatic,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.exerciseTransition,
      data: {
        'from': fromExercise,
        'to': toExercise,
        'durationMs': durationMs,
        'automatic': wasAutomatic,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log exercise completion.
  void logExerciseCompleted({
    required String exerciseType,
    required int durationMs,
    required int cycles,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.exerciseCompleted,
      data: {
        'exerciseType': exerciseType,
        'durationMs': durationMs,
        'cycles': cycles,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log crisis flow entry.
  void logCrisisFlowEntered({
    required PanicUXState fromState,
    required String trigger,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.crisisFlowEntered,
      data: {
        'fromState': fromState.name,
        'trigger': trigger,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log crisis resource used (phone call, website, etc).
  void logCrisisResourceUsed({
    required String resource,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.crisisResourceUsed,
      data: {
        'resource': resource,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log session outcome.
  void logSessionOutcome({
    required String outcome,
    required int durationMs,
    required PanicUXState finalState,
    required double finalIntensity,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.sessionOutcome,
      data: {
        'outcome': outcome,
        'durationMs': durationMs,
        'finalState': finalState.name,
        'finalIntensity': finalIntensity,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log intensity change during session.
  void logIntensityChange({
    required double previousIntensity,
    required double newIntensity,
  }) {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.intensityChange,
      data: {
        'previous': previousIntensity,
        'new': newIntensity,
        'delta': newIntensity - previousIntensity,
      },
      timestamp: DateTime.now(),
    ));
  }
  
  /// Log offline fallback activation.
  void logOfflineFallback() {
    _emit(PanicAnalyticsEvent(
      type: PanicEventType.offlineFallbackActivated,
      data: {},
      timestamp: DateTime.now(),
    ));
  }
}
