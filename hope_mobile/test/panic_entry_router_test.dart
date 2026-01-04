/// Unit Tests for PanicEntryRouter
/// 
/// Tests automatic routing decisions for all panic states.

import 'package:flutter_test/flutter_test.dart';
import 'package:hope_mobile/panic/ux/panic_state_classifier.dart';
import 'package:hope_mobile/panic/ux/panic_entry_router.dart';

void main() {
  late PanicEntryRouter router;

  setUp(() {
    router = PanicEntryRouter();
  });

  group('PanicEntryRouter - Initial Routing', () {
    test('routes MILD_PANIC to breathingExercise', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 3.0,
      ));
      
      expect(decision.route, PanicRoute.breathingExercise);
      expect(decision.sourceState, PanicUXState.MILD_PANIC);
      expect(decision.config['autoEscalate'], false);
    });

    test('routes MODERATE_PANIC to breathingExercise with autoEscalate', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 5.5,
      ));
      
      expect(decision.route, PanicRoute.breathingExercise);
      expect(decision.sourceState, PanicUXState.MODERATE_PANIC);
      expect(decision.config['autoEscalate'], true);
      expect(decision.config['autoEscalateAfterMs'], isNotNull);
    });

    test('routes SEVERE_PANIC to holdReassurance', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 8.0,
      ));
      
      expect(decision.route, PanicRoute.holdReassurance);
      expect(decision.sourceState, PanicUXState.SEVERE_PANIC);
      expect(decision.config['minDurationMs'], isNotNull);
    });

    test('routes CRITICAL_PANIC to crisisFlow', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 9.5,
      ));
      
      expect(decision.route, PanicRoute.crisisFlow);
      expect(decision.sourceState, PanicUXState.CRITICAL_PANIC);
      expect(decision.config['showHotlines'], true);
    });

    test('routes user-indicated crisis to crisisFlow', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 3.0,
        userIndicatedCrisis: true,
      ));
      
      expect(decision.route, PanicRoute.crisisFlow);
      expect(decision.sourceState, PanicUXState.CRITICAL_PANIC);
    });
  });

  group('PanicEntryRouter - Adaptive Tempo', () {
    test('MILD uses normal tempo', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 3.0,
      ));
      
      expect(decision.config['tempo'], 'normal');
      expect(decision.config['inhaleDuration'], 4);
      expect(decision.config['exhaleDuration'], 6);
    });

    test('MODERATE uses slow tempo', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 5.5,
      ));
      
      expect(decision.config['tempo'], 'slow');
      expect(decision.config['inhaleDuration'], 5);
      expect(decision.config['exhaleDuration'], 7);
    });
  });

  group('PanicEntryRouter - Transition Routing', () {
    test('maintains route when no significant change', () {
      final decision = router.determineTransition(
        currentState: PanicUXState.MODERATE_PANIC,
        currentIntensity: 5.5,
        exerciseDurationMs: 30000,
        currentExercise: 'breathing',
      );
      
      expect(decision.route, PanicRoute.breathingExercise);
    });

    test('auto-escalates from breathing to grounding after threshold', () {
      final decision = router.determineTransition(
        currentState: PanicUXState.MODERATE_PANIC,
        currentIntensity: 6.0, // No improvement
        exerciseDurationMs: 50000, // Past 45s threshold
        currentExercise: 'breathing',
      );
      
      expect(decision.route, PanicRoute.groundingExercise);
    });

    test('does not auto-escalate when intensity improved', () {
      final decision = router.determineTransition(
        currentState: PanicUXState.MODERATE_PANIC,
        currentIntensity: 4.0, // Improved
        exerciseDurationMs: 50000,
        currentExercise: 'breathing',
      );
      
      expect(decision.route, PanicRoute.breathingExercise);
    });

    test('does not auto-escalate for MILD state', () {
      final decision = router.determineTransition(
        currentState: PanicUXState.MILD_PANIC,
        currentIntensity: 3.5,
        exerciseDurationMs: 60000,
        currentExercise: 'breathing',
      );
      
      // Should stay on breathing, not auto-escalate
      expect(decision.route, PanicRoute.breathingExercise);
    });

    test('escalates to crisis when intensity spikes', () {
      final decision = router.determineTransition(
        currentState: PanicUXState.MODERATE_PANIC,
        currentIntensity: 9.5, // Spiked to critical
        exerciseDurationMs: 30000,
        currentExercise: 'breathing',
      );
      
      expect(decision.route, PanicRoute.crisisFlow);
    });
  });

  group('Routing Decision - Config', () {
    test('getConfig returns value when present', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 3.0,
      ));
      
      final tempo = decision.getConfig<String>('tempo', 'default');
      expect(tempo, 'normal');
    });

    test('getConfig returns default when not present', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 3.0,
      ));
      
      final missing = decision.getConfig<int>('nonexistent', 42);
      expect(missing, 42);
    });
  });

  group('Reason logging', () {
    test('all routes have non-empty reasons', () {
      for (final intensity in [3.0, 5.5, 8.0, 9.5]) {
        final decision = router.determineInitialRoute(PanicClassificationInput(
          intensity: intensity,
        ));
        
        expect(decision.reason, isNotEmpty);
      }
    });
  });
}
