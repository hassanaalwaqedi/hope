/// Panic Score Calculator
/// 
/// Combines breathing and distress analysis into a unified panic score.
/// Implements false positive prevention with multiple validation layers.
/// 
/// SCORING FORMULA:
/// panicScore = (
///   0.35 × hyperventilationScore +
///   0.25 × irregularityScore +
///   0.20 × gaspingScore +
///   0.10 × cryingScore +
///   0.10 × silenceStressScore
/// ) × contextMultiplier
/// 
/// FALSE POSITIVE PREVENTION:
/// 1. Temporal persistence (10+ seconds)
/// 2. Confidence threshold (0.7)
/// 3. Speech exclusion
/// 4. Cooldown period (30 seconds)

import 'dart:async';
import 'package:flutter/foundation.dart';

import 'breathing_detector.dart';
import 'distress_detector.dart';
import 'audio_features.dart';

/// Context that affects panic sensitivity
enum PanicContext {
  /// Normal operation
  normal,
  /// User previously pressed panic button
  userInitiated,
  /// Previous panic in this session
  previousPanic,
  /// Night hours (higher isolation risk)
  nightTime,
}

/// Panic score result
class PanicScore {
  /// Overall panic score (0.0 - 1.0)
  final double value;
  
  /// Individual component scores
  final double hyperventilationScore;
  final double irregularityScore;
  final double gaspingScore;
  final double cryingScore;
  final double silenceStressScore;
  
  /// Context multiplier applied
  final double contextMultiplier;
  
  /// How long distress has persisted
  final Duration persistedFor;
  
  /// Confidence in the score
  final double confidence;
  
  /// Whether trigger conditions are met
  final bool shouldTrigger;
  
  /// Reason for trigger (or why not)
  final String triggerReason;
  
  /// Timestamp
  final DateTime timestamp;
  
  const PanicScore({
    required this.value,
    required this.hyperventilationScore,
    required this.irregularityScore,
    required this.gaspingScore,
    required this.cryingScore,
    required this.silenceStressScore,
    required this.contextMultiplier,
    required this.persistedFor,
    required this.confidence,
    required this.shouldTrigger,
    required this.triggerReason,
    required this.timestamp,
  });
  
  /// Create empty score
  factory PanicScore.empty() => PanicScore(
    value: 0,
    hyperventilationScore: 0,
    irregularityScore: 0,
    gaspingScore: 0,
    cryingScore: 0,
    silenceStressScore: 0,
    contextMultiplier: 1.0,
    persistedFor: Duration.zero,
    confidence: 0,
    shouldTrigger: false,
    triggerReason: 'Insufficient data',
    timestamp: DateTime.now(),
  );
  
  /// Severity level based on score
  String get severity {
    if (value >= 0.8) return 'CRITICAL';
    if (value >= 0.6) return 'HIGH';
    if (value >= 0.4) return 'MODERATE';
    if (value >= 0.2) return 'LOW';
    return 'MINIMAL';
  }
  
  @override
  String toString() => 
      'PanicScore(value=${(value * 100).toStringAsFixed(0)}%, '
      'severity=$severity, trigger=$shouldTrigger)';
}

/// Panic Score Calculator
/// 
/// Combines multiple detection sources into unified panic assessment.
class PanicScoreCalculator {
  /// Trigger threshold
  static const double triggerThreshold = 0.7;
  
  /// Minimum persistence for trigger
  static const Duration minPersistence = Duration(seconds: 10);
  
  /// Cooldown between triggers
  static const Duration cooldownDuration = Duration(seconds: 30);
  
  /// Weight factors
  static const double weightHyperventilation = 0.35;
  static const double weightIrregularity = 0.25;
  static const double weightGasping = 0.20;
  static const double weightCrying = 0.10;
  static const double weightSilenceStress = 0.10;
  
  /// Context multipliers
  static const Map<PanicContext, double> contextMultipliers = {
    PanicContext.normal: 1.0,
    PanicContext.userInitiated: 1.5,
    PanicContext.previousPanic: 1.3,
    PanicContext.nightTime: 1.2,
  };
  
  /// Current context
  PanicContext _context = PanicContext.normal;
  
  /// Last trigger time
  DateTime? _lastTriggerTime;
  
  /// Whether speech is currently detected
  bool _isSpeechDetected = false;
  
  /// Distress start time (for persistence tracking)
  DateTime? _distressStartTime;
  
  /// Callbacks
  Function(PanicScore)? onScoreCalculated;
  Function(PanicScore)? onPanicTriggered;
  
  /// Set current context
  void setContext(PanicContext context) {
    _context = context;
    debugPrint('PanicScoreCalculator: Context set to $context');
  }
  
  /// Notify that speech was detected (suppresses false positives)
  void setSpeechDetected(bool detected) {
    _isSpeechDetected = detected;
  }
  
  /// Check if in cooldown
  bool get isInCooldown {
    if (_lastTriggerTime == null) return false;
    return DateTime.now().difference(_lastTriggerTime!) < cooldownDuration;
  }
  
  /// Calculate panic score from breathing and distress analysis
  PanicScore calculate({
    required BreathingAnalysis breathing,
    required DistressAnalysis distress,
  }) {
    // Calculate individual component scores (0.0 - 1.0)
    
    // Hyperventilation score
    double hyperScore = 0.0;
    if (breathing.state == BreathingState.hyperventilating) {
      // Scale based on how far above threshold
      final excess = breathing.breathingRate - 25.0;
      hyperScore = (0.7 + (excess / 20.0)).clamp(0.0, 1.0);
    } else if (breathing.state == BreathingState.elevated) {
      hyperScore = 0.3;
    }
    
    // Irregularity score
    double irregularityScore = 0.0;
    if (breathing.irregularity > 0.4) {
      irregularityScore = ((breathing.irregularity - 0.4) / 0.3 + 0.5).clamp(0.0, 1.0);
    } else if (breathing.irregularity > 0.2) {
      irregularityScore = 0.3;
    }
    
    // Gasping score
    double gaspingScore = 0.0;
    if (distress.gaspingDetected) {
      gaspingScore = (0.6 + (distress.gaspingCount / 5.0) * 0.4).clamp(0.0, 1.0);
    }
    
    // Crying score
    double cryingScore = 0.0;
    if (distress.cryingDetected) {
      cryingScore = distress.cryingIntensity;
    }
    
    // Silence stress score
    double silenceScore = distress.stressSilenceDetected ? 0.6 : 0.0;
    
    // Calculate weighted score
    double baseScore = 
        weightHyperventilation * hyperScore +
        weightIrregularity * irregularityScore +
        weightGasping * gaspingScore +
        weightCrying * cryingScore +
        weightSilenceStress * silenceScore;
    
    // Apply context multiplier
    final multiplier = contextMultipliers[_context] ?? 1.0;
    final finalScore = (baseScore * multiplier).clamp(0.0, 1.0);
    
    // Track persistence
    final persistedFor = _trackPersistence(finalScore >= 0.5);
    
    // Calculate overall confidence
    final confidence = (breathing.confidence + distress.confidence) / 2.0;
    
    // Determine if should trigger
    final (shouldTrigger, reason) = _shouldTrigger(
      score: finalScore,
      confidence: confidence,
      persistedFor: persistedFor,
    );
    
    final panicScore = PanicScore(
      value: finalScore,
      hyperventilationScore: hyperScore,
      irregularityScore: irregularityScore,
      gaspingScore: gaspingScore,
      cryingScore: cryingScore,
      silenceStressScore: silenceScore,
      contextMultiplier: multiplier,
      persistedFor: persistedFor,
      confidence: confidence,
      shouldTrigger: shouldTrigger,
      triggerReason: reason,
      timestamp: DateTime.now(),
    );
    
    // Notify callbacks
    onScoreCalculated?.call(panicScore);
    
    if (shouldTrigger) {
      _lastTriggerTime = DateTime.now();
      onPanicTriggered?.call(panicScore);
    }
    
    return panicScore;
  }
  
  /// Track persistence of elevated score
  Duration _trackPersistence(bool isElevated) {
    if (isElevated) {
      _distressStartTime ??= DateTime.now();
      return DateTime.now().difference(_distressStartTime!);
    } else {
      _distressStartTime = null;
      return Duration.zero;
    }
  }
  
  /// Determine if panic should be triggered
  (bool, String) _shouldTrigger({
    required double score,
    required double confidence,
    required Duration persistedFor,
  }) {
    // Check cooldown
    if (isInCooldown) {
      return (false, 'In cooldown period');
    }
    
    // Check speech (false positive indicator)
    if (_isSpeechDetected) {
      return (false, 'Speech detected - not panic pattern');
    }
    
    // Check score threshold
    if (score < triggerThreshold) {
      return (false, 'Score below threshold (${(score * 100).toStringAsFixed(0)}% < 70%)');
    }
    
    // Check confidence
    if (confidence < 0.5) {
      return (false, 'Low confidence (${(confidence * 100).toStringAsFixed(0)}%)');
    }
    
    // Check persistence
    if (persistedFor < minPersistence) {
      final remaining = minPersistence.inSeconds - persistedFor.inSeconds;
      return (false, 'Not persisted long enough ($remaining seconds remaining)');
    }
    
    // All conditions met
    return (true, 'Distress pattern confirmed - triggering panic support');
  }
  
  /// Reset calculator state
  void reset() {
    _distressStartTime = null;
    _isSpeechDetected = false;
    _context = PanicContext.normal;
  }
  
  /// Force start cooldown (e.g., after user interaction)
  void startCooldown() {
    _lastTriggerTime = DateTime.now();
  }
}
