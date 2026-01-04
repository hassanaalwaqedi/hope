/// Panic Active Screen - Adaptive intervention routing
/// 
/// Routes to appropriate intervention based on classified panic state.
/// The system decides. User follows. Minimal cognitive load.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../panic/panic_state.dart';
import '../../panic/ux/panic_entry_router.dart';
import '../../core/theme/app_theme.dart';
import '../widgets/adaptive_breathing_exercise.dart';
import '../widgets/adaptive_grounding_exercise.dart';
import 'hold_reassurance_screen.dart';
import 'crisis_flow_screen.dart';

class PanicActiveScreen extends StatelessWidget {
  const PanicActiveScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocConsumer<PanicBloc, PanicSessionState>(
      listener: (context, state) {
        // Handle session end
        if (state.phase == PanicPhase.resolved || state.phase == PanicPhase.idle) {
          Navigator.of(context).popUntil((route) => route.isFirst);
        }
      },
      builder: (context, state) {
        // Route to appropriate screen based on state
        return _buildScreen(context, state);
      },
    );
  }

  Widget _buildScreen(BuildContext context, PanicSessionState state) {
    // Handle transitioning state
    if (state.phase == PanicPhase.entering || 
        state.phase == PanicPhase.routing ||
        state.phase == PanicPhase.transitioning) {
      return _buildTransitionScreen(context, state);
    }
    
    // Route based on active exercise
    final exerciseType = state.activeExercise?.type;
    
    switch (exerciseType) {
      case 'breathing':
        return AdaptiveBreathingExercise(
          config: state.activeExercise?.config ?? {},
          intensity: state.reportedIntensity,
          message: state.currentMessage,
          isConnected: state.isConnected,
          voiceEnabled: state.voiceEnabled,
        );
        
      case 'grounding':
        return AdaptiveGroundingExercise(
          config: state.activeExercise?.config ?? {},
          intensity: state.reportedIntensity,
          message: state.currentMessage,
          isConnected: state.isConnected,
        );
        
      case 'hold':
        return HoldReassuranceScreen(
          config: state.activeExercise?.config ?? {},
        );
        
      case 'crisis':
        return CrisisFlowScreen(
          config: state.activeExercise?.config ?? {},
        );
        
      default:
        // Fallback to breathing - always works offline
        return AdaptiveBreathingExercise(
          config: const {},
          intensity: state.reportedIntensity,
          message: state.currentMessage ?? "Let's breathe together.",
          isConnected: state.isConnected,
          voiceEnabled: state.voiceEnabled,
        );
    }
  }

  Widget _buildTransitionScreen(BuildContext context, PanicSessionState state) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A2E),
      body: SafeArea(
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Gentle loading indicator
              SizedBox(
                width: 60,
                height: 60,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    Colors.white.withOpacity(0.5),
                  ),
                ),
              ),
              const SizedBox(height: 32),
              Text(
                state.currentMessage ?? "I'm here with you...",
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 20,
                  color: Colors.white.withOpacity(0.8),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
