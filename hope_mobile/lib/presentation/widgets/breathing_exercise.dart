/// Enhanced Breathing Exercise with better visuals
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/theme/app_theme.dart';

class BreathingExercise extends StatefulWidget {
  const BreathingExercise({super.key});

  @override
  State<BreathingExercise> createState() => _BreathingExerciseState();
}

class _BreathingExerciseState extends State<BreathingExercise>
    with TickerProviderStateMixin {
  late AnimationController _breathController;
  late Animation<double> _scaleAnimation;
  int _phase = 0; // 0: inhale, 1: hold, 2: exhale
  int _cycleCount = 0;

  static const _inhaleSeconds = 4;
  static const _holdSeconds = 4;
  static const _exhaleSeconds = 6;

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
    _startBreathingCycle();
  }

  void _startBreathingCycle() {
    _phase = 0;
    _breathController = AnimationController(
      duration: Duration(seconds: _inhaleSeconds),
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
      if (_phase == 0) _cycleCount++;
    });

    final duration = switch (_phase) {
      0 => _inhaleSeconds,
      1 => _holdSeconds,
      2 => _exhaleSeconds,
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
    _breathController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currentColor = _phaseColors[_phase];
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Cycle counter
        if (_cycleCount > 0)
          Text(
            'Cycle $_cycleCount',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: currentColor,
            ),
          ),
        
        const SizedBox(height: 16),

        // Instruction
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: Text(
            _phaseLabels[_phase],
            key: ValueKey(_phase),
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              color: currentColor,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        
        const SizedBox(height: 40),

        // Animated breathing circle
        AnimatedBuilder(
          animation: _scaleAnimation,
          builder: (context, child) {
            return Stack(
              alignment: Alignment.center,
              children: [
                // Outer glow
                Container(
                  width: 200 * _scaleAnimation.value + 40,
                  height: 200 * _scaleAnimation.value + 40,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: currentColor.withOpacity(0.1),
                  ),
                ),
                // Inner circle
                Container(
                  width: 200 * _scaleAnimation.value,
                  height: 200 * _scaleAnimation.value,
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
                    boxShadow: [
                      BoxShadow(
                        color: currentColor.withOpacity(0.3),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                ),
                // Timer countdown
                Text(
                  _getCountdown(),
                  style: TextStyle(
                    fontSize: 48,
                    fontWeight: FontWeight.w300,
                    color: Colors.white.withOpacity(0.9),
                  ),
                ),
              ],
            );
          },
        ),
        
        const SizedBox(height: 40),

        // Phase indicator dots
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
      ],
    );
  }

  String _getCountdown() {
    final duration = switch (_phase) {
      0 => _inhaleSeconds,
      1 => _holdSeconds,
      2 => _exhaleSeconds,
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
          width: isActive ? 16 : 12,
          height: isActive ? 16 : 12,
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
            fontSize: 12,
            fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
            color: color,
          ),
        ),
      ],
    );
  }
}
