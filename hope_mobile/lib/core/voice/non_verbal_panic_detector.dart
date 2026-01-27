/// Non-Verbal Panic Detector
/// 
/// Main integration class that coordinates:
/// - BreathingDetector: Hyperventilation and irregular breathing
/// - DistressDetector: Gasping, crying, stress silence
/// - PanicScoreCalculator: Unified scoring and trigger logic
/// 
/// This class:
/// 1. Receives raw sound level data from onSoundLevelChange
/// 2. Feeds data to all detectors
/// 3. Combines results into panic score
/// 4. Triggers panic flow when thresholds are met
/// 
/// DOES NOT require speech recognition to activate panic mode.

import 'dart:async';
import 'package:flutter/foundation.dart';

import 'breathing_detector.dart';
import 'distress_detector.dart';
import 'panic_score_calculator.dart';
import 'audio_features.dart';

/// Non-verbal panic trigger event
class NonVerbalPanicTrigger {
  final PanicScore score;
  final BreathingAnalysis breathing;
  final DistressAnalysis distress;
  final String triggerReason;
  final DateTime timestamp;
  
  const NonVerbalPanicTrigger({
    required this.score,
    required this.breathing,
    required this.distress,
    required this.triggerReason,
    required this.timestamp,
  });
  
  /// Summary of what triggered the panic
  String get summary {
    final triggers = <String>[];
    
    if (breathing.state == BreathingState.hyperventilating) {
      triggers.add('hyperventilation (${breathing.breathingRate.toStringAsFixed(0)}/min)');
    }
    if (breathing.state == BreathingState.irregular) {
      triggers.add('irregular breathing');
    }
    if (distress.gaspingDetected) {
      triggers.add('gasping (${distress.gaspingCount}x)');
    }
    if (distress.cryingDetected) {
      triggers.add('crying pattern');
    }
    if (distress.stressSilenceDetected) {
      triggers.add('stress silence');
    }
    
    return triggers.isEmpty ? 'Unknown trigger' : triggers.join(', ');
  }
  
  @override
  String toString() => 'NonVerbalPanicTrigger($summary)';
}

/// Detection status for UI feedback
class DetectionStatus {
  final bool isActive;
  final BreathingState breathingState;
  final double breathingRate;
  final double panicScore;
  final Duration persistedFor;
  final String statusMessage;
  
  const DetectionStatus({
    required this.isActive,
    required this.breathingState,
    required this.breathingRate,
    required this.panicScore,
    required this.persistedFor,
    required this.statusMessage,
  });
  
  factory DetectionStatus.inactive() => const DetectionStatus(
    isActive: false,
    breathingState: BreathingState.insufficient,
    breathingRate: 0,
    panicScore: 0,
    persistedFor: Duration.zero,
    statusMessage: 'Detection inactive',
  );
}

/// Non-Verbal Panic Detector
/// 
/// Central coordinator for all non-verbal panic detection.
class NonVerbalPanicDetector {
  /// Breathing detector
  final BreathingDetector _breathingDetector = BreathingDetector();
  
  /// Distress pattern detector
  final DistressDetector _distressDetector = DistressDetector();
  
  /// Panic score calculator
  final PanicScoreCalculator _scoreCalculator = PanicScoreCalculator();
  
  /// Whether detection is active
  bool _isActive = false;
  
  /// Last analysis results (for combining)
  BreathingAnalysis? _lastBreathingAnalysis;
  DistressAnalysis? _lastDistressAnalysis;
  
  /// Analysis interval (don't analyze every sample)
  int _sampleCount = 0;
  static const int _analysisInterval = 10; // Analyze every 10 samples (~1 second)
  
  /// Callbacks
  Function(NonVerbalPanicTrigger)? onPanicTriggered;
  Function(DetectionStatus)? onStatusChanged;
  Function(PanicScore)? onScoreUpdated;
  
  /// Whether detection is active
  bool get isActive => _isActive;
  
  /// Current panic score (0-1)
  double get currentScore => _lastScore?.value ?? 0.0;
  
  PanicScore? _lastScore;
  
  /// Start detection
  /// 
  /// Call this when entering panic-sensitive mode.
  void start() {
    _isActive = true;
    _sampleCount = 0;
    _lastBreathingAnalysis = null;
    _lastDistressAnalysis = null;
    _lastScore = null;
    
    // Set up internal callbacks
    _scoreCalculator.onPanicTriggered = _handlePanicTriggered;
    
    debugPrint('NonVerbalPanicDetector: Started');
    
    _notifyStatus('Monitoring active');
  }
  
  /// Stop detection
  void stop() {
    _isActive = false;
    _breathingDetector.reset();
    _distressDetector.reset();
    _scoreCalculator.reset();
    
    debugPrint('NonVerbalPanicDetector: Stopped');
    
    onStatusChanged?.call(DetectionStatus.inactive());
  }
  
  /// Set context (affects sensitivity)
  void setContext(PanicContext context) {
    _scoreCalculator.setContext(context);
  }
  
  /// Notify that speech was detected (suppresses false positives)
  void notifySpeechDetected(bool detected) {
    _scoreCalculator.setSpeechDetected(detected);
  }
  
  /// Process sound level sample
  /// 
  /// Call this with each onSoundLevelChange callback.
  /// Detection runs on-device, no network required.
  void processSample(double soundLevel) {
    if (!_isActive) return;
    
    // Feed to breathing detector
    final breathingResult = _breathingDetector.addSample(soundLevel);
    if (breathingResult != null) {
      _lastBreathingAnalysis = breathingResult;
    }
    
    // Feed to distress detector
    final distressResult = _distressDetector.addSample(soundLevel);
    if (distressResult != null) {
      _lastDistressAnalysis = distressResult;
    }
    
    // Analyze periodically (not every sample)
    _sampleCount++;
    if (_sampleCount >= _analysisInterval) {
      _sampleCount = 0;
      _performAnalysis();
    }
  }
  
  /// Perform combined analysis
  void _performAnalysis() {
    // Need both analyses
    if (_lastBreathingAnalysis == null || _lastDistressAnalysis == null) {
      return;
    }
    
    // Calculate combined panic score
    final score = _scoreCalculator.calculate(
      breathing: _lastBreathingAnalysis!,
      distress: _lastDistressAnalysis!,
    );
    
    _lastScore = score;
    onScoreUpdated?.call(score);
    
    // Update status
    _notifyStatus(_getStatusMessage(score));
  }
  
  /// Handle panic trigger from score calculator
  void _handlePanicTriggered(PanicScore score) {
    if (_lastBreathingAnalysis == null || _lastDistressAnalysis == null) {
      return;
    }
    
    final trigger = NonVerbalPanicTrigger(
      score: score,
      breathing: _lastBreathingAnalysis!,
      distress: _lastDistressAnalysis!,
      triggerReason: score.triggerReason,
      timestamp: DateTime.now(),
    );
    
    debugPrint('NonVerbalPanicDetector: PANIC TRIGGERED - ${trigger.summary}');
    
    onPanicTriggered?.call(trigger);
  }
  
  /// Get status message for current state
  String _getStatusMessage(PanicScore score) {
    if (score.shouldTrigger) {
      return 'Panic support activating...';
    }
    
    if (score.value >= 0.5) {
      final remaining = 10 - score.persistedFor.inSeconds;
      if (remaining > 0) {
        return 'Elevated distress detected (${remaining}s to confirm)';
      }
    }
    
    if (_lastBreathingAnalysis?.state == BreathingState.hyperventilating) {
      return 'Rapid breathing detected';
    }
    
    if (_lastBreathingAnalysis?.state == BreathingState.elevated) {
      return 'Breathing slightly elevated';
    }
    
    if (_lastDistressAnalysis?.hasDistress == true) {
      return 'Distress pattern detected';
    }
    
    return 'Monitoring breathing patterns';
  }
  
  /// Notify status change
  void _notifyStatus(String message) {
    if (!_isActive) return;
    
    final status = DetectionStatus(
      isActive: _isActive,
      breathingState: _lastBreathingAnalysis?.state ?? BreathingState.insufficient,
      breathingRate: _lastBreathingAnalysis?.breathingRate ?? 0,
      panicScore: _lastScore?.value ?? 0,
      persistedFor: _lastScore?.persistedFor ?? Duration.zero,
      statusMessage: message,
    );
    
    onStatusChanged?.call(status);
  }
  
  /// Force trigger cooldown (after user interaction)
  void startCooldown() {
    _scoreCalculator.startCooldown();
    _breathingDetector.startCooldown();
  }
  
  /// Reset all detectors
  void reset() {
    _breathingDetector.reset();
    _distressDetector.reset();
    _scoreCalculator.reset();
    _lastBreathingAnalysis = null;
    _lastDistressAnalysis = null;
    _lastScore = null;
    _sampleCount = 0;
  }
}
