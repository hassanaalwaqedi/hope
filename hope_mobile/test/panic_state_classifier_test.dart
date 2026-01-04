/// Unit Tests for PanicUXStateClassifier
/// 
/// Tests all classification rules are deterministic and correct.

import 'package:flutter_test/flutter_test.dart';
import 'package:hope_mobile/panic/ux/panic_state_classifier.dart';

void main() {
  late PanicUXStateClassifier classifier;

  setUp(() {
    classifier = PanicUXStateClassifier();
  });

  group('PanicUXStateClassifier', () {
    group('CRITICAL_PANIC classification', () {
      test('classifies intensity >= 9 as CRITICAL', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 9.0,
        ));
        
        expect(result.state, PanicUXState.CRITICAL_PANIC);
        expect(result.reason, contains('critical threshold'));
      });

      test('classifies intensity 10 as CRITICAL', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 10.0,
        ));
        
        expect(result.state, PanicUXState.CRITICAL_PANIC);
      });

      test('classifies userIndicatedCrisis=true as CRITICAL', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 3.0,
          userIndicatedCrisis: true,
        ));
        
        expect(result.state, PanicUXState.CRITICAL_PANIC);
        expect(result.reason, contains('User explicitly indicated'));
      });

      test('classifies previousOutcome=escalated as CRITICAL', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 5.0,
          previousOutcome: 'escalated',
        ));
        
        expect(result.state, PanicUXState.CRITICAL_PANIC);
        expect(result.reason, contains('Previous session'));
      });
    });

    group('SEVERE_PANIC classification', () {
      test('classifies intensity 7-8 as SEVERE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 8.0,
        ));
        
        expect(result.state, PanicUXState.SEVERE_PANIC);
        expect(result.reason, contains('severe panic'));
      });

      test('classifies intensity 7 as SEVERE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 7.0,
        ));
        
        expect(result.state, PanicUXState.SEVERE_PANIC);
      });

      test('classifies long timeToFirstInteraction as SEVERE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 4.0,
          timeToFirstInteractionMs: 35000, // 35 seconds
        ));
        
        expect(result.state, PanicUXState.SEVERE_PANIC);
        expect(result.reason, contains('freeze response'));
      });
    });

    group('MODERATE_PANIC classification', () {
      test('classifies intensity 5-6 as MODERATE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 6.0,
        ));
        
        expect(result.state, PanicUXState.MODERATE_PANIC);
        expect(result.reason, contains('moderate panic'));
      });

      test('classifies intensity 5 as MODERATE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 5.0,
        ));
        
        expect(result.state, PanicUXState.MODERATE_PANIC);
      });

      test('classifies frequent sessions as MODERATE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 3.0,
          recentSessionCount: 3,
        ));
        
        expect(result.state, PanicUXState.MODERATE_PANIC);
        expect(result.reason, contains('Frequent sessions'));
      });

      test('classifies previousOutcome=abandoned as MODERATE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 3.0,
          previousOutcome: 'abandoned',
        ));
        
        expect(result.state, PanicUXState.MODERATE_PANIC);
        expect(result.reason, contains('abandoned'));
      });
    });

    group('MILD_PANIC classification', () {
      test('classifies low intensity with no concerning factors as MILD', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 3.0,
        ));
        
        expect(result.state, PanicUXState.MILD_PANIC);
        expect(result.reason, contains('manageable'));
      });

      test('classifies intensity 4 with no other factors as MILD', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 4.0,
          recentSessionCount: 1,
        ));
        
        expect(result.state, PanicUXState.MILD_PANIC);
      });

      test('classifies intensity 1 as MILD', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 1.0,
        ));
        
        expect(result.state, PanicUXState.MILD_PANIC);
      });
    });

    group('Priority ordering', () {
      test('CRITICAL takes priority over SEVERE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 9.0,
          timeToFirstInteractionMs: 35000, // Would be SEVERE alone
        ));
        
        expect(result.state, PanicUXState.CRITICAL_PANIC);
      });

      test('SEVERE takes priority over MODERATE', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 8.0,
          recentSessionCount: 5, // Would be MODERATE alone
        ));
        
        expect(result.state, PanicUXState.SEVERE_PANIC);
      });
    });

    group('Reclassification during session', () {
      test('detects escalation to CRITICAL', () {
        final result = classifier.reclassify(
          currentState: PanicUXState.MODERATE_PANIC,
          newIntensity: 9.5,
          sessionDurationMs: 60000,
        );
        
        expect(result.state, PanicUXState.CRITICAL_PANIC);
        expect(result.reason, contains('escalated to critical'));
      });

      test('detects improvement to MILD', () {
        final result = classifier.reclassify(
          currentState: PanicUXState.SEVERE_PANIC,
          newIntensity: 3.0,
          sessionDurationMs: 120000,
        );
        
        expect(result.state, PanicUXState.MILD_PANIC);
        expect(result.reason, contains('improvement'));
      });

      test('maintains state when no significant change', () {
        final result = classifier.reclassify(
          currentState: PanicUXState.MODERATE_PANIC,
          newIntensity: 5.5,
          sessionDurationMs: 30000,
        );
        
        expect(result.state, PanicUXState.MODERATE_PANIC);
        expect(result.reason, contains('Maintaining'));
      });
    });

    group('Classification result', () {
      test('includes timestamp', () {
        final before = DateTime.now();
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 5.0,
        ));
        final after = DateTime.now();
        
        expect(result.classifiedAt.isAfter(before) || 
               result.classifiedAt.isAtSameMomentAs(before), isTrue);
        expect(result.classifiedAt.isBefore(after) || 
               result.classifiedAt.isAtSameMomentAs(after), isTrue);
      });

      test('toAuditLog contains required fields', () {
        final result = classifier.classify(const PanicClassificationInput(
          intensity: 7.0,
        ));
        
        final log = result.toAuditLog();
        expect(log['state'], isNotNull);
        expect(log['reason'], isNotNull);
        expect(log['timestamp'], isNotNull);
      });
    });
  });
}
