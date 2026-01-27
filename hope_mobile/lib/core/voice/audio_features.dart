/// Audio Features Model
/// 
/// Extracted audio features for breathing and distress detection.
/// These features are calculated from raw sound level data.
/// 
/// CLINICAL NOTE: These are approximations from dB levels only.
/// Full clinical accuracy would require raw audio waveform analysis.

import 'dart:math' as math;

/// Audio features extracted from sound level time series
class AudioFeatures {
  /// Average amplitude in dB over analysis window
  final double meanAmplitude;
  
  /// Peak (maximum) amplitude in dB
  final double peakAmplitude;
  
  /// Minimum amplitude in dB
  final double minAmplitude;
  
  /// Standard deviation of amplitude
  final double amplitudeVariance;
  
  /// Estimated breathing rate (breaths per minute)
  final double breathingRate;
  
  /// Breathing irregularity coefficient (0 = regular, >0.4 = erratic)
  final double irregularityCoefficient;
  
  /// Number of detected breathing cycles
  final int breathingCycles;
  
  /// Whether gasping pattern detected
  final bool gaspingDetected;
  
  /// Whether crying pattern detected
  final bool cryingDetected;
  
  /// Whether stressed silence detected
  final bool stressSilenceDetected;
  
  /// Timestamp of analysis
  final DateTime timestamp;
  
  /// Duration of analysis window
  final Duration analysisWindow;
  
  const AudioFeatures({
    required this.meanAmplitude,
    required this.peakAmplitude,
    required this.minAmplitude,
    required this.amplitudeVariance,
    required this.breathingRate,
    required this.irregularityCoefficient,
    required this.breathingCycles,
    required this.gaspingDetected,
    required this.cryingDetected,
    required this.stressSilenceDetected,
    required this.timestamp,
    required this.analysisWindow,
  });
  
  /// Create empty/default features
  factory AudioFeatures.empty() {
    return AudioFeatures(
      meanAmplitude: -50.0,
      peakAmplitude: -50.0,
      minAmplitude: -50.0,
      amplitudeVariance: 0.0,
      breathingRate: 15.0,
      irregularityCoefficient: 0.0,
      breathingCycles: 0,
      gaspingDetected: false,
      cryingDetected: false,
      stressSilenceDetected: false,
      timestamp: DateTime.now(),
      analysisWindow: Duration.zero,
    );
  }
  
  /// Check if breathing rate indicates hyperventilation
  bool get isHyperventilating => breathingRate > 25.0;
  
  /// Check if breathing is irregular
  bool get isIrregularBreathing => irregularityCoefficient > 0.4;
  
  /// Check if breathing rate is elevated but not hyperventilating
  bool get isElevatedBreathing => breathingRate > 20.0 && breathingRate <= 25.0;
  
  /// Check if any distress pattern is detected
  bool get hasDistressPattern => 
      gaspingDetected || cryingDetected || stressSilenceDetected;
  
  /// Overall distress indicator
  bool get indicatesDistress => 
      isHyperventilating || isIrregularBreathing || hasDistressPattern;
  
  /// Convert to map for logging/analytics
  Map<String, dynamic> toJson() => {
    'meanAmplitude': meanAmplitude,
    'peakAmplitude': peakAmplitude,
    'breathingRate': breathingRate,
    'irregularity': irregularityCoefficient,
    'cycles': breathingCycles,
    'gasping': gaspingDetected,
    'crying': cryingDetected,
    'stressSilence': stressSilenceDetected,
    'timestamp': timestamp.toIso8601String(),
  };
  
  @override
  String toString() => 
      'AudioFeatures(rate=${breathingRate.toStringAsFixed(1)}/min, '
      'irregularity=${irregularityCoefficient.toStringAsFixed(2)}, '
      'distress=$indicatesDistress)';
}

/// Circular buffer for time-series audio data
class AudioSampleBuffer {
  final int maxSamples;
  final List<AudioSample> _samples = [];
  
  AudioSampleBuffer({required this.maxSamples});
  
  /// Add a new sample (auto-removes oldest if full)
  void add(double soundLevel) {
    _samples.add(AudioSample(
      level: soundLevel,
      timestamp: DateTime.now(),
    ));
    
    // Remove oldest samples if over capacity
    while (_samples.length > maxSamples) {
      _samples.removeAt(0);
    }
  }
  
  /// Clear all samples
  void clear() => _samples.clear();
  
  /// Get all samples
  List<AudioSample> get samples => List.unmodifiable(_samples);
  
  /// Get number of samples
  int get length => _samples.length;
  
  /// Check if buffer has enough data for analysis
  bool get hasEnoughData => _samples.length >= maxSamples ~/ 2;
  
  /// Get samples from last N seconds
  List<AudioSample> samplesFromLast(Duration duration) {
    final cutoff = DateTime.now().subtract(duration);
    return _samples.where((s) => s.timestamp.isAfter(cutoff)).toList();
  }
  
  /// Get sound levels as list
  List<double> get levels => _samples.map((s) => s.level).toList();
  
  /// Calculate mean of all samples
  double get mean {
    if (_samples.isEmpty) return -50.0;
    return _samples.map((s) => s.level).reduce((a, b) => a + b) / _samples.length;
  }
  
  /// Calculate variance
  double get variance {
    if (_samples.length < 2) return 0.0;
    final m = mean;
    final sumSquares = _samples.map((s) => math.pow(s.level - m, 2)).reduce((a, b) => a + b);
    return sumSquares / (_samples.length - 1);
  }
  
  /// Calculate standard deviation
  double get standardDeviation => math.sqrt(variance);
  
  /// Get maximum level
  double get max => _samples.isEmpty ? -50.0 : _samples.map((s) => s.level).reduce(math.max);
  
  /// Get minimum level
  double get min => _samples.isEmpty ? -50.0 : _samples.map((s) => s.level).reduce(math.min);
}

/// Single audio sample with timestamp
class AudioSample {
  final double level;
  final DateTime timestamp;
  
  const AudioSample({
    required this.level,
    required this.timestamp,
  });
}
