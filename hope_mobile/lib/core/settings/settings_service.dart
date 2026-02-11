/// Settings Service
/// 
/// Production-grade settings persistence using SharedPreferences.
/// Syncs with backend for authenticated users.
/// All settings are REAL, PERSISTED, and APPLIED.

import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';

/// All user settings stored locally and synced to backend
class UserSettings {
  // Panic Mode
  final bool voiceGuidance;
  final bool hapticFeedback;
  final String breathingSpeed; // 'slow', 'normal', 'fast'
  
  // Notifications
  final bool dailyCheckIn;
  
  // Appearance
  final ThemePreference themePreference;
  
  // Privacy
  final bool analyticsEnabled;
  final String? consentVersion;
  final DateTime? consentDate;
  final String? termsVersion;
  final DateTime? termsAcceptedDate;
  
  // Metadata
  final DateTime lastUpdated;
  
  const UserSettings({
    this.voiceGuidance = false,
    this.hapticFeedback = true,
    this.breathingSpeed = 'normal',
    this.dailyCheckIn = true,
    this.themePreference = ThemePreference.system,
    this.analyticsEnabled = true,
    this.consentVersion,
    this.consentDate,
    this.termsVersion,
    this.termsAcceptedDate,
    required this.lastUpdated,
  });
  
  UserSettings copyWith({
    bool? voiceGuidance,
    bool? hapticFeedback,
    String? breathingSpeed,
    bool? dailyCheckIn,
    ThemePreference? themePreference,
    bool? analyticsEnabled,
    String? consentVersion,
    DateTime? consentDate,
    String? termsVersion,
    DateTime? termsAcceptedDate,
    DateTime? lastUpdated,
  }) {
    return UserSettings(
      voiceGuidance: voiceGuidance ?? this.voiceGuidance,
      hapticFeedback: hapticFeedback ?? this.hapticFeedback,
      breathingSpeed: breathingSpeed ?? this.breathingSpeed,
      dailyCheckIn: dailyCheckIn ?? this.dailyCheckIn,
      themePreference: themePreference ?? this.themePreference,
      analyticsEnabled: analyticsEnabled ?? this.analyticsEnabled,
      consentVersion: consentVersion ?? this.consentVersion,
      consentDate: consentDate ?? this.consentDate,
      termsVersion: termsVersion ?? this.termsVersion,
      termsAcceptedDate: termsAcceptedDate ?? this.termsAcceptedDate,
      lastUpdated: lastUpdated ?? DateTime.now(),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'voice_guidance': voiceGuidance,
    'haptic_feedback': hapticFeedback,
    'breathing_speed': breathingSpeed,
    'daily_check_in': dailyCheckIn,
    'theme_preference': themePreference.name,
    'analytics_enabled': analyticsEnabled,
    'consent_version': consentVersion,
    'consent_date': consentDate?.toIso8601String(),
    'terms_version': termsVersion,
    'terms_accepted_date': termsAcceptedDate?.toIso8601String(),
    'last_updated': lastUpdated.toIso8601String(),
  };
  
  factory UserSettings.fromJson(Map<String, dynamic> json) {
    return UserSettings(
      voiceGuidance: json['voice_guidance'] ?? false,
      hapticFeedback: json['haptic_feedback'] ?? true,
      breathingSpeed: json['breathing_speed'] ?? 'normal',
      dailyCheckIn: json['daily_check_in'] ?? true,
      themePreference: ThemePreference.values.firstWhere(
        (e) => e.name == json['theme_preference'],
        orElse: () => ThemePreference.system,
      ),
      analyticsEnabled: json['analytics_enabled'] ?? true,
      consentVersion: json['consent_version'],
      consentDate: json['consent_date'] != null 
          ? DateTime.parse(json['consent_date']) 
          : null,
      termsVersion: json['terms_version'],
      termsAcceptedDate: json['terms_accepted_date'] != null
          ? DateTime.parse(json['terms_accepted_date'])
          : null,
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'])
          : DateTime.now(),
    );
  }
  
  static UserSettings defaults() => UserSettings(lastUpdated: DateTime.now());
}

enum ThemePreference {
  system,
  light,
  dark,
}

/// Settings Service - Real persistence with SharedPreferences
/// 
/// All settings are:
/// - Saved immediately on change
/// - Loaded on app start
/// - Synced to backend when authenticated
class SettingsService {
  static const _storageKey = 'hope_user_settings';
  
  // Production Azure backend
  static const _backendUrl = 'https://hope-api-b3bxa3htdsd3guhc.swedencentral-01.azurewebsites.net';
  
  // For local development, uncomment this:
  // static const _backendUrl = 'http://10.0.2.2:8000';
  
  SharedPreferences? _prefs;
  UserSettings _settings = UserSettings.defaults();
  String? _authToken;
  
  final List<Function(UserSettings)> _listeners = [];
  
  /// Current settings (read-only)
  UserSettings get settings => _settings;
  
  /// Initialize the service
  Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
    await _loadFromLocal();
    debugPrint('SettingsService: Initialized with settings: ${_settings.toJson()}');
  }
  
  /// Set auth token for backend sync
  void setAuthToken(String? token) {
    _authToken = token;
    if (token != null) {
      _syncFromBackend();
    }
  }
  
  /// Add listener for settings changes
  void addListener(Function(UserSettings) listener) {
    _listeners.add(listener);
  }
  
  /// Remove listener
  void removeListener(Function(UserSettings) listener) {
    _listeners.remove(listener);
  }
  
  // Individual setting updates with persistence
  
  Future<void> setVoiceGuidance(bool value) async {
    _settings = _settings.copyWith(voiceGuidance: value);
    await _save();
  }
  
  Future<void> setHapticFeedback(bool value) async {
    _settings = _settings.copyWith(hapticFeedback: value);
    await _save();
  }
  
  Future<void> setBreathingSpeed(String value) async {
    _settings = _settings.copyWith(breathingSpeed: value);
    await _save();
  }
  
  Future<void> setDailyCheckIn(bool value) async {
    _settings = _settings.copyWith(dailyCheckIn: value);
    await _save();
  }
  
  Future<void> setThemePreference(ThemePreference value) async {
    _settings = _settings.copyWith(themePreference: value);
    await _save();
  }
  
  Future<void> setAnalyticsEnabled(bool value) async {
    _settings = _settings.copyWith(analyticsEnabled: value);
    await _save();
  }
  
  Future<void> recordConsentAcceptance(String version) async {
    _settings = _settings.copyWith(
      consentVersion: version,
      consentDate: DateTime.now(),
    );
    await _save();
  }
  
  Future<void> recordTermsAcceptance(String version) async {
    _settings = _settings.copyWith(
      termsVersion: version,
      termsAcceptedDate: DateTime.now(),
    );
    await _save();
  }
  
  /// Check if user has accepted current terms
  bool hasAcceptedTerms(String currentVersion) {
    return _settings.termsVersion == currentVersion;
  }
  
  /// Check if user has accepted current privacy policy
  bool hasAcceptedPrivacyPolicy(String currentVersion) {
    return _settings.consentVersion == currentVersion;
  }
  
  // Private methods
  
  Future<void> _loadFromLocal() async {
    final json = _prefs?.getString(_storageKey);
    if (json != null) {
      try {
        _settings = UserSettings.fromJson(jsonDecode(json));
      } catch (e) {
        debugPrint('SettingsService: Failed to load settings: $e');
        _settings = UserSettings.defaults();
      }
    }
  }
  
  Future<void> _save() async {
    // Save locally
    await _prefs?.setString(_storageKey, jsonEncode(_settings.toJson()));
    
    // Notify listeners
    for (final listener in _listeners) {
      listener(_settings);
    }
    
    // Sync to backend if authenticated
    if (_authToken != null) {
      await _syncToBackend();
    }
    
    debugPrint('SettingsService: Saved settings');
  }
  
  Future<void> _syncToBackend() async {
    if (_authToken == null) return;
    
    try {
      final dio = Dio(BaseOptions(
        baseUrl: _backendUrl,
        headers: {'Authorization': 'Bearer $_authToken'},
      ));
      
      await dio.put('/api/v1/user/preferences', data: _settings.toJson());
      debugPrint('SettingsService: Synced to backend');
    } catch (e) {
      debugPrint('SettingsService: Backend sync failed: $e');
      // Silent fail - local settings are still saved
    }
  }
  
  Future<void> _syncFromBackend() async {
    if (_authToken == null) return;
    
    try {
      final dio = Dio(BaseOptions(
        baseUrl: _backendUrl,
        headers: {'Authorization': 'Bearer $_authToken'},
      ));
      
      final response = await dio.get('/api/v1/user/preferences');
      if (response.statusCode == 200 && response.data != null) {
        final backendSettings = UserSettings.fromJson(response.data);
        
        // Use most recent settings
        if (backendSettings.lastUpdated.isAfter(_settings.lastUpdated)) {
          _settings = backendSettings;
          await _prefs?.setString(_storageKey, jsonEncode(_settings.toJson()));
          
          for (final listener in _listeners) {
            listener(_settings);
          }
        }
      }
    } catch (e) {
      debugPrint('SettingsService: Backend fetch failed: $e');
    }
  }
  
  /// Clear all settings (for logout or data deletion)
  Future<void> clearAll() async {
    await _prefs?.remove(_storageKey);
    _settings = UserSettings.defaults();
    
    for (final listener in _listeners) {
      listener(_settings);
    }
  }
}
