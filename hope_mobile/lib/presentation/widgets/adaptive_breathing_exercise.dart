/// Adaptive Breathing Exercise
/// 
/// Production-grade breathing exercise with:
/// - Dynamic tempo based on intensity
/// - Auto-escalation callbacks
/// - Smooth transitions
/// - Cycle tracking for observability

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../core/theme/app_theme.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../panic/ux/panic_analytics.dart';
import '../widgets/intensity_slider.dart';

class AdaptiveBreathingExercise extends StatefulWidget {
  final Map<String, dynamic> config;
  final double intensity;
  final String? message;
  final bool isConnected;
  final bool voiceEnabled;
  
  const AdaptiveBreathingExercise({
    super.key,
    required this.config,
    required this.intensity,
    this.message,
    this.isConnected = false,
    this.voiceEnabled = false,
  });

  @override
  State<AdaptiveBreathingExercise> createState() => _AdaptiveBreathingExerciseState();
}

class _AdaptiveBreathingExerciseState extends State<AdaptiveBreathingExercise>
    with TickerProviderStateMixin {
  late AnimationController _breathController;
  late Animation<double> _scaleAnimation;
  
  int _phase = 0; // 0: inhale, 1: hold, 2: exhale
  int _cycleCount = 0;
  double _currentIntensity = 5.0;
  
  final _analytics = PanicAnalytics.instance;
  final _stopwatch = Stopwatch();
  
  // Adaptive timing based on config
  late int _inhaleDuration;
  late int _holdDuration;
  late int _exhaleDuration;

  final List<String> _phaseLabels = [
    'Breathe in slowly...',
    'Hold gently...',
    'Let it all out...',
  ];

  final List<Color> _phaseColors = [
    const Color(0xFF7C9A92),
    const Color(0xFF6B7FD7),
    const Color(0xFFD4A373),
  ];

  @override
  void initState() {
    super.initState();
    _stopwatch.start();
    _currentIntensity = widget.intensity;
    
    // Get adaptive timing from config
    _inhaleDuration = widget.config['inhaleDuration'] as int? ?? 4;
    _holdDuration = widget.config['holdDuration'] as int? ?? 4;
    _exhaleDuration = widget.config['exhaleDuration'] as int? ?? 6;
    
    // Adjust for intensity if not specified
    if (widget.intensity > 7) {
      // Slower breathing for higher intensity
      _inhaleDuration = 5;
      _holdDuration = 5;
      _exhaleDuration = 7;
    }
    
    _startBreathingCycle();
  }

  void _startBreathingCycle() {
    _phase = 0;
    _breathController = AnimationController(
      duration: Duration(seconds: _inhaleDuration),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _breathController, curve: Curves.easeInOut),
    );

    _breathController.forward().then((_) => _onPhaseComplete());
  }

  void _onPhaseComplete() {
    if (!mounted) return;
    
    HapticFeedback.lightImpact();
    
    setState(() {
      _phase = (_phase + 1) % 3;
      if (_phase == 0) {
        _cycleCount++;
        context.read<PanicBloc>().add(const ExerciseCycleCompleted());
      }
    });

    final duration = switch (_phase) {
      0 => _inhaleDuration,
      1 => _holdDuration,
      2 => _exhaleDuration,
      _ => 4,
    };

    _breathController.dispose();
    _breathController = AnimationController(
      duration: Duration(seconds: duration),
      vsync: this,
    );

    if (_phase == 0) {
      _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
        CurvedAnimation(parent: _breathController, curve: Curves.easeInOut),
      );
    } else if (_phase == 1) {
      _scaleAnimation = Tween<double>(begin: 1.0, end: 1.0).animate(
        CurvedAnimation(parent: _breathController, curve: Curves.linear),
      );
    } else {
      _scaleAnimation = Tween<double>(begin: 1.0, end: 0.5).animate(
        CurvedAnimation(parent: _breathController, curve: Curves.easeInOut),
      );
    }

    _breathController.forward().then((_) => _onPhaseComplete());
  }

  @override
  void dispose() {
    _stopwatch.stop();
    _breathController.dispose();
    _analytics.logExerciseCompleted(
      exerciseType: 'breathing',
      durationMs: _stopwatch.elapsedMilliseconds,
      cycles: _cycleCount,
    );
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currentColor = _phaseColors[_phase];
    
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) _showExitConfirmation();
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF1A1A2E),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
            child: Column(
              children: [
                // Header
                _buildHeader(),
                
                const Spacer(),
                
                // Message from server/local
                if (widget.message != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: Text(
                      widget.message!,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontSize: 18,
                        color: Colors.white.withOpacity(0.8),
                        height: 1.4,
                      ),
                    ),
                  ),
                
                const SizedBox(height: 32),

                // Instruction
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: Text(
                    _phaseLabels[_phase],
                    key: ValueKey(_phase),
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w400,
                      color: currentColor,
                    ),
                  ),
                ),
                
                const SizedBox(height: 32),

                // Animated breathing circle
                AnimatedBuilder(
                  animation: _scaleAnimation,
                  builder: (context, child) {
                    return Stack(
                      alignment: Alignment.center,
                      children: [
                        // Outer glow
                        Container(
                          width: 180 * _scaleAnimation.value + 40,
                          height: 180 * _scaleAnimation.value + 40,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: currentColor.withOpacity(0.1),
                          ),
                        ),
                        // Inner circle
                        Container(
                          width: 180 * _scaleAnimation.value,
                          height: 180 * _scaleAnimation.value,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: RadialGradient(
                              colors: [
                                currentColor.withOpacity(0.3),
                                currentColor.withOpacity(0.6),
                              ],
                            ),
                            border: Border.all(
                              color: currentColor,
                              width: 3,
                            ),
                          ),
                        ),
                        // Timer countdown
                        Text(
                          _getCountdown(),
                          style: TextStyle(
                            fontSize: 42,
                            fontWeight: FontWeight.w300,
                            color: Colors.white.withOpacity(0.9),
                          ),
                        ),
                      ],
                    );
                  },
                ),
                
                const SizedBox(height: 32),

                // Cycle counter
                if (_cycleCount > 0)
                  Text(
                    'Cycle $_cycleCount',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.5),
                    ),
                  ),

                // Phase indicator dots
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _buildPhaseDot('In', 0),
                    const SizedBox(width: 32),
                    _buildPhaseDot('Hold', 1),
                    const SizedBox(width: 32),
                    _buildPhaseDot('Out', 2),
                  ],
                ),
                
                const Spacer(),
                
                // Intensity reporting
                IntensitySlider(
                  value: _currentIntensity,
                  onChanged: (value) {
                    setState(() => _currentIntensity = value);
                    context.read<PanicBloc>().add(IntensityReported(value));
                  },
                ),
                
                const SizedBox(height: 16),
                
                // Actions
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: _switchToGrounding,
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(color: Colors.white.withOpacity(0.3)),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: const Text(
                          'Try grounding',
                          style: TextStyle(color: Colors.white70),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: _feelBetter,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppTheme.calmColor,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: const Text('I feel better'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: widget.isConnected ? AppTheme.calmColor : Colors.orange,
          ),
        ),
        const SizedBox(width: 8),
        Text(
          widget.isConnected ? 'Connected' : 'Offline',
          style: TextStyle(
            fontSize: 12,
            color: Colors.white.withOpacity(0.5),
          ),
        ),
        const Spacer(),
        IconButton(
          icon: Icon(
            widget.voiceEnabled ? Icons.volume_up : Icons.volume_off,
            color: Colors.white.withOpacity(0.5),
          ),
          onPressed: () {
            context.read<PanicBloc>().add(VoiceToggled(!widget.voiceEnabled));
          },
        ),
      ],
    );
  }

  String _getCountdown() {
    final duration = switch (_phase) {
      0 => _inhaleDuration,
      1 => _holdDuration,
      2 => _exhaleDuration,
      _ => 4,
    };
    final remaining = (duration * (1 - _breathController.value)).ceil();
    return '$remaining';
  }

  Widget _buildPhaseDot(String label, int phaseIndex) {
    final isActive = _phase == phaseIndex;
    final color = isActive ? _phaseColors[phaseIndex] : Colors.grey;
    
    return Column(
      children: [
        AnimatedContainer(
          duration: const Duration(milliseconds: 300),
          width: isActive ? 14 : 10,
          height: isActive ? 14 : 10,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isActive ? color : Colors.transparent,
            border: Border.all(color: color, width: 2),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
            color: color,
          ),
        ),
      ],
    );
  }

  void _switchToGrounding() {
    HapticFeedback.mediumImpact();
    context.read<PanicBloc>().add(const ExerciseTransitionRequested(
      fromExercise: 'breathing',
      toExercise: 'grounding',
    ));
  }

  void _feelBetter() {
    HapticFeedback.heavyImpact();
    _showExitConfirmation();
  }

  void _showExitConfirmation() {
    HapticFeedback.lightImpact();
    showModalBottomSheet(
      context: context,
      backgroundColor: const Color(0xFF1A1A2E),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.white24,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Feeling better?',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              "Take your time. Are you ready to end this session?",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white.withOpacity(0.7)),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: Colors.white24),
                    ),
                    child: const Text('Stay', style: TextStyle(color: Colors.white70)),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      Navigator.pop(context);
                      context.read<PanicBloc>().add(const PanicExitRequested());
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.calmColor,
                    ),
                    child: const Text('End session'),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }
}
