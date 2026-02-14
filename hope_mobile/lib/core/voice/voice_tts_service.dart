/// Voice Text-to-Speech Service (MOCK)
/// 
/// Temporary mock to bypass flutter_tts build issues on Windows.
/// 

import 'dart:async';
import 'package:flutter/foundation.dart';
// import 'package:flutter_tts/flutter_tts.dart';

/// TTS speaking state
enum VoiceSpeakingState {
  idle,
  speaking,
  paused,
  error,
}

/// Voice mode for different contexts
enum VoiceMode {
  /// Normal conversational speed
  normal,
  /// Slower, calmer pace for panic situations
  panic,
  /// Very slow with long pauses for breathing exercises
  breathing,
}

/// Voice TTS Service (MOCK)
class VoiceTtsService {
  // final FlutterTts _tts = FlutterTts();
  
  VoiceSpeakingState _state = VoiceSpeakingState.idle;
  VoiceMode _mode = VoiceMode.normal;
  String _currentLanguage = 'en-US';
  bool _isInitialized = false;
  List<dynamic>? _availableVoices;
  List<dynamic>? _availableLanguages;
  
  // Speech queue for sequential speaking
  final List<String> _speechQueue = [];
  bool _isProcessingQueue = false;
  
  // Callbacks
  Function(VoiceSpeakingState)? onStateChange;
  Function(String)? onError;
  Function()? onSpeechComplete;
  
  /// Current speaking state
  VoiceSpeakingState get state => _state;
  
  /// Current voice mode
  VoiceMode get mode => _mode;
  
  /// Whether currently speaking
  bool get isSpeaking => _state == VoiceSpeakingState.speaking;
  
  /// Whether TTS is available
  bool get isAvailable => _isInitialized;
  
  /// Initialize the TTS service
  Future<bool> initialize() async {
    debugPrint('VoiceTtsService (Mock): Initialized');
    _isInitialized = true;
    return true;
  }
  
  /// Set the voice mode (affects speed and pauses)
  Future<void> setMode(VoiceMode mode) async {
    _mode = mode;
  }
  
  /// Set the language for speech
  Future<bool> setLanguage(String languageCode) async {
    debugPrint('VoiceTtsService (Mock): setLanguage $languageCode');
    return true;
  }
  
  /// Speak text with current settings
  Future<bool> speak(String text, {bool immediate = false}) async {
    debugPrint('VoiceTtsService (Mock): speak "$text"');
    return true;
  }
  
  /// Speak with panic-safe formatting
  Future<bool> speakForPanic(String text) async {
    debugPrint('VoiceTtsService (Mock): speakForPanic "$text"');
    return true;
  }
  
  /// Speak breathing instructions with sync pauses
  Future<void> speakBreathingInstruction(
    String instruction,
    int durationSeconds,
  ) async {
    debugPrint('VoiceTtsService (Mock): speakBreathingInstruction "$instruction"');
    await Future.delayed(Duration(seconds: durationSeconds));
  }
  
  /// Speak grounding exercise prompts
  Future<void> speakGroundingPrompt(String prompt, {int pauseMs = 2000}) async {
    debugPrint('VoiceTtsService (Mock): speakGroundingPrompt "$prompt"');
    await Future.delayed(Duration(milliseconds: pauseMs));
  }
  
  /// Speak crisis hotline information
  Future<void> speakCrisisInfo(String hotlineName, String number) async {
    debugPrint('VoiceTtsService (Mock): speakCrisisInfo "$hotlineName"');
  }
  
  /// Stop speaking
  Future<void> stop() async {
    debugPrint('VoiceTtsService (Mock): stop');
    _state = VoiceSpeakingState.idle;
  }
  
  /// Pause speaking
  Future<void> pause() async {
     debugPrint('VoiceTtsService (Mock): pause');
  }
  
  /// Check if a language is supported
  bool isLanguageSupported(String languageCode) {
    return true;
  }
  
  /// Get list of supported language codes
  List<String> getSupportedLanguages() {
    return ['en', 'fr', 'ar', 'es', 'de', 'tr', 'ja', 'ko', 'it', 'sv', 'pt', 'zh', 'ru', 'hi'];
  }
  
  void dispose() {}
}
