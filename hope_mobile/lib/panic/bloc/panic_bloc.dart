/// Panic BLoC - State Management with Adaptive UX Intelligence
/// 
/// Integrates:
/// - PanicUXStateClassifier for severity determination
/// - PanicEntryRouter for automatic intervention routing
/// - PanicAnalytics for observability
/// - WebSocket service for backend communication
/// 
/// The system decides routing. User follows.

import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../panic_state.dart';
import '../ux/panic_state_classifier.dart';
import '../ux/panic_entry_router.dart';
import '../ux/panic_analytics.dart';
import '../../data/services/websocket_service.dart';

// ============================================================================
// EVENTS
// ============================================================================

abstract class PanicEvent extends Equatable {
  const PanicEvent();
  @override
  List<Object?> get props => [];
}

/// Triggered when user initiates panic session.
class PanicTriggered extends PanicEvent {
  final double? initialIntensity;
  const PanicTriggered({this.initialIntensity});
  @override
  List<Object?> get props => [initialIntensity];
}

/// User sent a message (intensity update, acknowledgment, etc.)
class PanicMessageSent extends PanicEvent {
  final String message;
  const PanicMessageSent(this.message);
  @override
  List<Object?> get props => [message];
}

/// User reported intensity change.
class IntensityReported extends PanicEvent {
  final double intensity;
  const IntensityReported(this.intensity);
  @override
  List<Object?> get props => [intensity];
}

/// Request to transition between exercises.
class ExerciseTransitionRequested extends PanicEvent {
  final String fromExercise;
  final String toExercise;
  const ExerciseTransitionRequested({
    required this.fromExercise,
    required this.toExercise,
  });
  @override
  List<Object?> get props => [fromExercise, toExercise];
}

/// Exercise cycle completed.
class ExerciseCycleCompleted extends PanicEvent {
  const ExerciseCycleCompleted();
}

/// Request to exit panic session.
class PanicExitRequested extends PanicEvent {
  const PanicExitRequested();
}

/// Toggle voice guidance.
class VoiceToggled extends PanicEvent {
  final bool enabled;
  const VoiceToggled(this.enabled);
  @override
  List<Object?> get props => [enabled];
}

/// User indicated crisis state explicitly.
class CrisisIndicated extends PanicEvent {
  const CrisisIndicated();
}

/// Connection state changed.
class _ConnectionStateChanged extends PanicEvent {
  final ConnectionState state;
  const _ConnectionStateChanged(this.state);
  @override
  List<Object?> get props => [state];
}

/// Server message received.
class _ServerMessage extends PanicEvent {
  final Map<String, dynamic> data;
  const _ServerMessage(this.data);
  @override
  List<Object?> get props => [data];
}

/// Auto-escalation timer triggered.
class _AutoEscalationTriggered extends PanicEvent {
  const _AutoEscalationTriggered();
}

// ============================================================================
// BLOC
// ============================================================================

class PanicBloc extends Bloc<PanicEvent, PanicSessionState> {
  final WebSocketService _wsService;
  final PanicUXStateClassifier _classifier;
  final PanicEntryRouter _router;
  final PanicAnalytics _analytics;
  
  StreamSubscription? _messageSubscription;
  StreamSubscription? _connectionSubscription;
  Timer? _autoEscalationTimer;
  
  // Fallback messages for offline mode
  static const List<String> _fallbackMessages = [
    "I'm here with you. Let's breathe together.",
    "You're safe. This feeling will pass.",
    "Focus on your breathing. Slow and steady.",
    "You're doing great. One breath at a time.",
    "Notice your feet on the ground. You are here, now.",
  ];
  int _fallbackIndex = 0;

  PanicBloc({
    WebSocketService? wsService,
    PanicUXStateClassifier? classifier,
    PanicEntryRouter? router,
    PanicAnalytics? analytics,
  })  : _wsService = wsService ?? WebSocketService(),
        _classifier = classifier ?? PanicUXStateClassifier(),
        _router = router ?? PanicEntryRouter(),
        _analytics = analytics ?? PanicAnalytics.instance,
        super(PanicSessionState.initial()) {
    
    // Register event handlers
    on<PanicTriggered>(_onPanicTriggered);
    on<PanicMessageSent>(_onMessageSent);
    on<IntensityReported>(_onIntensityReported);
    on<ExerciseTransitionRequested>(_onExerciseTransition);
    on<ExerciseCycleCompleted>(_onExerciseCycleCompleted);
    on<PanicExitRequested>(_onExitRequested);
    on<VoiceToggled>(_onVoiceToggled);
    on<CrisisIndicated>(_onCrisisIndicated);
    on<_ConnectionStateChanged>(_onConnectionStateChanged);
    on<_ServerMessage>(_onServerMessage);
    on<_AutoEscalationTriggered>(_onAutoEscalation);
    
    // Listen to WebSocket
    _messageSubscription = _wsService.messages.listen((data) {
      add(_ServerMessage(data));
    });
    
    _connectionSubscription = _wsService.connectionState.listen((connState) {
      add(_ConnectionStateChanged(connState));
    });
  }

  // --------------------------------------------------------------------------
  // Panic Session Lifecycle
  // --------------------------------------------------------------------------

  Future<void> _onPanicTriggered(
    PanicTriggered event,
    Emitter<PanicSessionState> emit,
  ) async {
    final now = DateTime.now();
    final initialIntensity = event.initialIntensity ?? 5.0;
    
    // Enter session
    emit(state.copyWith(
      phase: PanicPhase.entering,
      startedAt: now,
      reportedIntensity: initialIntensity,
      intensityHistory: [initialIntensity],
      currentMessage: "I'm here with you...",
    ));
    
    // Classify panic state
    final input = PanicClassificationInput(
      intensity: initialIntensity,
      timeToFirstInteractionMs: 0,
      recentSessionCount: state.recentSessionCount,
      previousOutcome: state.previousOutcome,
    );
    
    final routingDecision = _router.determineInitialRoute(input);
    
    emit(state.copyWith(
      phase: PanicPhase.routing,
      uxState: routingDecision.sourceState,
      routingDecision: routingDecision,
    ));
    
    // Attempt backend connection
    try {
      await _wsService.connect();
      _wsService.startPanicSession(initialIntensity: initialIntensity);
      emit(state.copyWith(isConnected: true));
    } catch (e) {
      // Offline mode
      emit(state.copyWith(
        isConnected: false,
        fallbackMessage: "I'm having trouble connecting, but I'm still here with you.",
      ));
      _analytics.logOfflineFallback();
    }
    
    // Activate exercise based on routing
    final exercise = ActiveExercise(
      type: _exerciseTypeFromRoute(routingDecision.route),
      startedAt: now,
      config: routingDecision.config,
    );
    
    emit(state.copyWith(
      phase: PanicPhase.active,
      activeExercise: exercise,
      currentMessage: _getInitialMessage(routingDecision),
    ));
    
    // Start auto-escalation timer if configured
    _startAutoEscalationTimer(routingDecision);
  }

  Future<void> _onIntensityReported(
    IntensityReported event,
    Emitter<PanicSessionState> emit,
  ) async {
    final newIntensity = event.intensity;
    final previousIntensity = state.reportedIntensity;
    
    // Log intensity change
    _analytics.logIntensityChange(
      previousIntensity: previousIntensity,
      newIntensity: newIntensity,
    );
    
    // Update state
    emit(state.copyWith(
      reportedIntensity: newIntensity,
      intensityHistory: [...state.intensityHistory, newIntensity],
      lastInteractionAt: DateTime.now(),
    ));
    
    // First interaction timing
    if (state.timeToFirstInteractionMs == null && state.startedAt != null) {
      emit(state.copyWith(
        timeToFirstInteractionMs: DateTime.now().difference(state.startedAt!).inMilliseconds,
      ));
    }
    
    // Check if re-routing is needed
    if (state.activeExercise != null) {
      final transition = _router.determineTransition(
        currentState: state.uxState ?? PanicUXState.MILD_PANIC,
        currentIntensity: newIntensity,
        exerciseDurationMs: state.activeExercise!.durationMs,
        currentExercise: state.activeExercise!.type,
      );
      
      if (transition.route.name != state.activeExercise!.type) {
        add(ExerciseTransitionRequested(
          fromExercise: state.activeExercise!.type,
          toExercise: _exerciseTypeFromRoute(transition.route),
        ));
      }
    }
    
    // Send to backend
    if (_wsService.isConnected) {
      _wsService.reportIntensity(newIntensity);
    }
  }

  Future<void> _onExerciseTransition(
    ExerciseTransitionRequested event,
    Emitter<PanicSessionState> emit,
  ) async {
    emit(state.copyWith(
      phase: PanicPhase.transitioning,
    ));
    
    // Log transition
    _analytics.logExerciseTransition(
      fromExercise: event.fromExercise,
      toExercise: event.toExercise,
      durationMs: state.activeExercise?.durationMs ?? 0,
      wasAutomatic: false,
    );
    
    // Cancel existing auto-escalation timer
    _autoEscalationTimer?.cancel();
    
    // Small delay for smooth transition
    await Future.delayed(const Duration(milliseconds: 300));
    
    final newExercise = ActiveExercise(
      type: event.toExercise,
      startedAt: DateTime.now(),
    );
    
    emit(state.copyWith(
      phase: PanicPhase.active,
      activeExercise: newExercise,
      currentMessage: _getExerciseMessage(event.toExercise),
    ));
    
    _analytics.logExerciseStarted(
      exerciseType: event.toExercise,
      panicState: state.uxState ?? PanicUXState.MILD_PANIC,
    );
  }

  void _onExerciseCycleCompleted(
    ExerciseCycleCompleted event,
    Emitter<PanicSessionState> emit,
  ) {
    if (state.activeExercise != null) {
      emit(state.copyWith(
        activeExercise: state.activeExercise!.incrementCycles(),
      ));
    }
  }

  Future<void> _onExitRequested(
    PanicExitRequested event,
    Emitter<PanicSessionState> emit,
  ) async {
    emit(state.copyWith(
      phase: PanicPhase.calming,
      currentMessage: "You're doing great. Take all the time you need.",
    ));
    
    // Log outcome
    _analytics.logSessionOutcome(
      outcome: 'resolved',
      durationMs: state.sessionDurationMs,
      finalState: state.uxState ?? PanicUXState.MILD_PANIC,
      finalIntensity: state.reportedIntensity,
    );
    
    if (_wsService.isConnected) {
      _wsService.endPanicSession(outcome: 'resolved');
    }
    
    await Future.delayed(const Duration(seconds: 2));
    emit(state.copyWith(phase: PanicPhase.resolved));
    
    await Future.delayed(const Duration(seconds: 1));
    emit(PanicSessionState.initial().copyWith(
      previousOutcome: 'resolved',
      recentSessionCount: state.recentSessionCount + 1,
    ));
    
    _autoEscalationTimer?.cancel();
    await _wsService.disconnect();
  }

  void _onCrisisIndicated(
    CrisisIndicated event,
    Emitter<PanicSessionState> emit,
  ) {
    _analytics.logCrisisFlowEntered(
      fromState: state.uxState ?? PanicUXState.MILD_PANIC,
      trigger: 'user_indicated',
    );
    
    emit(state.copyWith(
      phase: PanicPhase.escalated,
      uxState: PanicUXState.CRITICAL_PANIC,
    ));
  }

  // --------------------------------------------------------------------------
  // Internal Handlers
  // --------------------------------------------------------------------------

  void _onVoiceToggled(VoiceToggled event, Emitter<PanicSessionState> emit) {
    emit(state.copyWith(voiceEnabled: event.enabled));
  }

  void _onConnectionStateChanged(
    _ConnectionStateChanged event,
    Emitter<PanicSessionState> emit,
  ) {
    final isConnected = event.state == ConnectionState.connected;
    
    if (!isConnected && state.isActive) {
      emit(state.copyWith(
        isConnected: false,
        fallbackMessage: "Connection interrupted. Using offline support.",
      ));
      _analytics.logOfflineFallback();
    } else if (isConnected) {
      emit(state.copyWith(
        isConnected: true,
        clearFallbackMessage: true,
      ));
    }
  }

  void _onServerMessage(
    _ServerMessage event,
    Emitter<PanicSessionState> emit,
  ) {
    final data = event.data;
    final type = data['type'] as String?;
    
    switch (type) {
      case 'ai_response':
        final text = data['text'] as String? ?? data['message'] as String?;
        if (text != null) {
          emit(state.copyWith(
            currentMessage: text,
            isConnected: true,
          ));
        }
        break;
        
      case 'crisis_resources':
        emit(state.copyWith(
          phase: PanicPhase.escalated,
          uxState: PanicUXState.CRITICAL_PANIC,
          currentMessage: data['message'] as String?,
        ));
        break;
    }
  }

  Future<void> _onMessageSent(
    PanicMessageSent event,
    Emitter<PanicSessionState> emit,
  ) async {
    if (_wsService.isConnected) {
      _wsService.sendPanicMessage(event.message, intensity: state.reportedIntensity);
    } else {
      // Offline mode - cycle through fallback messages
      _fallbackIndex = (_fallbackIndex + 1) % _fallbackMessages.length;
      emit(state.copyWith(
        currentMessage: _fallbackMessages[_fallbackIndex],
      ));
    }
  }

  void _onAutoEscalation(
    _AutoEscalationTriggered event,
    Emitter<PanicSessionState> emit,
  ) {
    if (!state.isActive || state.activeExercise == null) return;
    
    // Check if should auto-escalate
    final currentExercise = state.activeExercise!.type;
    final currentIntensity = state.reportedIntensity;
    
    // Only escalate if intensity hasn't improved significantly
    if (currentIntensity > 5.0) {
      String nextExercise;
      switch (currentExercise) {
        case 'breathing':
          nextExercise = 'grounding';
          break;
        case 'grounding':
          nextExercise = 'hold';
          break;
        default:
          return; // No further escalation
      }
      
      add(ExerciseTransitionRequested(
        fromExercise: currentExercise,
        toExercise: nextExercise,
      ));
    }
  }

  // --------------------------------------------------------------------------
  // Helpers
  // --------------------------------------------------------------------------

  void _startAutoEscalationTimer(PanicRoutingDecision decision) {
    if (decision.config['autoEscalate'] != true) return;
    
    final timeoutMs = decision.config['autoEscalateAfterMs'] as int? ?? 45000;
    
    _autoEscalationTimer?.cancel();
    _autoEscalationTimer = Timer(
      Duration(milliseconds: timeoutMs),
      () => add(const _AutoEscalationTriggered()),
    );
  }

  String _exerciseTypeFromRoute(PanicRoute route) {
    switch (route) {
      case PanicRoute.breathingExercise:
        return 'breathing';
      case PanicRoute.groundingExercise:
        return 'grounding';
      case PanicRoute.holdReassurance:
        return 'hold';
      case PanicRoute.crisisFlow:
        return 'crisis';
    }
  }

  String _getInitialMessage(PanicRoutingDecision decision) {
    switch (decision.route) {
      case PanicRoute.breathingExercise:
        return "Let's breathe together. Follow along with me.";
      case PanicRoute.groundingExercise:
        return "Let's ground ourselves. Notice your surroundings.";
      case PanicRoute.holdReassurance:
        return "I'm here with you.";
      case PanicRoute.crisisFlow:
        return "You're not alone.";
    }
  }

  String _getExerciseMessage(String exerciseType) {
    switch (exerciseType) {
      case 'breathing':
        return "Let's focus on your breathing now.";
      case 'grounding':
        return "Let's try a grounding exercise.";
      case 'hold':
        return "I'm here with you. Just stay with me.";
      case 'crisis':
        return "You're not alone. Help is available.";
      default:
        return "I'm here with you.";
    }
  }

  @override
  Future<void> close() {
    _messageSubscription?.cancel();
    _connectionSubscription?.cancel();
    _autoEscalationTimer?.cancel();
    _wsService.dispose();
    return super.close();
  }
}
