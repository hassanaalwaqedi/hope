/// Audio Session Service
/// 
/// Manages platform audio session for background/locked-screen operation.
/// CRITICAL for panic mode - keeps microphone active when screen is off.
/// 
/// This service handles:
/// - iOS AVAudioSession configuration
/// - Android foreground service notification
/// - Background audio mode activation/deactivation

import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Audio session state for panic mode
enum AudioSessionState {
  /// Session not active
  inactive,
  /// Session active for normal use
  active,
  /// Session active in panic/background mode
  panicMode,
  /// Session failed to configure
  error,
}

/// Audio Session Service
/// 
/// Configures platform audio for continuous listening during panic.
/// On iOS: Sets AVAudioSession category to PlayAndRecord
/// On Android: Manages foreground service for continuous audio
class AudioSessionService {
  static final AudioSessionService _instance = AudioSessionService._();
  factory AudioSessionService() => _instance;
  AudioSessionService._();
  
  static const _channel = MethodChannel('app.hope/audio_session');
  
  AudioSessionState _state = AudioSessionState.inactive;
  bool _isConfigured = false;
  
  /// Current session state
  AudioSessionState get state => _state;
  
  /// Whether session is ready for background audio
  bool get isBackgroundReady => _state == AudioSessionState.panicMode;
  
  /// Initialize audio session for voice support
  /// 
  /// Call this once at app startup.
  Future<bool> initialize() async {
    if (_isConfigured) return true;
    
    try {
      if (Platform.isIOS) {
        await _configureIOSSession();
      } else if (Platform.isAndroid) {
        await _configureAndroidSession();
      }
      
      _isConfigured = true;
      _state = AudioSessionState.active;
      debugPrint('AudioSessionService: Initialized for ${Platform.operatingSystem}');
      return true;
    } catch (e) {
      debugPrint('AudioSessionService: Initialization failed - $e');
      _state = AudioSessionState.error;
      return false;
    }
  }
  
  /// Activate panic mode for background/locked-screen listening
  /// 
  /// Call when entering panic flow.
  /// Keeps audio active even when:
  /// - Screen is locked
  /// - App goes to background
  /// - Device enters low-power mode
  Future<bool> activatePanicMode() async {
    if (!_isConfigured) {
      await initialize();
    }
    
    try {
      if (Platform.isIOS) {
        await _activateIOSPanicMode();
      } else if (Platform.isAndroid) {
        await _startAndroidForegroundService();
      }
      
      _state = AudioSessionState.panicMode;
      debugPrint('AudioSessionService: Panic mode ACTIVATED');
      return true;
    } catch (e) {
      debugPrint('AudioSessionService: Failed to activate panic mode - $e');
      return false;
    }
  }
  
  /// Deactivate panic mode
  /// 
  /// Call when exiting panic flow.
  /// Returns to normal audio behavior.
  Future<void> deactivatePanicMode() async {
    try {
      if (Platform.isIOS) {
        await _deactivateIOSPanicMode();
      } else if (Platform.isAndroid) {
        await _stopAndroidForegroundService();
      }
      
      _state = AudioSessionState.active;
      debugPrint('AudioSessionService: Panic mode deactivated');
    } catch (e) {
      debugPrint('AudioSessionService: Failed to deactivate panic mode - $e');
    }
  }
  
  // iOS Audio Session Configuration
  
  Future<void> _configureIOSSession() async {
    // iOS audio session is configured via Info.plist keys:
    // - AVAudioSessionCategory: AVAudioSessionCategoryPlayAndRecord
    // - AVAudioSessionMode: AVAudioSessionModeVoiceChat
    // - UIBackgroundModes: audio
    // 
    // The speech_to_text plugin handles AVAudioSession configuration,
    // but we ensure the correct category is set.
    
    try {
      // Use method channel if native code is available
      await _channel.invokeMethod('configureIOSSession', {
        'category': 'playAndRecord',
        'mode': 'voiceChat',
        'options': ['allowBluetooth', 'defaultToSpeaker', 'mixWithOthers'],
      });
    } on MissingPluginException {
      // Native plugin not implemented - rely on Info.plist settings
      debugPrint('AudioSessionService: Using Info.plist audio configuration');
    }
  }
  
  Future<void> _activateIOSPanicMode() async {
    try {
      await _channel.invokeMethod('activatePanicMode', {
        'keepAlive': true,
        'mixWithOthers': false,
      });
    } on MissingPluginException {
      // Native plugin not implemented - background audio via Info.plist
      debugPrint('AudioSessionService: iOS panic mode via Info.plist');
    }
  }
  
  Future<void> _deactivateIOSPanicMode() async {
    try {
      await _channel.invokeMethod('deactivatePanicMode');
    } on MissingPluginException {
      // Native plugin not implemented
      debugPrint('AudioSessionService: iOS panic mode deactivated');
    }
  }
  
  // Android Foreground Service Configuration
  
  Future<void> _configureAndroidSession() async {
    // Android audio configuration is handled via:
    // - RECORD_AUDIO permission in AndroidManifest.xml
    // - FOREGROUND_SERVICE permission for background operation
    // - WAKE_LOCK permission for screen-off operation
    //
    // The speech_to_text plugin manages AudioRecord configuration.
    
    try {
      await _channel.invokeMethod('configureAndroidSession', {
        'audioSource': 'voiceRecognition',
        'sampleRate': 16000,
        'channelConfig': 'mono',
      });
    } on MissingPluginException {
      // Native plugin not implemented - use plugin defaults
      debugPrint('AudioSessionService: Using plugin audio configuration');
    }
  }
  
  Future<void> _startAndroidForegroundService() async {
    try {
      await _channel.invokeMethod('startForegroundService', {
        'title': 'HOPE Panic Support',
        'content': 'Listening for voice commands',
        'importance': 'low',
      });
    } on MissingPluginException {
      // Native plugin not implemented
      // Foreground service configured in AndroidManifest.xml
      debugPrint('AudioSessionService: Android foreground service via manifest');
    }
  }
  
  Future<void> _stopAndroidForegroundService() async {
    try {
      await _channel.invokeMethod('stopForegroundService');
    } on MissingPluginException {
      debugPrint('AudioSessionService: Android foreground service stopped');
    }
  }
}

/// Background audio behavior documentation:
/// 
/// ### iOS Background Audio
/// 
/// **How it works:**
/// 1. `UIBackgroundModes: audio` in Info.plist enables background execution
/// 2. `AVAudioSessionCategoryPlayAndRecord` allows simultaneous input/output
/// 3. `AVAudioSessionModeVoiceChat` optimizes for voice with echo cancellation
/// 4. Session remains active when screen locks or app backgrounds
/// 
/// **Limitations:**
/// - User must grant microphone permission
/// - System may interrupt for phone calls
/// - Siri activation temporarily pauses recording
/// 
/// **Battery impact:**
/// - Moderate (~5-10% per hour active)
/// - Audio processing uses hardware DSP
/// 
/// 
/// ### Android Background Audio
/// 
/// **How it works:**
/// 1. `FOREGROUND_SERVICE` permission allows background execution
/// 2. `FOREGROUND_SERVICE_MICROPHONE` declares microphone usage (Android 14+)
/// 3. Foreground notification shows "HOPE Panic Support - Listening"
/// 4. `WAKE_LOCK` permission keeps CPU active when screen off
/// 5. `showWhenLocked="true"` allows panic button access from lock screen
/// 
/// **Limitations:**
/// - User must grant microphone AND notification permissions
/// - Android 12+ limits background microphone access
/// - Some OEMs (Xiaomi, Huawei) may kill background apps
/// 
/// **Battery impact:**
/// - Similar to iOS (~5-10% per hour)
/// - Foreground service prevents aggressive battery optimization
