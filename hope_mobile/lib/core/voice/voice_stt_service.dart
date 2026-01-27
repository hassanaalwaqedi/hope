/// Voice Speech-to-Text Service
/// 
/// Production-ready STT using platform-native speech recognition.
/// Supports 10+ languages with auto-detection.
/// Designed for panic scenarios - continuous listening mode.
/// 
/// NO MOCKS - Real speech recognition only.

import 'package:flutter/foundation.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_recognition_error.dart';

import 'voice_permission_service.dart';
import 'audio_session_service.dart';
import 'non_verbal_panic_detector.dart';
import 'panic_score_calculator.dart';

/// Supported languages for speech recognition
class VoiceLanguage {
  final String code;
  final String name;
  final String locale;
  
  const VoiceLanguage({
    required this.code,
    required this.name,
    required this.locale,
  });
  
  static const List<VoiceLanguage> supported = [
    VoiceLanguage(code: 'en', name: 'English', locale: 'en_US'),
    VoiceLanguage(code: 'fr', name: 'French', locale: 'fr_FR'),
    VoiceLanguage(code: 'ar', name: 'Arabic', locale: 'ar_SA'),
    VoiceLanguage(code: 'es', name: 'Spanish', locale: 'es_ES'),
    VoiceLanguage(code: 'de', name: 'German', locale: 'de_DE'),
    VoiceLanguage(code: 'tr', name: 'Turkish', locale: 'tr_TR'),
    VoiceLanguage(code: 'ja', name: 'Japanese', locale: 'ja_JP'),
    VoiceLanguage(code: 'ko', name: 'Korean', locale: 'ko_KR'),
    VoiceLanguage(code: 'it', name: 'Italian', locale: 'it_IT'),
    VoiceLanguage(code: 'sv', name: 'Swedish', locale: 'sv_SE'),
    VoiceLanguage(code: 'pt', name: 'Portuguese', locale: 'pt_BR'),
    VoiceLanguage(code: 'zh', name: 'Chinese', locale: 'zh_CN'),
    VoiceLanguage(code: 'ru', name: 'Russian', locale: 'ru_RU'),
    VoiceLanguage(code: 'hi', name: 'Hindi', locale: 'hi_IN'),
  ];
  
  static VoiceLanguage? findByCode(String code) {
    try {
      return supported.firstWhere((l) => l.code == code);
    } catch (_) {
      return null;
    }
  }
}

/// STT recognition result with metadata
class VoiceRecognitionResult {
  final String transcript;
  final String detectedLanguage;
  final double confidence;
  final bool isFinal;
  final DateTime timestamp;
  
  VoiceRecognitionResult({
    required this.transcript,
    required this.detectedLanguage,
    required this.confidence,
    required this.isFinal,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
  
  Map<String, dynamic> toJson() => {
    'transcript': transcript,
    'detected_language': detectedLanguage,
    'confidence': confidence,
    'is_final': isFinal,
    'timestamp': timestamp.toIso8601String(),
  };
}

/// STT listening state
enum VoiceListeningState {
  idle,
  initializing,
  listening,
  processing,
  error,
}

/// Voice Speech-to-Text Service
/// 
/// Uses platform-native speech recognition (Android/iOS).
/// Supports continuous listening for panic mode.
class VoiceSttService {
  final SpeechToText _speech = SpeechToText();
  
  VoiceListeningState _state = VoiceListeningState.idle;
  String _currentLocale = 'en_US';
  bool _isInitialized = false;
  List<LocaleName> _availableLocales = [];
  
  // Non-verbal panic detection
  final NonVerbalPanicDetector _panicDetector = NonVerbalPanicDetector();
  bool _nonVerbalDetectionEnabled = false;
  
  // Callbacks
  Function(VoiceRecognitionResult)? onResult;
  Function(VoiceListeningState)? onStateChange;
  Function(String)? onError;
  Function(double)? onSoundLevel;
  Function(NonVerbalPanicTrigger)? onNonVerbalPanicDetected;
  
  /// Current listening state
  VoiceListeningState get state => _state;
  
  /// Whether STT is available
  bool get isAvailable => _isInitialized;
  
  /// Whether currently listening
  bool get isListening => _speech.isListening;
  
  /// Available locales on this device
  List<LocaleName> get availableLocales => _availableLocales;
  
  /// Initialize the STT service
  /// 
  /// Requests permissions if not already granted.
  /// Returns true if ready to use, false otherwise.
  Future<bool> initialize() async {
    if (_isInitialized) return true;
    
    _setState(VoiceListeningState.initializing);
    
    try {
      // Request microphone permission via VoicePermissionService
      final permissionService = VoicePermissionService();
      final permResult = await permissionService.requestPermissions();
      
      if (!permResult.canUseMicrophone) {
        _handleError('Microphone permission denied: ${permResult.userMessage}');
        // Return false but don't crash - caller can handle gracefully
        return false;
      }
      
      // Initialize audio session for background operation
      final audioSession = AudioSessionService();
      await audioSession.initialize();
      
      // Initialize speech recognition
      _isInitialized = await _speech.initialize(
        onError: _onSpeechError,
        onStatus: _onSpeechStatus,
        debugLogging: kDebugMode,
      );
      
      if (_isInitialized) {
        // Get available locales
        _availableLocales = await _speech.locales();
        debugPrint('VoiceSttService: Initialized with ${_availableLocales.length} locales');
        _setState(VoiceListeningState.idle);
      } else {
        _handleError('Speech recognition not available on this device');
      }
      
      return _isInitialized;
    } catch (e) {
      _handleError('Failed to initialize: $e');
      return false;
    }
  }
  
  /// Start listening for speech
  /// 
  /// [locale] - Language locale (e.g., 'en_US', 'fr_FR')
  /// [continuous] - Keep listening until explicitly stopped (panic mode)
  /// [partialResults] - Receive interim transcripts
  Future<bool> startListening({
    String? locale,
    bool continuous = false,
    bool partialResults = true,
  }) async {
    if (!_isInitialized) {
      final initialized = await initialize();
      if (!initialized) return false;
    }
    
    if (_speech.isListening) {
      await stopListening();
    }
    
    // Find best matching locale
    final targetLocale = locale ?? _currentLocale;
    final matchedLocale = _findBestLocale(targetLocale);
    _currentLocale = matchedLocale;
    
    _setState(VoiceListeningState.listening);
    
    try {
      await _speech.listen(
        onResult: (result) => _onSpeechResult(result, matchedLocale),
        localeId: matchedLocale,
        cancelOnError: !continuous,
        partialResults: partialResults,
        onSoundLevelChange: (level) {
          onSoundLevel?.call(level);
          // Feed to non-verbal panic detector
          if (_nonVerbalDetectionEnabled) {
            _panicDetector.processSample(level);
          }
        },
        listenFor: continuous ? const Duration(minutes: 5) : const Duration(seconds: 30),
        pauseFor: continuous ? const Duration(seconds: 10) : const Duration(seconds: 3),
        listenOptions: SpeechListenOptions(
          cancelOnError: !continuous,
          partialResults: partialResults,
          autoPunctuation: true,
          enableHapticFeedback: true,
        ),
      );
      
      return true;
    } catch (e) {
      _handleError('Failed to start listening: $e');
      return false;
    }
  }
  
  /// Start continuous listening mode for panic support
  /// 
  /// Keeps listening until explicitly stopped.
  /// Auto-restarts on silence.
  /// Enables non-verbal panic detection.
  Future<bool> startPanicListening({String? locale}) async {
    // Enable non-verbal detection for panic mode
    enableNonVerbalDetection();
    
    return startListening(
      locale: locale,
      continuous: true,
      partialResults: true,
    );
  }
  
  /// Stop listening
  Future<void> stopListening() async {
    if (_speech.isListening) {
      await _speech.stop();
    }
    _setState(VoiceListeningState.idle);
  }
  
  /// Cancel current recognition
  Future<void> cancel() async {
    await _speech.cancel();
    _setState(VoiceListeningState.idle);
  }
  
  /// Set preferred language
  void setLanguage(String languageCode) {
    final lang = VoiceLanguage.findByCode(languageCode);
    if (lang != null) {
      _currentLocale = lang.locale;
    }
  }
  
  /// Check if a language is supported on this device
  bool isLanguageSupported(String languageCode) {
    final lang = VoiceLanguage.findByCode(languageCode);
    if (lang == null) return false;
    
    return _availableLocales.any(
      (l) => l.localeId.startsWith(languageCode),
    );
  }
  
  /// Get list of supported languages on this device
  List<VoiceLanguage> getDeviceSupportedLanguages() {
    return VoiceLanguage.supported.where((lang) {
      return _availableLocales.any(
        (l) => l.localeId.startsWith(lang.code),
      );
    }).toList();
  }
  
  // Private methods
  
  String _findBestLocale(String targetLocale) {
    // Try exact match
    if (_availableLocales.any((l) => l.localeId == targetLocale)) {
      return targetLocale;
    }
    
    // Try language code match
    final langCode = targetLocale.split('_').first;
    final match = _availableLocales.firstWhere(
      (l) => l.localeId.startsWith(langCode),
      orElse: () => LocaleName('en_US', 'English'),
    );
    
    return match.localeId;
  }
  
  void _onSpeechResult(SpeechRecognitionResult result, String locale) {
    _setState(VoiceListeningState.processing);
    
    final voiceResult = VoiceRecognitionResult(
      transcript: result.recognizedWords,
      detectedLanguage: locale.split('_').first,
      confidence: result.confidence,
      isFinal: result.finalResult,
    );
    
    onResult?.call(voiceResult);
    
    if (result.finalResult) {
      _setState(VoiceListeningState.idle);
    } else {
      _setState(VoiceListeningState.listening);
    }
  }
  
  void _onSpeechError(SpeechRecognitionError error) {
    _handleError('${error.errorMsg} (${error.permanent ? 'permanent' : 'temporary'})');
  }
  
  void _onSpeechStatus(String status) {
    debugPrint('VoiceSttService: Status = $status');
    
    switch (status) {
      case 'listening':
        _setState(VoiceListeningState.listening);
        break;
      case 'notListening':
        _setState(VoiceListeningState.idle);
        break;
      case 'done':
        _setState(VoiceListeningState.idle);
        break;
    }
  }
  
  void _setState(VoiceListeningState newState) {
    if (_state != newState) {
      _state = newState;
      onStateChange?.call(newState);
    }
  }
  
  void _handleError(String message) {
    debugPrint('VoiceSttService ERROR: $message');
    _setState(VoiceListeningState.error);
    onError?.call(message);
    // Reset to idle after error
    Future.delayed(const Duration(seconds: 2), () {
      if (_state == VoiceListeningState.error) {
        _setState(VoiceListeningState.idle);
      }
    });
  }
  
  // ============================================================================
  // NON-VERBAL PANIC DETECTION
  // ============================================================================
  
  /// Enable non-verbal panic detection
  /// 
  /// When enabled, sound levels are analyzed for:
  /// - Hyperventilation (>25 breaths/min)
  /// - Irregular breathing patterns
  /// - Gasping, crying, stress silence
  /// 
  /// Panic mode auto-activates when distress is detected.
  void enableNonVerbalDetection() {
    _nonVerbalDetectionEnabled = true;
    _panicDetector.start();
    _panicDetector.onPanicTriggered = (trigger) {
      debugPrint('VoiceSttService: Non-verbal panic detected - ${trigger.summary}');
      onNonVerbalPanicDetected?.call(trigger);
    };
    debugPrint('VoiceSttService: Non-verbal detection ENABLED');
  }
  
  /// Disable non-verbal panic detection
  void disableNonVerbalDetection() {
    _nonVerbalDetectionEnabled = false;
    _panicDetector.stop();
    debugPrint('VoiceSttService: Non-verbal detection DISABLED');
  }
  
  /// Check if non-verbal detection is enabled
  bool get isNonVerbalDetectionEnabled => _nonVerbalDetectionEnabled;
  
  /// Get current panic score (0-1)
  double get currentPanicScore => _panicDetector.currentScore;
  
  /// Set context for panic detection (affects sensitivity)
  void setDetectionContext(PanicContext context) {
    _panicDetector.setContext(context);
  }
  
  /// Notify detector that speech was recognized
  /// 
  /// Call this when speech-to-text produces valid text.
  /// Helps prevent false positives from talking.
  void notifySpeechRecognized() {
    _panicDetector.notifySpeechDetected(true);
    // Clear after 2 seconds
    Future.delayed(const Duration(seconds: 2), () {
      _panicDetector.notifySpeechDetected(false);
    });
  }
  
  /// Dispose resources
  void dispose() {
    _speech.cancel();
    _panicDetector.stop();
  }
}
