/// Hold/Reassurance Screen for Severe Panic
/// 
/// Minimal motion, strong presence UI for severe panic states.
/// Designed to reduce cognitive load and provide grounding presence.
/// 
/// Key design principles:
/// - No animated circles or complex visuals
/// - Large, calm text
/// - Muted colors
/// - Minimal interaction required

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../core/theme/app_theme.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../panic/panic_state.dart';
import '../../panic/ux/panic_analytics.dart';
import '../../panic/ux/panic_state_classifier.dart';

class HoldReassuranceScreen extends StatefulWidget {
  final Map<String, dynamic> config;
  
  const HoldReassuranceScreen({
    super.key,
    this.config = const {},
  });

  @override
  State<HoldReassuranceScreen> createState() => _HoldReassuranceScreenState();
}

class _HoldReassuranceScreenState extends State<HoldReassuranceScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;
  
  int _messageIndex = 0;
  bool _canProceed = false;
  bool _showExerciseOption = false;
  
  final _analytics = PanicAnalytics.instance;
  final _stopwatch = Stopwatch();
  
  static const List<String> _reassuranceMessages = [
    "I'm here with you.",
    "You are safe.",
    "This moment will pass.",
    "You're not alone.",
    "Just stay with me.",
  ];

  @override
  void initState() {
    super.initState();
    _stopwatch.start();
    
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 3000),
      vsync: this,
    );
    
    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _fadeController, curve: Curves.easeIn),
    );
    
    _fadeController.forward();
    
    // Show proceed option after minimum duration
    final minDurationMs = widget.config['minDurationMs'] as int? ?? 30000;
    Future.delayed(Duration(milliseconds: minDurationMs), () {
      if (mounted) {
        setState(() {
          _canProceed = true;
          _showExerciseOption = widget.config['showExerciseOption'] as bool? ?? true;
        });
        HapticFeedback.lightImpact();
      }
    });
    
    // Cycle through messages slowly
    _startMessageCycle();
    
    _analytics.logExerciseStarted(
      exerciseType: 'holdReassurance',
      panicState: PanicUXState.SEVERE_PANIC,
    );
  }

  void _startMessageCycle() {
    Future.delayed(const Duration(seconds: 8), () {
      if (mounted) {
        _fadeController.reverse().then((_) {
          if (mounted) {
            setState(() {
              _messageIndex = (_messageIndex + 1) % _reassuranceMessages.length;
            });
            _fadeController.forward();
            _startMessageCycle();
          }
        });
      }
    });
  }

  @override
  void dispose() {
    _stopwatch.stop();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) _showExitConfirmation(context);
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF1A1A2E), // Deep, calming dark
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 24),
            child: Column(
              children: [
                // Minimal header
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (_canProceed)
                      TextButton(
                        onPressed: () => _showExitConfirmation(context),
                        child: Text(
                          'Exit',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.5),
                          ),
                        ),
                      ),
                  ],
                ),
                
                const Spacer(flex: 2),
                
                // Main reassurance message
                FadeTransition(
                  opacity: _fadeAnimation,
                  child: Text(
                    _reassuranceMessages[_messageIndex],
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: 36,
                      fontWeight: FontWeight.w300,
                      color: Colors.white,
                      letterSpacing: 1.2,
                      height: 1.4,
                    ),
                  ),
                ),
                
                const SizedBox(height: 60),
                
                // Gentle breathing prompt
                AnimatedOpacity(
                  opacity: _canProceed ? 0.7 : 1.0,
                  duration: const Duration(milliseconds: 500),
                  child: Column(
                    children: [
                      Text(
                        'Breathe with me',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.white.withOpacity(0.6),
                        ),
                      ),
                      const SizedBox(height: 16),
                      _buildGentleBreathingIndicator(),
                    ],
                  ),
                ),
                
                const Spacer(flex: 2),
                
                // Action buttons (appear after min duration)
                AnimatedOpacity(
                  opacity: _canProceed ? 1.0 : 0.0,
                  duration: const Duration(milliseconds: 800),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (_showExerciseOption) ...[
                        SizedBox(
                          width: double.infinity,
                          child: OutlinedButton(
                            onPressed: _canProceed ? _goToBreathing : null,
                            style: OutlinedButton.styleFrom(
                              side: BorderSide(color: Colors.white.withOpacity(0.3)),
                              padding: const EdgeInsets.symmetric(vertical: 16),
                            ),
                            child: const Text(
                              'I want to try breathing exercises',
                              style: TextStyle(color: Colors.white70),
                            ),
                          ),
                        ),
                        const SizedBox(height: 12),
                      ],
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _canProceed ? _feelingBetter : null,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppTheme.calmColor.withOpacity(0.8),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: const Text(
                            'I\'m ready to continue',
                            style: TextStyle(fontSize: 16),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGentleBreathingIndicator() {
    return SizedBox(
      width: 60,
      height: 60,
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.8, end: 1.0),
        duration: const Duration(seconds: 4),
        curve: Curves.easeInOut,
        onEnd: () {
          // This creates a continuous gentle pulse
        },
        builder: (context, value, child) {
          return Container(
            width: 60 * value,
            height: 60 * value,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: Colors.white.withOpacity(0.2),
                width: 2,
              ),
            ),
          );
        },
      ),
    );
  }

  void _goToBreathing() {
    HapticFeedback.mediumImpact();
    _analytics.logExerciseTransition(
      fromExercise: 'holdReassurance',
      toExercise: 'breathing',
      durationMs: _stopwatch.elapsedMilliseconds,
      wasAutomatic: false,
    );
    context.read<PanicBloc>().add(const ExerciseTransitionRequested(
      fromExercise: 'hold',
      toExercise: 'breathing',
    ));
  }

  void _feelingBetter() {
    HapticFeedback.mediumImpact();
    _analytics.logExerciseCompleted(
      exerciseType: 'holdReassurance',
      durationMs: _stopwatch.elapsedMilliseconds,
      cycles: _messageIndex + 1,
    );
    context.read<PanicBloc>().add(const PanicExitRequested());
  }

  void _showExitConfirmation(BuildContext context) {
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
              'Take your time',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
            const SizedBox(height: 12),
            Text(
              "There's no rush. Are you ready to leave?",
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
                    child: const Text('Leave'),
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
