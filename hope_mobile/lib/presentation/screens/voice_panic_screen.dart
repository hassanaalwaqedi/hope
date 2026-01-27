/// Voice Panic Screen
/// 
/// Hands-free panic support interface.
/// Large microphone button, waveform indicator, voice status display.
/// Designed for use during panic attacks when typing is not possible.

import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/voice/voice_stt_service.dart';
import '../../../core/voice/voice_tts_service.dart';
import '../../../core/voice/bloc/voice_panic_bloc.dart';
import '../../../core/theme/app_theme.dart';
import '../../../l10n/generated/app_localizations.dart';

class VoicePanicScreen extends StatefulWidget {
  final String languageCode;
  final String countryCode;
  
  const VoicePanicScreen({
    super.key,
    this.languageCode = 'en',
    this.countryCode = 'US',
  });

  @override
  State<VoicePanicScreen> createState() => _VoicePanicScreenState();
}

class _VoicePanicScreenState extends State<VoicePanicScreen>
    with TickerProviderStateMixin {
  
  late final VoicePanicBloc _bloc;
  late final AnimationController _pulseController;
  late final AnimationController _waveController;
  
  @override
  void initState() {
    super.initState();
    
    // Initialize voice services and bloc
    final stt = VoiceSttService();
    final tts = VoiceTtsService();
    _bloc = VoicePanicBloc(sttService: stt, ttsService: tts);
    
    // Animation controllers
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);
    
    _waveController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 100),
    );
    
    // Start voice panic session
    _bloc.add(VoicePanicStarted(
      languageCode: widget.languageCode,
      countryCode: widget.countryCode,
    ));
  }
  
  @override
  void dispose() {
    _bloc.close();
    _pulseController.dispose();
    _waveController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return BlocProvider.value(
      value: _bloc,
      child: BlocBuilder<VoicePanicBloc, VoicePanicState>(
        builder: (context, state) {
          return Scaffold(
            backgroundColor: _getBackgroundColor(state.phase),
            body: SafeArea(
              child: Column(
                children: [
                  // Header with close button
                  _buildHeader(context, state),
                  
                  const Spacer(flex: 1),
                  
                  // Main content area
                  Expanded(
                    flex: 4,
                    child: _buildMainContent(context, state),
                  ),
                  
                  const Spacer(flex: 1),
                  
                  // Microphone button
                  _buildMicrophoneButton(context, state),
                  
                  const SizedBox(height: 24),
                  
                  // Status text
                  _buildStatusText(context, state),
                  
                  const SizedBox(height: 48),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
  
  Widget _buildHeader(BuildContext context, VoicePanicState state) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          // AI-only indicator
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.orange.withOpacity(0.2),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.smart_toy, color: Colors.orange, size: 16),
                const SizedBox(width: 6),
                Text(
                  'AI Assistant',
                  style: TextStyle(
                    color: Colors.orange.shade300,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          
          const Spacer(),
          
          // Close button
          IconButton(
            onPressed: () {
              _bloc.add(const VoicePanicEnded());
              Navigator.of(context).pop();
            },
            icon: Icon(
              Icons.close,
              color: Colors.white.withOpacity(0.7),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildMainContent(BuildContext context, VoicePanicState state) {
    switch (state.phase) {
      case VoicePanicPhase.breathing:
        return _buildBreathingContent(state);
      case VoicePanicPhase.grounding:
        return _buildGroundingContent(state);
      case VoicePanicPhase.crisis:
        return _buildCrisisContent(state);
      default:
        return _buildDefaultContent(state);
    }
  }
  
  Widget _buildDefaultContent(VoicePanicState state) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Sound level visualizer
        if (state.isListening)
          SoundWaveVisualizer(
            soundLevel: state.soundLevel,
            isActive: state.isListening,
          ),
        
        const SizedBox(height: 32),
        
        // Last transcript
        if (state.lastTranscript != null && state.lastTranscript!.isNotEmpty)
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 24),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              state.lastTranscript!,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: Colors.white.withOpacity(0.8),
                fontSize: 18,
                fontStyle: FontStyle.italic,
              ),
            ),
          ),
        
        const SizedBox(height: 24),
        
        // Last response
        if (state.lastResponse != null)
          Container(
            margin: const EdgeInsets.symmetric(horizontal: 24),
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              state.lastResponse!,
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 20,
                height: 1.5,
              ),
            ),
          ),
      ],
    );
  }
  
  Widget _buildBreathingContent(VoicePanicState state) {
    final instructions = ['Breathe in', 'Hold', 'Breathe out'];
    final colors = [Colors.blue, Colors.purple, Colors.teal];
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Breathing circle animation
        AnimatedBuilder(
          animation: _pulseController,
          builder: (context, child) {
            final scale = 1.0 + (_pulseController.value * 0.3);
            return Transform.scale(
              scale: state.breathingPhase == 0 ? scale : 
                     state.breathingPhase == 2 ? 1.3 - (_pulseController.value * 0.3) : 1.15,
              child: Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: colors[state.breathingPhase].withOpacity(0.3),
                  border: Border.all(
                    color: colors[state.breathingPhase],
                    width: 3,
                  ),
                ),
                child: Center(
                  child: Text(
                    instructions[state.breathingPhase],
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 24,
                      fontWeight: FontWeight.w300,
                    ),
                  ),
                ),
              ),
            );
          },
        ),
        
        const SizedBox(height: 32),
        
        // Cycle count
        Text(
          'Cycle ${state.breathingCount + 1}',
          style: TextStyle(
            color: Colors.white.withOpacity(0.6),
            fontSize: 16,
          ),
        ),
      ],
    );
  }
  
  Widget _buildGroundingContent(VoicePanicState state) {
    final senses = ['👁️ See', '✋ Touch', '👂 Hear', '👃 Smell', '👅 Taste'];
    final counts = [5, 4, 3, 2, 1];
    final currentIndex = 5 - state.groundingStep;
    
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // Current sense icon
        Text(
          senses[currentIndex].split(' ').first,
          style: const TextStyle(fontSize: 64),
        ),
        
        const SizedBox(height: 16),
        
        // Instruction
        Text(
          '${counts[currentIndex]} things you can ${senses[currentIndex].split(' ').last.toLowerCase()}',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.w300,
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Progress dots
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(5, (i) => Container(
            margin: const EdgeInsets.symmetric(horizontal: 4),
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: i <= currentIndex 
                  ? Colors.white 
                  : Colors.white.withOpacity(0.3),
            ),
          )),
        ),
      ],
    );
  }
  
  Widget _buildCrisisContent(VoicePanicState state) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(
          Icons.phone_in_talk,
          color: Colors.white,
          size: 64,
        ),
        const SizedBox(height: 24),
        const Text(
          'Crisis Support',
          style: TextStyle(
            color: Colors.white,
            fontSize: 28,
            fontWeight: FontWeight.w300,
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Listening for crisis hotline information...',
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 16,
          ),
        ),
      ],
    );
  }
  
  Widget _buildMicrophoneButton(BuildContext context, VoicePanicState state) {
    final isActive = state.isListening || state.isSpeaking;
    
    return GestureDetector(
      onTap: () {
        HapticFeedback.mediumImpact();
        _bloc.add(const VoiceListeningToggled());
      },
      child: AnimatedBuilder(
        animation: _pulseController,
        builder: (context, child) {
          final pulseScale = state.isListening 
              ? 1.0 + (_pulseController.value * 0.15) 
              : 1.0;
          
          return Transform.scale(
            scale: pulseScale,
            child: Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isActive ? Colors.red : Colors.white.withOpacity(0.2),
                boxShadow: isActive ? [
                  BoxShadow(
                    color: Colors.red.withOpacity(0.4),
                    blurRadius: 30,
                    spreadRadius: 10,
                  ),
                ] : null,
              ),
              child: Icon(
                state.isListening ? Icons.mic : 
                state.isSpeaking ? Icons.volume_up : Icons.mic_off,
                color: Colors.white,
                size: 48,
              ),
            ),
          );
        },
      ),
    );
  }
  
  Widget _buildStatusText(BuildContext context, VoicePanicState state) {
    String statusText;
    switch (state.phase) {
      case VoicePanicPhase.idle:
        statusText = 'Tap microphone to start';
        break;
      case VoicePanicPhase.initializing:
        statusText = 'Initializing voice...';
        break;
      case VoicePanicPhase.listening:
        statusText = 'Listening...';
        break;
      case VoicePanicPhase.processing:
        statusText = 'Processing...';
        break;
      case VoicePanicPhase.speaking:
        statusText = 'Speaking...';
        break;
      case VoicePanicPhase.breathing:
        statusText = 'Breathing exercise';
        break;
      case VoicePanicPhase.grounding:
        statusText = 'Grounding exercise';
        break;
      case VoicePanicPhase.crisis:
        statusText = 'Crisis support';
        break;
      case VoicePanicPhase.error:
        statusText = state.errorMessage ?? 'Error occurred';
        break;
    }
    
    return Text(
      statusText,
      style: TextStyle(
        color: Colors.white.withOpacity(0.7),
        fontSize: 16,
      ),
    );
  }
  
  Color _getBackgroundColor(VoicePanicPhase phase) {
    switch (phase) {
      case VoicePanicPhase.breathing:
        return const Color(0xFF1A237E); // Deep blue
      case VoicePanicPhase.grounding:
        return const Color(0xFF1B5E20); // Deep green
      case VoicePanicPhase.crisis:
        return AppTheme.crisisColor.withOpacity(0.8);
      default:
        return const Color(0xFF1A1A2E); // Dark purple
    }
  }
}

/// Sound wave visualizer widget
class SoundWaveVisualizer extends StatelessWidget {
  final double soundLevel;
  final bool isActive;
  
  const SoundWaveVisualizer({
    super.key,
    required this.soundLevel,
    required this.isActive,
  });

  @override
  Widget build(BuildContext context) {
    // Normalize sound level (typically -2 to 10 dB)
    final normalized = ((soundLevel + 2) / 12).clamp(0.0, 1.0);
    
    return SizedBox(
      height: 60,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(9, (i) {
          // Create wave pattern
          final baseHeight = 20.0;
          final maxAddition = 40.0;
          final waveOffset = (i - 4).abs() / 4; // 0 at center, 1 at edges
          final height = baseHeight + (maxAddition * normalized * (1 - waveOffset * 0.5));
          
          return AnimatedContainer(
            duration: const Duration(milliseconds: 100),
            margin: const EdgeInsets.symmetric(horizontal: 2),
            width: 6,
            height: isActive ? height : baseHeight,
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.7),
              borderRadius: BorderRadius.circular(3),
            ),
          );
        }),
      ),
    );
  }
}
