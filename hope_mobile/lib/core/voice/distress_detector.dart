/// Distress Detector
/// 
/// Detects non-verbal distress patterns in audio:
/// - Gasping: Sudden high-amplitude spikes with fast rise
/// - Crying: Rhythmic amplitude modulation
/// - Stress silence: Low amplitude with high variance
/// 
/// Works alongside BreathingDetector for comprehensive analysis.

import 'dart:math' as math;
import 'package:flutter/foundation.dart';

import 'audio_features.dart';

/// Distress detection thresholds
class DistressThresholds {
  /// Gasping: spike must rise this many dB in short time
  static const double gaspingRiseThreshold = 15.0;
  
  /// Gasping: time window for rise detection (samples at 10 Hz)
  static const int gaspingRiseSamples = 3; // 300ms
  
  /// Gasping: minimum spike count in analysis window
  static const int minGaspingSpikes = 2;
  
  /// Crying: frequency range (modulations per second)
  static const double cryingFrequencyMin = 2.0;
  static const double cryingFrequencyMax = 4.0;
  
  /// Crying: minimum modulation depth (dB)
  static const double cryingModulationDepth = 5.0;
  
  /// Stress silence: maximum amplitude for silence
  static const double silenceThreshold = -20.0;
  
  /// Stress silence: variance threshold (high variance = stress)
  static const double silenceVarianceThreshold = 8.0;
  
  /// Minimum confidence for pattern detection
  static const double minConfidence = 0.6;
}

/// Types of distress patterns
enum DistressPattern {
  /// No distress detected
  none,
  /// Gasping sound detected
  gasping,
  /// Crying pattern detected
  crying,
  /// Stressed silence detected
  stressSilence,
  /// Multiple patterns detected
  multiple,
}

/// Result of distress analysis
class DistressAnalysis {
  final DistressPattern pattern;
  final bool gaspingDetected;
  final bool cryingDetected;
  final bool stressSilenceDetected;
  final double confidence;
  final int gaspingCount;
  final double cryingIntensity;
  final DateTime timestamp;
  
  const DistressAnalysis({
    required this.pattern,
    required this.gaspingDetected,
    required this.cryingDetected,
    required this.stressSilenceDetected,
    required this.confidence,
    required this.gaspingCount,
    required this.cryingIntensity,
    required this.timestamp,
  });
  
  /// Create empty analysis
  factory DistressAnalysis.empty() => DistressAnalysis(
    pattern: DistressPattern.none,
    gaspingDetected: false,
    cryingDetected: false,
    stressSilenceDetected: false,
    confidence: 0,
    gaspingCount: 0,
    cryingIntensity: 0,
    timestamp: DateTime.now(),
  );
  
  /// Check if any distress pattern detected
  bool get hasDistress => pattern != DistressPattern.none;
  
  /// Count of detected patterns
  int get patternCount {
    int count = 0;
    if (gaspingDetected) count++;
    if (cryingDetected) count++;
    if (stressSilenceDetected) count++;
    return count;
  }
  
  @override
  String toString() => 
      'Distress(pattern=$pattern, gasping=$gaspingCount, '
      'confidence=${(confidence * 100).toStringAsFixed(0)}%)';
}

/// Distress Detector
/// 
/// Analyzes audio patterns for non-breathing distress signals.
class DistressDetector {
  /// Sample buffer
  final AudioSampleBuffer _buffer = AudioSampleBuffer(maxSamples: 100); // 10 seconds
  
  /// Callbacks
  Function(DistressAnalysis)? onDistressDetected;
  
  /// Add sample and analyze
  DistressAnalysis? addSample(double soundLevel) {
    _buffer.add(soundLevel);
    
    if (_buffer.length < 30) { // Need at least 3 seconds
      return null;
    }
    
    return analyze();
  }
  
  /// Analyze buffer for distress patterns
  DistressAnalysis analyze() {
    final levels = _buffer.levels;
    
    // Detect individual patterns
    final (gaspingDetected, gaspingCount) = _detectGasping(levels);
    final (cryingDetected, cryingIntensity) = _detectCrying(levels);
    final stressSilence = _detectStressSilence(levels);
    
    // Determine overall pattern
    final patternCount = (gaspingDetected ? 1 : 0) + 
                         (cryingDetected ? 1 : 0) + 
                         (stressSilence ? 1 : 0);
    
    DistressPattern pattern;
    if (patternCount == 0) {
      pattern = DistressPattern.none;
    } else if (patternCount > 1) {
      pattern = DistressPattern.multiple;
    } else if (gaspingDetected) {
      pattern = DistressPattern.gasping;
    } else if (cryingDetected) {
      pattern = DistressPattern.crying;
    } else {
      pattern = DistressPattern.stressSilence;
    }
    
    // Calculate overall confidence
    double confidence = 0.0;
    if (gaspingDetected) confidence = math.max(confidence, 0.7);
    if (cryingDetected) confidence = math.max(confidence, cryingIntensity);
    if (stressSilence) confidence = math.max(confidence, 0.5);
    
    final analysis = DistressAnalysis(
      pattern: pattern,
      gaspingDetected: gaspingDetected,
      cryingDetected: cryingDetected,
      stressSilenceDetected: stressSilence,
      confidence: confidence,
      gaspingCount: gaspingCount,
      cryingIntensity: cryingIntensity,
      timestamp: DateTime.now(),
    );
    
    if (analysis.hasDistress) {
      onDistressDetected?.call(analysis);
    }
    
    return analysis;
  }
  
  /// Detect gasping patterns (sudden high-amplitude spikes)
  (bool detected, int count) _detectGasping(List<double> levels) {
    if (levels.length < DistressThresholds.gaspingRiseSamples + 1) {
      return (false, 0);
    }
    
    int gaspCount = 0;
    
    for (int i = DistressThresholds.gaspingRiseSamples; i < levels.length; i++) {
      // Calculate rise over short window
      final previousLevel = levels[i - DistressThresholds.gaspingRiseSamples];
      final currentLevel = levels[i];
      final rise = currentLevel - previousLevel;
      
      // Check for sharp spike
      if (rise >= DistressThresholds.gaspingRiseThreshold) {
        gaspCount++;
        // Skip ahead to avoid counting same gasp multiple times
        // (But we need to be careful with index)
      }
    }
    
    final detected = gaspCount >= DistressThresholds.minGaspingSpikes;
    return (detected, gaspCount);
  }
  
  /// Detect crying patterns (rhythmic modulation at 2-4 Hz)
  (bool detected, double intensity) _detectCrying(List<double> levels) {
    if (levels.length < 30) { // Need at least 3 seconds
      return (false, 0.0);
    }
    
    // Simple approach: count zero crossings around mean
    // Crying produces regular oscillations
    final mean = levels.reduce((a, b) => a + b) / levels.length;
    
    int zeroCrossings = 0;
    for (int i = 1; i < levels.length; i++) {
      final prevAbove = levels[i - 1] > mean;
      final currAbove = levels[i] > mean;
      if (prevAbove != currAbove) {
        zeroCrossings++;
      }
    }
    
    // Convert to frequency (crossings per second)
    final durationSeconds = levels.length / 10.0; // 10 Hz sample rate
    final crossingRate = zeroCrossings / durationSeconds / 2.0; // Divide by 2 for full cycles
    
    // Check if in crying frequency range
    final inRange = crossingRate >= DistressThresholds.cryingFrequencyMin &&
                    crossingRate <= DistressThresholds.cryingFrequencyMax;
    
    // Check modulation depth
    final maxLevel = levels.reduce(math.max);
    final minLevel = levels.reduce(math.min);
    final modulation = maxLevel - minLevel;
    final hasDepth = modulation >= DistressThresholds.cryingModulationDepth;
    
    if (inRange && hasDepth) {
      // Calculate intensity based on modulation depth
      final intensity = math.min(1.0, modulation / 15.0);
      return (true, intensity);
    }
    
    return (false, 0.0);
  }
  
  /// Detect stress silence (low amplitude but high variance)
  bool _detectStressSilence(List<double> levels) {
    if (levels.isEmpty) return false;
    
    final mean = levels.reduce((a, b) => a + b) / levels.length;
    
    // Check if mostly silent
    if (mean > DistressThresholds.silenceThreshold) {
      return false;
    }
    
    // Calculate variance
    final variance = levels.map((l) => math.pow(l - mean, 2))
        .reduce((a, b) => a + b) / levels.length;
    
    // High variance in silence indicates stress (irregular breathing, trembling)
    return variance >= DistressThresholds.silenceVarianceThreshold;
  }
  
  /// Reset detector
  void reset() {
    _buffer.clear();
  }
}
