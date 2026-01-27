/// Breathing Detector
/// 
/// Clinical-grade breathing pattern detection from sound level data.
/// Detects hyperventilation, irregular breathing, and distress patterns.
/// 
/// ALGORITHM:
/// 1. Collect sound levels in 30-second sliding window
/// 2. Apply smoothing to reduce noise
/// 3. Detect peaks (inhale/exhale boundaries)
/// 4. Calculate breathing rate from peak intervals
/// 5. Measure irregularity from interval variance
/// 
/// CLINICAL THRESHOLDS:
/// - Normal breathing: 12-20 breaths/min
/// - Elevated: 20-25 breaths/min  
/// - Hyperventilation: >25 breaths/min
/// - Irregular: coefficient of variation > 0.4

import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/foundation.dart';

import 'audio_features.dart';

/// Breathing detection thresholds (clinical values)
class BreathingThresholds {
  /// Normal breathing range
  static const double normalMin = 12.0;
  static const double normalMax = 20.0;
  
  /// Elevated breathing (warning)
  static const double elevatedMin = 20.0;
  static const double elevatedMax = 25.0;
  
  /// Hyperventilation threshold
  static const double hyperventilationThreshold = 25.0;
  
  /// Irregularity thresholds
  static const double normalIrregularity = 0.2;
  static const double warningIrregularity = 0.4;
  
  /// Minimum peak amplitude to detect breathing (dB above baseline)
  static const double minPeakHeight = 3.0;
  
  /// Minimum interval between peaks (seconds) - 40 breaths/min max
  static const double minPeakInterval = 1.5;
  
  /// Maximum interval between peaks (seconds) - 10 breaths/min min
  static const double maxPeakInterval = 6.0;
  
  /// Persistence required before triggering (seconds)
  static const int persistenceSeconds = 10;
  
  /// Cooldown between triggers (seconds)
  static const int cooldownSeconds = 30;
}

/// Breathing pattern state
enum BreathingState {
  /// Normal breathing detected
  normal,
  /// Slightly elevated but not alarming
  elevated,
  /// Hyperventilation detected
  hyperventilating,
  /// Irregular breathing pattern
  irregular,
  /// No clear pattern (speech, silence, noise)
  unclear,
  /// Insufficient data for analysis
  insufficient,
}

/// Result of breathing analysis
class BreathingAnalysis {
  final BreathingState state;
  final double breathingRate;
  final double irregularity;
  final int cyclesDetected;
  final double confidence;
  final DateTime timestamp;
  final Duration persistedFor;
  
  const BreathingAnalysis({
    required this.state,
    required this.breathingRate,
    required this.irregularity,
    required this.cyclesDetected,
    required this.confidence,
    required this.timestamp,
    required this.persistedFor,
  });
  
  /// Create empty analysis
  factory BreathingAnalysis.empty() => BreathingAnalysis(
    state: BreathingState.insufficient,
    breathingRate: 0,
    irregularity: 0,
    cyclesDetected: 0,
    confidence: 0,
    timestamp: DateTime.now(),
    persistedFor: Duration.zero,
  );
  
  /// Check if this indicates distress
  bool get indicatesDistress => 
      state == BreathingState.hyperventilating ||
      state == BreathingState.irregular;
  
  /// Check if persisted long enough to trigger
  bool get persistedEnough => 
      persistedFor.inSeconds >= BreathingThresholds.persistenceSeconds;
  
  @override
  String toString() => 
      'Breathing(state=$state, rate=${breathingRate.toStringAsFixed(1)}/min, '
      'confidence=${(confidence * 100).toStringAsFixed(0)}%)';
}

/// Breathing Detector
/// 
/// Analyzes sound level data to detect breathing patterns.
/// Works on-device without network dependency.
class BreathingDetector {
  /// Sample buffer (10 Hz for 30 seconds = 300 samples)
  final AudioSampleBuffer _buffer = AudioSampleBuffer(maxSamples: 300);
  
  /// Analysis window
  final Duration _analysisWindow = const Duration(seconds: 30);
  
  /// Previous distress state start (for persistence tracking)
  DateTime? _distressStartTime;
  
  /// Last trigger time (for cooldown)
  DateTime? _lastTriggerTime;
  
  /// Current state
  BreathingState _currentState = BreathingState.insufficient;
  
  /// Callbacks
  Function(BreathingAnalysis)? onAnalysisComplete;
  Function(BreathingAnalysis)? onDistressDetected;
  
  /// Get current state
  BreathingState get currentState => _currentState;
  
  /// Check if in cooldown period
  bool get isInCooldown {
    if (_lastTriggerTime == null) return false;
    return DateTime.now().difference(_lastTriggerTime!).inSeconds < 
           BreathingThresholds.cooldownSeconds;
  }
  
  /// Add sound level sample
  /// 
  /// Call this with each onSoundLevelChange callback.
  /// Returns analysis result if enough data, null otherwise.
  BreathingAnalysis? addSample(double soundLevel) {
    _buffer.add(soundLevel);
    
    // Only analyze if we have enough data
    if (!_buffer.hasEnoughData) {
      return null;
    }
    
    return analyze();
  }
  
  /// Perform breathing analysis on current buffer
  BreathingAnalysis analyze() {
    if (_buffer.length < 50) {
      return BreathingAnalysis.empty();
    }
    
    final levels = _buffer.levels;
    
    // Step 1: Smooth the signal (moving average)
    final smoothed = _smoothSignal(levels, windowSize: 5);
    
    // Step 2: Detect peaks
    final peaks = _detectPeaks(smoothed);
    
    // Step 3: Calculate breathing metrics
    final (rate, irregularity, confidence) = _calculateBreathingMetrics(peaks);
    
    // Step 4: Determine state
    final state = _determineState(rate, irregularity, peaks.length, confidence);
    
    // Step 5: Track persistence
    final persistedFor = _trackPersistence(state);
    
    _currentState = state;
    
    final analysis = BreathingAnalysis(
      state: state,
      breathingRate: rate,
      irregularity: irregularity,
      cyclesDetected: peaks.length > 1 ? peaks.length - 1 : 0,
      confidence: confidence,
      timestamp: DateTime.now(),
      persistedFor: persistedFor,
    );
    
    // Notify callbacks
    onAnalysisComplete?.call(analysis);
    
    // Check for distress trigger
    if (analysis.indicatesDistress && 
        analysis.persistedEnough && 
        !isInCooldown) {
      _lastTriggerTime = DateTime.now();
      onDistressDetected?.call(analysis);
    }
    
    return analysis;
  }
  
  /// Smooth signal with moving average
  List<double> _smoothSignal(List<double> signal, {int windowSize = 5}) {
    if (signal.length < windowSize) return signal;
    
    final smoothed = <double>[];
    final halfWindow = windowSize ~/ 2;
    
    for (int i = 0; i < signal.length; i++) {
      final start = math.max(0, i - halfWindow);
      final end = math.min(signal.length, i + halfWindow + 1);
      final window = signal.sublist(start, end);
      smoothed.add(window.reduce((a, b) => a + b) / window.length);
    }
    
    return smoothed;
  }
  
  /// Detect peaks in smoothed signal
  List<_Peak> _detectPeaks(List<double> signal) {
    if (signal.length < 3) return [];
    
    final peaks = <_Peak>[];
    final baseline = signal.reduce((a, b) => a + b) / signal.length;
    final threshold = baseline + BreathingThresholds.minPeakHeight;
    
    for (int i = 1; i < signal.length - 1; i++) {
      // Check if this is a local maximum above threshold
      if (signal[i] > signal[i - 1] && 
          signal[i] > signal[i + 1] &&
          signal[i] > threshold) {
        
        // Check minimum distance from previous peak
        if (peaks.isEmpty || 
            (i - peaks.last.index) >= 15) { // ~1.5 seconds at 10 Hz
          peaks.add(_Peak(index: i, value: signal[i]));
        }
      }
    }
    
    return peaks;
  }
  
  /// Calculate breathing metrics from peaks
  (double rate, double irregularity, double confidence) _calculateBreathingMetrics(
    List<_Peak> peaks,
  ) {
    if (peaks.length < 2) {
      return (0.0, 0.0, 0.0);
    }
    
    // Calculate inter-peak intervals (in samples, 10 Hz)
    final intervals = <double>[];
    for (int i = 1; i < peaks.length; i++) {
      final intervalSamples = (peaks[i].index - peaks[i - 1].index).toDouble();
      final intervalSeconds = intervalSamples / 10.0; // 10 Hz sample rate
      
      // Only include valid intervals
      if (intervalSeconds >= BreathingThresholds.minPeakInterval &&
          intervalSeconds <= BreathingThresholds.maxPeakInterval) {
        intervals.add(intervalSeconds);
      }
    }
    
    if (intervals.isEmpty) {
      return (0.0, 0.0, 0.0);
    }
    
    // Calculate mean interval
    final meanInterval = intervals.reduce((a, b) => a + b) / intervals.length;
    
    // Calculate breathing rate (breaths per minute)
    final rate = 60.0 / meanInterval;
    
    // Calculate irregularity (coefficient of variation)
    double irregularity = 0.0;
    if (intervals.length > 1) {
      final variance = intervals.map((i) => math.pow(i - meanInterval, 2))
          .reduce((a, b) => a + b) / (intervals.length - 1);
      final stdDev = math.sqrt(variance);
      irregularity = stdDev / meanInterval;
    }
    
    // Calculate confidence based on number of cycles and consistency
    final cycleConfidence = math.min(1.0, intervals.length / 5.0);
    final consistencyConfidence = math.max(0.0, 1.0 - irregularity);
    final confidence = (cycleConfidence + consistencyConfidence) / 2.0;
    
    return (rate, irregularity, confidence);
  }
  
  /// Determine breathing state from metrics
  BreathingState _determineState(
    double rate,
    double irregularity,
    int peakCount,
    double confidence,
  ) {
    // Not enough peaks for reliable detection
    if (peakCount < 3 || confidence < 0.3) {
      return BreathingState.unclear;
    }
    
    // High irregularity indicates erratic breathing
    if (irregularity > BreathingThresholds.warningIrregularity) {
      return BreathingState.irregular;
    }
    
    // Check breathing rate
    if (rate > BreathingThresholds.hyperventilationThreshold) {
      return BreathingState.hyperventilating;
    } else if (rate > BreathingThresholds.elevatedMax) {
      return BreathingState.elevated;
    } else if (rate >= BreathingThresholds.normalMin && 
               rate <= BreathingThresholds.normalMax) {
      return BreathingState.normal;
    } else if (rate < BreathingThresholds.normalMin) {
      // Very slow breathing - could be deep calming breaths
      return BreathingState.normal;
    }
    
    return BreathingState.elevated;
  }
  
  /// Track how long distress state has persisted
  Duration _trackPersistence(BreathingState state) {
    final isDistress = state == BreathingState.hyperventilating ||
                       state == BreathingState.irregular;
    
    if (isDistress) {
      _distressStartTime ??= DateTime.now();
      return DateTime.now().difference(_distressStartTime!);
    } else {
      _distressStartTime = null;
      return Duration.zero;
    }
  }
  
  /// Reset detector state
  void reset() {
    _buffer.clear();
    _distressStartTime = null;
    _currentState = BreathingState.insufficient;
  }
  
  /// Force trigger cooldown (e.g., after user interaction)
  void startCooldown() {
    _lastTriggerTime = DateTime.now();
  }
}

/// Internal peak representation
class _Peak {
  final int index;
  final double value;
  
  const _Peak({required this.index, required this.value});
}
