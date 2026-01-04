/// Offline Fallback Regression Test
/// 
/// Ensures breathing exercise always works offline.
/// This is a critical safety requirement.

import 'package:flutter_test/flutter_test.dart';
import 'package:hope_mobile/panic/ux/panic_state_classifier.dart';
import 'package:hope_mobile/panic/ux/panic_entry_router.dart';

void main() {
  group('Offline Fallback - Breathing Always Works', () {
    late PanicEntryRouter router;

    setUp(() {
      router = PanicEntryRouter();
    });

    test('MILD panic routes to breathing (works offline)', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 3.0,
      ));
      
      expect(decision.route, PanicRoute.breathingExercise);
      expect(decision.config, isNotNull);
    });

    test('MODERATE panic routes to breathing (works offline)', () {
      final decision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 5.5,
      ));
      
      expect(decision.route, PanicRoute.breathingExercise);
    });

    test('Breathing exercise config is always valid', () {
      for (final intensity in [1.0, 3.0, 4.0, 5.0, 6.0]) {
        final decision = router.determineInitialRoute(PanicClassificationInput(
          intensity: intensity,
        ));
        
        // Breathing should always have valid timing config
        if (decision.route == PanicRoute.breathingExercise) {
          expect(decision.config['inhaleDuration'], isPositive);
          expect(decision.config['holdDuration'], isPositive);
          expect(decision.config['exhaleDuration'], isPositive);
        }
      }
    });

    test('Router does not require network for routing decision', () {
      // Router should work synchronously without any async network calls
      final stopwatch = Stopwatch()..start();
      
      for (var i = 0; i < 100; i++) {
        router.determineInitialRoute(PanicClassificationInput(
          intensity: (i % 10 + 1).toDouble(),
        ));
      }
      
      stopwatch.stop();
      
      // 100 routing decisions should complete in under 100ms
      expect(stopwatch.elapsedMilliseconds, lessThan(100));
    });

    test('Classification is deterministic', () {
      const input = PanicClassificationInput(
        intensity: 5.0,
        timeToFirstInteractionMs: 1000,
        recentSessionCount: 1,
      );
      
      final results = List.generate(10, (_) => router.determineInitialRoute(input));
      
      // All results should be identical
      for (final result in results) {
        expect(result.route, results.first.route);
        expect(result.sourceState, results.first.sourceState);
      }
    });

    test('Fallback path exists for any intensity', () {
      // Test all possible intensity values
      for (var intensity = 1.0; intensity <= 10.0; intensity += 0.5) {
        final decision = router.determineInitialRoute(PanicClassificationInput(
          intensity: intensity,
        ));
        
        // Must always return a valid route
        expect(decision.route, isNotNull);
        expect(
          [
            PanicRoute.breathingExercise,
            PanicRoute.groundingExercise,
            PanicRoute.holdReassurance,
            PanicRoute.crisisFlow,
          ].contains(decision.route),
          isTrue,
        );
      }
    });

    test('Hold and Crisis screens allow exercise fallback', () {
      // SEVERE panic
      final severeDecision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 8.0,
      ));
      expect(severeDecision.config['showExerciseOption'], isTrue);
      
      // CRITICAL panic
      final criticalDecision = router.determineInitialRoute(const PanicClassificationInput(
        intensity: 9.5,
      ));
      expect(criticalDecision.config['allowExerciseFallback'], isTrue);
    });
  });

  group('PanicClassificationInput validation', () {
    test('accepts valid intensity range', () {
      for (var i = 1.0; i <= 10.0; i++) {
        expect(
          () => PanicClassificationInput(intensity: i),
          returnsNormally,
        );
      }
    });

    test('toString provides readable output', () {
      const input = PanicClassificationInput(
        intensity: 5.0,
        timeToFirstInteractionMs: 5000,
        recentSessionCount: 2,
        previousOutcome: 'resolved',
      );
      
      expect(input.toString(), contains('intensity'));
      expect(input.toString(), contains('5.0'));
    });
  });
}
