/// Settings BLoC
/// 
/// State management for settings with reactive updates.
/// Connects SettingsService to UI.

import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

import 'settings_service.dart';
import 'user_data_service.dart';

// Events

abstract class SettingsEvent extends Equatable {
  const SettingsEvent();
  
  @override
  List<Object?> get props => [];
}

class SettingsLoaded extends SettingsEvent {
  const SettingsLoaded();
}

class VoiceGuidanceToggled extends SettingsEvent {
  final bool value;
  const VoiceGuidanceToggled(this.value);
  
  @override
  List<Object?> get props => [value];
}

class HapticFeedbackToggled extends SettingsEvent {
  final bool value;
  const HapticFeedbackToggled(this.value);
  
  @override
  List<Object?> get props => [value];
}

class BreathingSpeedChanged extends SettingsEvent {
  final String value;
  const BreathingSpeedChanged(this.value);
  
  @override
  List<Object?> get props => [value];
}

class DailyCheckInToggled extends SettingsEvent {
  final bool value;
  const DailyCheckInToggled(this.value);
  
  @override
  List<Object?> get props => [value];
}

class ThemePreferenceChanged extends SettingsEvent {
  final ThemePreference value;
  const ThemePreferenceChanged(this.value);
  
  @override
  List<Object?> get props => [value];
}

class DataExportRequested extends SettingsEvent {
  const DataExportRequested();
}

class DataDeletionRequested extends SettingsEvent {
  const DataDeletionRequested();
}

class PrivacyPolicyAccepted extends SettingsEvent {
  final String version;
  const PrivacyPolicyAccepted(this.version);
  
  @override
  List<Object?> get props => [version];
}

class TermsAccepted extends SettingsEvent {
  final String version;
  const TermsAccepted(this.version);
  
  @override
  List<Object?> get props => [version];
}

// States

enum SettingsStatus {
  initial,
  loading,
  loaded,
  saving,
  exporting,
  deleting,
  error,
}

class SettingsState extends Equatable {
  final SettingsStatus status;
  final UserSettings settings;
  final String? errorMessage;
  final String? exportFilePath;
  final bool deletionComplete;
  
  const SettingsState({
    this.status = SettingsStatus.initial,
    required this.settings,
    this.errorMessage,
    this.exportFilePath,
    this.deletionComplete = false,
  });
  
  SettingsState copyWith({
    SettingsStatus? status,
    UserSettings? settings,
    String? errorMessage,
    String? exportFilePath,
    bool? deletionComplete,
  }) {
    return SettingsState(
      status: status ?? this.status,
      settings: settings ?? this.settings,
      errorMessage: errorMessage,
      exportFilePath: exportFilePath,
      deletionComplete: deletionComplete ?? this.deletionComplete,
    );
  }
  
  /// Get ThemeMode from preferences
  ThemeMode get themeMode {
    switch (settings.themePreference) {
      case ThemePreference.light:
        return ThemeMode.light;
      case ThemePreference.dark:
        return ThemeMode.dark;
      case ThemePreference.system:
        return ThemeMode.system;
    }
  }
  
  @override
  List<Object?> get props => [status, settings, errorMessage, exportFilePath, deletionComplete];
}

/// Settings BLoC
/// 
/// Manages all settings state and persistence.
class SettingsBloc extends Bloc<SettingsEvent, SettingsState> {
  final SettingsService _settingsService;
  final UserDataService _userDataService;
  
  SettingsBloc({
    required SettingsService settingsService,
    required UserDataService userDataService,
  }) : _settingsService = settingsService,
       _userDataService = userDataService,
       super(SettingsState(settings: UserSettings.defaults())) {
    
    on<SettingsLoaded>(_onLoaded);
    on<VoiceGuidanceToggled>(_onVoiceGuidanceToggled);
    on<HapticFeedbackToggled>(_onHapticFeedbackToggled);
    on<BreathingSpeedChanged>(_onBreathingSpeedChanged);
    on<DailyCheckInToggled>(_onDailyCheckInToggled);
    on<ThemePreferenceChanged>(_onThemePreferenceChanged);
    on<DataExportRequested>(_onDataExportRequested);
    on<DataDeletionRequested>(_onDataDeletionRequested);
    on<PrivacyPolicyAccepted>(_onPrivacyPolicyAccepted);
    on<TermsAccepted>(_onTermsAccepted);
    
    // Listen for changes from service
    _settingsService.addListener((settings) {
      // Update state when service changes externally
      if (!isClosed) {
        emit(state.copyWith(settings: settings));
      }
    });
  }
  
  Future<void> _onLoaded(
    SettingsLoaded event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.loading));
    
    try {
      await _settingsService.initialize();
      emit(state.copyWith(
        status: SettingsStatus.loaded,
        settings: _settingsService.settings,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: SettingsStatus.error,
        errorMessage: 'Failed to load settings: $e',
      ));
    }
  }
  
  Future<void> _onVoiceGuidanceToggled(
    VoiceGuidanceToggled event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.saving));
    await _settingsService.setVoiceGuidance(event.value);
    emit(state.copyWith(
      status: SettingsStatus.loaded,
      settings: _settingsService.settings,
    ));
  }
  
  Future<void> _onHapticFeedbackToggled(
    HapticFeedbackToggled event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.saving));
    await _settingsService.setHapticFeedback(event.value);
    emit(state.copyWith(
      status: SettingsStatus.loaded,
      settings: _settingsService.settings,
    ));
  }
  
  Future<void> _onBreathingSpeedChanged(
    BreathingSpeedChanged event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.saving));
    await _settingsService.setBreathingSpeed(event.value);
    emit(state.copyWith(
      status: SettingsStatus.loaded,
      settings: _settingsService.settings,
    ));
  }
  
  Future<void> _onDailyCheckInToggled(
    DailyCheckInToggled event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.saving));
    await _settingsService.setDailyCheckIn(event.value);
    emit(state.copyWith(
      status: SettingsStatus.loaded,
      settings: _settingsService.settings,
    ));
  }
  
  Future<void> _onThemePreferenceChanged(
    ThemePreferenceChanged event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.saving));
    await _settingsService.setThemePreference(event.value);
    emit(state.copyWith(
      status: SettingsStatus.loaded,
      settings: _settingsService.settings,
    ));
  }
  
  Future<void> _onDataExportRequested(
    DataExportRequested event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.exporting));
    
    final result = await _userDataService.exportData();
    
    if (result.success) {
      emit(state.copyWith(
        status: SettingsStatus.loaded,
        exportFilePath: result.filePath,
      ));
    } else {
      emit(state.copyWith(
        status: SettingsStatus.error,
        errorMessage: result.error,
      ));
    }
  }
  
  Future<void> _onDataDeletionRequested(
    DataDeletionRequested event,
    Emitter<SettingsState> emit,
  ) async {
    emit(state.copyWith(status: SettingsStatus.deleting));
    
    final result = await _userDataService.deleteAllData();
    
    if (result.success) {
      emit(state.copyWith(
        status: SettingsStatus.loaded,
        settings: UserSettings.defaults(),
        deletionComplete: true,
      ));
    } else {
      emit(state.copyWith(
        status: SettingsStatus.error,
        errorMessage: result.error,
      ));
    }
  }
  
  Future<void> _onPrivacyPolicyAccepted(
    PrivacyPolicyAccepted event,
    Emitter<SettingsState> emit,
  ) async {
    await _settingsService.recordConsentAcceptance(event.version);
    emit(state.copyWith(settings: _settingsService.settings));
  }
  
  Future<void> _onTermsAccepted(
    TermsAccepted event,
    Emitter<SettingsState> emit,
  ) async {
    await _settingsService.recordTermsAcceptance(event.version);
    emit(state.copyWith(settings: _settingsService.settings));
  }
}
