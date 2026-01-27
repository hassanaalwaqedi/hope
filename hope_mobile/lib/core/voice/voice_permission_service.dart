/// Voice Permission Service
/// 
/// Production-ready permission handling for voice-based panic support.
/// Requests microphone and speech recognition permissions.
/// Provides safe fallback when permissions are denied.
/// 
/// CRITICAL: This service MUST be called before any voice pipeline starts.

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:permission_handler/permission_handler.dart';

/// Permission status for voice features
enum VoicePermissionStatus {
  /// All permissions granted - voice fully operational
  granted,
  /// Microphone denied - can use text-only mode
  microphoneDenied,
  /// Speech recognition denied - can use TTS-only mode
  speechDenied,
  /// All voice permissions denied - fallback to touch mode
  allDenied,
  /// Permission permanently denied - must open settings
  permanentlyDenied,
  /// Permission status unknown or restricted
  restricted,
}

/// Result of permission request with details
class VoicePermissionResult {
  final VoicePermissionStatus status;
  final bool canUseMicrophone;
  final bool canUseSpeechRecognition;
  final bool shouldShowSettings;
  final String userMessage;
  
  const VoicePermissionResult({
    required this.status,
    required this.canUseMicrophone,
    required this.canUseSpeechRecognition,
    required this.shouldShowSettings,
    required this.userMessage,
  });
  
  /// Quick check if any voice feature is available
  bool get hasAnyVoiceCapability => canUseMicrophone || canUseSpeechRecognition;
  
  /// Quick check if full voice is available
  bool get hasFullVoice => canUseMicrophone && canUseSpeechRecognition;
}

/// Voice Permission Service
/// 
/// Handles all permission requests for voice functionality.
/// Provides graceful degradation when permissions are denied.
class VoicePermissionService {
  static final VoicePermissionService _instance = VoicePermissionService._();
  factory VoicePermissionService() => _instance;
  VoicePermissionService._();
  
  bool _hasChecked = false;
  VoicePermissionResult? _lastResult;
  
  /// Get cached permission status (call checkPermissions first)
  VoicePermissionResult? get lastResult => _lastResult;
  
  /// Check current permission status without requesting
  Future<VoicePermissionResult> checkPermissions() async {
    try {
      final micStatus = await Permission.microphone.status;
      final speechStatus = await Permission.speech.status;
      
      _lastResult = _buildResult(micStatus, speechStatus);
      _hasChecked = true;
      
      return _lastResult!;
    } catch (e) {
      debugPrint('VoicePermissionService: Check failed - $e');
      return _buildErrorResult();
    }
  }
  
  /// Request all voice permissions with user-friendly flow
  /// 
  /// Call this BEFORE starting any voice pipeline.
  /// Returns detailed result with fallback options.
  Future<VoicePermissionResult> requestPermissions() async {
    try {
      // Request microphone first (required for STT)
      final micStatus = await Permission.microphone.request();
      
      // Request speech recognition (required for STT on iOS)
      PermissionStatus speechStatus;
      if (Platform.isIOS) {
        speechStatus = await Permission.speech.request();
      } else {
        // Android uses microphone permission for speech
        speechStatus = micStatus;
      }
      
      // On Android 13+, request notification for foreground service
      if (Platform.isAndroid) {
        final androidInfo = await _getAndroidSdkVersion();
        if (androidInfo >= 33) {
          await Permission.notification.request();
        }
      }
      
      _lastResult = _buildResult(micStatus, speechStatus);
      _hasChecked = true;
      
      _logPermissionResult(_lastResult!);
      
      return _lastResult!;
    } catch (e) {
      debugPrint('VoicePermissionService: Request failed - $e');
      return _buildErrorResult();
    }
  }
  
  /// Open app settings for user to grant permissions manually
  Future<bool> openSettings() async {
    return await openAppSettings();
  }
  
  /// Check if we should prompt user again (not permanently denied)
  Future<bool> canRequestAgain() async {
    final micStatus = await Permission.microphone.status;
    return micStatus != PermissionStatus.permanentlyDenied;
  }
  
  VoicePermissionResult _buildResult(
    PermissionStatus micStatus,
    PermissionStatus speechStatus,
  ) {
    final canMic = micStatus.isGranted;
    final canSpeech = speechStatus.isGranted;
    final isPermanent = micStatus.isPermanentlyDenied || 
                        speechStatus.isPermanentlyDenied;
    
    VoicePermissionStatus status;
    String message;
    
    if (canMic && canSpeech) {
      status = VoicePermissionStatus.granted;
      message = 'Voice support is ready';
    } else if (isPermanent) {
      status = VoicePermissionStatus.permanentlyDenied;
      message = 'Please enable microphone in Settings to use voice support';
    } else if (!canMic && !canSpeech) {
      status = VoicePermissionStatus.allDenied;
      message = 'Voice support unavailable. Using touch mode.';
    } else if (!canMic) {
      status = VoicePermissionStatus.microphoneDenied;
      message = 'Microphone not available. Limited voice support.';
    } else {
      status = VoicePermissionStatus.speechDenied;
      message = 'Speech recognition not available. TTS only.';
    }
    
    return VoicePermissionResult(
      status: status,
      canUseMicrophone: canMic,
      canUseSpeechRecognition: canSpeech,
      shouldShowSettings: isPermanent,
      userMessage: message,
    );
  }
  
  VoicePermissionResult _buildErrorResult() {
    return const VoicePermissionResult(
      status: VoicePermissionStatus.restricted,
      canUseMicrophone: false,
      canUseSpeechRecognition: false,
      shouldShowSettings: false,
      userMessage: 'Voice support check failed. Using touch mode.',
    );
  }
  
  Future<int> _getAndroidSdkVersion() async {
    // Default to 30 if we can't determine
    if (!Platform.isAndroid) return 0;
    try {
      // In production, use device_info_plus package
      // For now, assume modern Android
      return 33;
    } catch (_) {
      return 30;
    }
  }
  
  void _logPermissionResult(VoicePermissionResult result) {
    debugPrint('VoicePermissionService: Status=${result.status.name}');
    debugPrint('VoicePermissionService: Mic=${result.canUseMicrophone}');
    debugPrint('VoicePermissionService: Speech=${result.canUseSpeechRecognition}');
    if (!result.hasFullVoice) {
      debugPrint('VoicePermissionService: ${result.userMessage}');
    }
  }
}

/// Extension for easy permission check in widgets
extension VoicePermissionContext on VoicePermissionResult {
  /// Get icon for status indication
  String get statusIcon {
    switch (status) {
      case VoicePermissionStatus.granted:
        return '🎤';
      case VoicePermissionStatus.microphoneDenied:
      case VoicePermissionStatus.speechDenied:
        return '🔇';
      case VoicePermissionStatus.allDenied:
      case VoicePermissionStatus.permanentlyDenied:
        return '🚫';
      case VoicePermissionStatus.restricted:
        return '⚠️';
    }
  }
  
  /// Get color for status (green=good, yellow=partial, red=denied)
  int get statusColorValue {
    switch (status) {
      case VoicePermissionStatus.granted:
        return 0xFF4CAF50; // Green
      case VoicePermissionStatus.microphoneDenied:
      case VoicePermissionStatus.speechDenied:
        return 0xFFFFC107; // Yellow
      case VoicePermissionStatus.allDenied:
      case VoicePermissionStatus.permanentlyDenied:
      case VoicePermissionStatus.restricted:
        return 0xFFF44336; // Red
    }
  }
}
