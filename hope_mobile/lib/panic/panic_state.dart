/// Panic Session State Model
/// 
/// Comprehensive state model for panic session management.
/// Includes UX state classification and routing information.

import 'package:flutter/foundation.dart';
import 'ux/panic_state_classifier.dart';
import 'ux/panic_entry_router.dart';

/// Panic session lifecycle phases.
enum PanicPhase {
  idle,           // No active session
  entering,       // Session starting, classification in progress
  routing,        // Determining intervention route
  active,         // Active intervention
  transitioning,  // Moving between exercises
  calming,        // User feeling better, preparing to exit
  resolved,       // Session ended successfully
  escalated,      // Escalated to crisis resources
  offline,        // Operating in offline mode
}

/// Message received from backend or generated locally.
@immutable
class PanicMessage {
  final String id;
  final String text;
  final DateTime timestamp;
  final bool isFromServer;
  final PanicPhase? suggestedPhase;
  final int? stepNumber;
  final int? totalSteps;
  
  const PanicMessage({
    required this.id,
    required this.text,
    required this.timestamp,
    this.isFromServer = false,
    this.suggestedPhase,
    this.stepNumber,
    this.totalSteps,
  });
}

/// Current active exercise information.
@immutable
class ActiveExercise {
  final String type; // 'breathing', 'grounding', 'hold', 'crisis'
  final DateTime startedAt;
  final int cycles;
  final Map<String, dynamic> config;
  
  const ActiveExercise({
    required this.type,
    required this.startedAt,
    this.cycles = 0,
    this.config = const {},
  });
  
  ActiveExercise incrementCycles() => ActiveExercise(
    type: type,
    startedAt: startedAt,
    cycles: cycles + 1,
    config: config,
  );
  
  int get durationMs => DateTime.now().difference(startedAt).inMilliseconds;
}

/// Complete panic session state.
@immutable
class PanicSessionState {
  final PanicPhase phase;
  final PanicUXState? uxState;
  final PanicRoutingDecision? routingDecision;
  final ActiveExercise? activeExercise;
  
  final DateTime? startedAt;
  final DateTime? lastInteractionAt;
  final int? timeToFirstInteractionMs;
  
  final double reportedIntensity;
  final List<double> intensityHistory;
  
  final String? currentMessage;
  final String? fallbackMessage;
  final List<PanicMessage> messageHistory;
  
  final int currentStep;
  final int totalSteps;
  
  final bool isConnected;
  final bool voiceEnabled;
  
  final String? sessionId;
  final String? previousOutcome;
  final int recentSessionCount;

  const PanicSessionState({
    required this.phase,
    this.uxState,
    this.routingDecision,
    this.activeExercise,
    this.startedAt,
    this.lastInteractionAt,
    this.timeToFirstInteractionMs,
    this.reportedIntensity = 5.0,
    this.intensityHistory = const [],
    this.currentMessage,
    this.fallbackMessage,
    this.messageHistory = const [],
    this.currentStep = 0,
    this.totalSteps = 1,
    this.isConnected = false,
    this.voiceEnabled = false,
    this.sessionId,
    this.previousOutcome,
    this.recentSessionCount = 0,
  });

  factory PanicSessionState.initial() => const PanicSessionState(
    phase: PanicPhase.idle,
    reportedIntensity: 5.0,
    intensityHistory: [],
    messageHistory: [],
  );

  bool get isActive => phase != PanicPhase.idle && 
                        phase != PanicPhase.resolved;
  
  bool get isInExercise => activeExercise != null;
  
  bool get needsEscalation => uxState == PanicUXState.CRITICAL_PANIC;
  
  int get sessionDurationMs => startedAt != null 
      ? DateTime.now().difference(startedAt!).inMilliseconds 
      : 0;
  
  double get intensityTrend {
    if (intensityHistory.length < 2) return 0.0;
    final recent = intensityHistory.sublist(
      intensityHistory.length - 3 < 0 ? 0 : intensityHistory.length - 3,
    );
    if (recent.isEmpty) return 0.0;
    return recent.last - recent.first;
  }
  
  PanicClassificationInput toClassificationInput() => PanicClassificationInput(
    intensity: reportedIntensity,
    timeToFirstInteractionMs: timeToFirstInteractionMs ?? 0,
    recentSessionCount: recentSessionCount,
    previousOutcome: previousOutcome,
  );

  PanicSessionState copyWith({
    PanicPhase? phase,
    PanicUXState? uxState,
    PanicRoutingDecision? routingDecision,
    ActiveExercise? activeExercise,
    bool clearActiveExercise = false,
    DateTime? startedAt,
    DateTime? lastInteractionAt,
    int? timeToFirstInteractionMs,
    double? reportedIntensity,
    List<double>? intensityHistory,
    String? currentMessage,
    String? fallbackMessage,
    bool clearFallbackMessage = false,
    List<PanicMessage>? messageHistory,
    int? currentStep,
    int? totalSteps,
    bool? isConnected,
    bool? voiceEnabled,
    String? sessionId,
    String? previousOutcome,
    int? recentSessionCount,
  }) {
    return PanicSessionState(
      phase: phase ?? this.phase,
      uxState: uxState ?? this.uxState,
      routingDecision: routingDecision ?? this.routingDecision,
      activeExercise: clearActiveExercise ? null : (activeExercise ?? this.activeExercise),
      startedAt: startedAt ?? this.startedAt,
      lastInteractionAt: lastInteractionAt ?? this.lastInteractionAt,
      timeToFirstInteractionMs: timeToFirstInteractionMs ?? this.timeToFirstInteractionMs,
      reportedIntensity: reportedIntensity ?? this.reportedIntensity,
      intensityHistory: intensityHistory ?? this.intensityHistory,
      currentMessage: currentMessage ?? this.currentMessage,
      fallbackMessage: clearFallbackMessage ? null : (fallbackMessage ?? this.fallbackMessage),
      messageHistory: messageHistory ?? this.messageHistory,
      currentStep: currentStep ?? this.currentStep,
      totalSteps: totalSteps ?? this.totalSteps,
      isConnected: isConnected ?? this.isConnected,
      voiceEnabled: voiceEnabled ?? this.voiceEnabled,
      sessionId: sessionId ?? this.sessionId,
      previousOutcome: previousOutcome ?? this.previousOutcome,
      recentSessionCount: recentSessionCount ?? this.recentSessionCount,
    );
  }
}
