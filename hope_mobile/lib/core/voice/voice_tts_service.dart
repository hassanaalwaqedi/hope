/// Voice Text-to-Speech Service
/// 
/// Production-ready TTS using flutter_tts.
/// Optimized for panic scenarios with calm, slow speech.
/// Supports 10+ languages with automatic voice selection.
/// 
/// NO MOCKS - Real speech synthesis only.

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';

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

/// Voice TTS Service
/// 
/// Uses platform-native TTS with panic-optimized settings.
/// Features:
/// - Natural, calm voice selection
/// - Adjustable speed (slower during panic)
/// - Breathing-synced pauses
/// - Automatic language matching
class VoiceTtsService {
  final FlutterTts _tts = FlutterTts();
  
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
    if (_isInitialized) return true;
    
    try {
      // Get available voices and languages
      _availableVoices = await _tts.getVoices;
      _availableLanguages = await _tts.getLanguages;
      
      // Configure TTS engine
      await _tts.setSharedInstance(true);
      await _tts.awaitSpeakCompletion(true);
      
      // Set up handlers
      _tts.setStartHandler(() {
        _setState(VoiceSpeakingState.speaking);
      });
      
      _tts.setCompletionHandler(() {
        _setState(VoiceSpeakingState.idle);
        onSpeechComplete?.call();
        _processQueue();
      });
      
      _tts.setErrorHandler((message) {
        _handleError(message.toString());
      });
      
      _tts.setCancelHandler(() {
        _setState(VoiceSpeakingState.idle);
      });
      
      _tts.setPauseHandler(() {
        _setState(VoiceSpeakingState.paused);
      });
      
      _tts.setContinueHandler(() {
        _setState(VoiceSpeakingState.speaking);
      });
      
      // Apply default settings
      await _applyModeSettings(_mode);
      
      _isInitialized = true;
      debugPrint('VoiceTtsService: Initialized with ${_availableLanguages?.length ?? 0} languages');
      
      return true;
    } catch (e) {
      _handleError('Failed to initialize TTS: $e');
      return false;
    }
  }
  
  /// Set the voice mode (affects speed and pauses)
  Future<void> setMode(VoiceMode mode) async {
    _mode = mode;
    await _applyModeSettings(mode);
  }
  
  /// Set the language for speech
  Future<bool> setLanguage(String languageCode) async {
    if (!_isInitialized) {
      await initialize();
    }
    
    // Map language codes to TTS locale format
    final ttsLanguage = _mapToTtsLanguage(languageCode);
    
    try {
      final result = await _tts.setLanguage(ttsLanguage);
      if (result == 1) {
        _currentLanguage = ttsLanguage;
        await _selectBestVoice(ttsLanguage);
        return true;
      }
      return false;
    } catch (e) {
      debugPrint('VoiceTtsService: Language $ttsLanguage not available');
      return false;
    }
  }
  
  /// Speak text with current settings
  /// 
  /// [text] - Text to speak
  /// [immediate] - If true, interrupts current speech
  Future<bool> speak(String text, {bool immediate = false}) async {
    if (!_isInitialized) {
      final initialized = await initialize();
      if (!initialized) {
        // Fallback: Return false, caller should show text
        return false;
      }
    }
    
    if (immediate) {
      await stop();
      return await _speakNow(text);
    } else {
      _speechQueue.add(text);
      _processQueue();
      return true;
    }
  }
  
  /// Speak with panic-safe formatting
  /// 
  /// Adds pauses between sentences and speaks slowly.
  Future<bool> speakForPanic(String text) async {
    // Set panic mode
    await setMode(VoiceMode.panic);
    
    // Split into sentences and speak with pauses
    final sentences = _splitIntoSentences(text);
    for (final sentence in sentences) {
      if (sentence.trim().isNotEmpty) {
        _speechQueue.add(sentence.trim());
      }
    }
    
    _processQueue();
    return true;
  }
  
  /// Speak breathing instructions with sync pauses
  /// 
  /// [instruction] - Breathing instruction (e.g., "Breathe in")
  /// [durationSeconds] - How long the phase lasts
  Future<void> speakBreathingInstruction(
    String instruction,
    int durationSeconds,
  ) async {
    await setMode(VoiceMode.breathing);
    await speak(instruction, immediate: true);
    
    // Wait for speech to complete
    await Future.delayed(Duration(milliseconds: 1500));
    
    // Speak countdown if duration > 3 seconds
    if (durationSeconds > 3) {
      for (int i = durationSeconds; i > 0; i--) {
        if (_state == VoiceSpeakingState.idle) break;
        await Future.delayed(const Duration(seconds: 1));
      }
    }
  }
  
  /// Speak grounding exercise prompts
  Future<void> speakGroundingPrompt(String prompt, {int pauseMs = 2000}) async {
    await setMode(VoiceMode.panic);
    await speak(prompt, immediate: true);
    
    // Wait for user to process
    await Future.delayed(Duration(milliseconds: pauseMs));
  }
  
  /// Speak crisis hotline information
  Future<void> speakCrisisInfo(String hotlineName, String number) async {
    await setMode(VoiceMode.panic);
    
    // Speak number slowly, digit by digit
    final formattedNumber = number.split('').join(' ... ');
    final message = '$hotlineName ... $formattedNumber';
    
    await speak(message, immediate: true);
  }
  
  /// Stop speaking
  Future<void> stop() async {
    _speechQueue.clear();
    await _tts.stop();
    _setState(VoiceSpeakingState.idle);
  }
  
  /// Pause speaking
  Future<void> pause() async {
    await _tts.pause();
  }
  
  /// Check if a language is supported
  bool isLanguageSupported(String languageCode) {
    final ttsLang = _mapToTtsLanguage(languageCode);
    return _availableLanguages?.any(
      (l) => l.toString().toLowerCase().startsWith(languageCode.toLowerCase()),
    ) ?? false;
  }
  
  /// Get list of supported language codes
  List<String> getSupportedLanguages() {
    final supported = <String>[];
    final codes = ['en', 'fr', 'ar', 'es', 'de', 'tr', 'ja', 'ko', 'it', 'sv', 'pt', 'zh', 'ru', 'hi'];
    
    for (final code in codes) {
      if (isLanguageSupported(code)) {
        supported.add(code);
      }
    }
    
    return supported;
  }
  
  // Private methods
  
  Future<bool> _speakNow(String text) async {
    try {
      final result = await _tts.speak(text);
      return result == 1;
    } catch (e) {
      _handleError('Speech failed: $e');
      return false;
    }
  }
  
  void _processQueue() async {
    if (_isProcessingQueue || _speechQueue.isEmpty) return;
    if (_state == VoiceSpeakingState.speaking) return;
    
    _isProcessingQueue = true;
    
    while (_speechQueue.isNotEmpty) {
      final text = _speechQueue.removeAt(0);
      await _speakNow(text);
      
      // Wait for completion
      while (_state == VoiceSpeakingState.speaking) {
        await Future.delayed(const Duration(milliseconds: 100));
      }
      
      // Add pause between sentences in panic mode
      if (_mode == VoiceMode.panic || _mode == VoiceMode.breathing) {
        await Future.delayed(const Duration(milliseconds: 500));
      }
    }
    
    _isProcessingQueue = false;
  }
  
  Future<void> _applyModeSettings(VoiceMode mode) async {
    switch (mode) {
      case VoiceMode.normal:
        await _tts.setSpeechRate(0.5);
        await _tts.setPitch(1.0);
        await _tts.setVolume(1.0);
        break;
        
      case VoiceMode.panic:
        // Slower, calmer speech for panic
        await _tts.setSpeechRate(0.35);
        await _tts.setPitch(0.95);
        await _tts.setVolume(1.0);
        break;
        
      case VoiceMode.breathing:
        // Very slow for breathing exercises
        await _tts.setSpeechRate(0.3);
        await _tts.setPitch(0.9);
        await _tts.setVolume(1.0);
        break;
    }
  }
  
  String _mapToTtsLanguage(String languageCode) {
    // Map ISO codes to TTS language codes
    final mapping = {
      'en': 'en-US',
      'fr': 'fr-FR',
      'ar': 'ar-SA',
      'es': 'es-ES',
      'de': 'de-DE',
      'tr': 'tr-TR',
      'ja': 'ja-JP',
      'ko': 'ko-KR',
      'it': 'it-IT',
      'sv': 'sv-SE',
      'pt': 'pt-BR',
      'zh': 'zh-CN',
      'ru': 'ru-RU',
      'hi': 'hi-IN',
    };
    
    return mapping[languageCode] ?? languageCode;
  }
  
  Future<void> _selectBestVoice(String language) async {
    if (_availableVoices == null) return;
    
    // Try to find a female voice (typically calmer) for the language
    try {
      final voices = _availableVoices!.where((v) {
        final map = v as Map;
        final locale = map['locale']?.toString() ?? '';
        final name = map['name']?.toString().toLowerCase() ?? '';
        return locale.startsWith(language.split('-').first) &&
               (name.contains('female') || name.contains('samantha') || name.contains('amelie'));
      }).toList();
      
      if (voices.isNotEmpty) {
        final voice = voices.first as Map;
        await _tts.setVoice({'name': voice['name'], 'locale': voice['locale']});
      }
    } catch (e) {
      // Use default voice
      debugPrint('VoiceTtsService: Using default voice');
    }
  }
  
  List<String> _splitIntoSentences(String text) {
    // Split on sentence-ending punctuation
    return text
        .replaceAll(RegExp(r'([.!?])\s*'), r'$1\n')
        .split('\n')
        .where((s) => s.trim().isNotEmpty)
        .toList();
  }
  
  void _setState(VoiceSpeakingState newState) {
    if (_state != newState) {
      _state = newState;
      onStateChange?.call(newState);
    }
  }
  
  void _handleError(String message) {
    debugPrint('VoiceTtsService ERROR: $message');
    _setState(VoiceSpeakingState.error);
    onError?.call(message);
    
    // Reset to idle after error
    Future.delayed(const Duration(seconds: 1), () {
      if (_state == VoiceSpeakingState.error) {
        _setState(VoiceSpeakingState.idle);
      }
    });
  }
  
  /// Dispose resources
  void dispose() {
    _tts.stop();
    _speechQueue.clear();
  }
}
