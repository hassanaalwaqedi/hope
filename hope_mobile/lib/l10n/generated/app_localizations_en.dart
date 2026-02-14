// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => 'Home';

  @override
  String get navChat => 'Chat';

  @override
  String get navHistory => 'History';

  @override
  String get navResources => 'Resources';

  @override
  String get navSettings => 'Settings';

  @override
  String get panicButtonText => 'I need help now';

  @override
  String get panicButtonSubtext => 'Tap if you\'re having a panic attack';

  @override
  String get breathingTitle => 'Breathing Exercise';

  @override
  String get breatheIn => 'Breathe in';

  @override
  String get holdBreath => 'Hold';

  @override
  String get breatheOut => 'Breathe out';

  @override
  String get groundingTitle => 'Grounding Exercise';

  @override
  String get groundingInstructions => 'Look around and find:';

  @override
  String groundingSee(int count) {
    return '$count things you can see';
  }

  @override
  String groundingTouch(int count) {
    return '$count things you can touch';
  }

  @override
  String groundingHear(int count) {
    return '$count things you can hear';
  }

  @override
  String groundingSmell(int count) {
    return '$count things you can smell';
  }

  @override
  String groundingTaste(int count) {
    return '$count thing you can taste';
  }

  @override
  String get chatWelcome =>
      'I\'m here with you. How are you feeling right now?';

  @override
  String get chatInputHint => 'Type how you\'re feeling...';

  @override
  String get chatSendButton => 'Send';

  @override
  String get crisisTitle => 'Crisis Support';

  @override
  String crisisEmergency(String number) {
    return 'Emergency: $number';
  }

  @override
  String get crisisHotline => 'Crisis Hotline';

  @override
  String get crisisAvailable247 => 'Available 24/7';

  @override
  String get crisisCall => 'Call Now';

  @override
  String get humanSupportNotice =>
      'HOPE provides AI-powered support only. For human assistance, please contact the crisis resources above.';

  @override
  String get aiOnlyDisclaimer =>
      'This is an AI assistant, not a human counselor';

  @override
  String get settingsLanguage => 'Language';

  @override
  String get settingsTheme => 'Theme';

  @override
  String get settingsNotifications => 'Notifications';

  @override
  String get settingsPrivacy => 'Privacy & Data';

  @override
  String get settingsAbout => 'About';

  @override
  String get consentTitle => 'Welcome to HOPE';

  @override
  String get consentTerms => 'I accept the Terms of Service';

  @override
  String get consentPrivacy => 'I accept the Privacy Policy';

  @override
  String get consentAge => 'I confirm I am 13 years or older';

  @override
  String get consentContinue => 'Continue';

  @override
  String get errorGeneric => 'Something went wrong. Please try again.';

  @override
  String get errorNetwork =>
      'Unable to connect. Please check your internet connection.';

  @override
  String get loading => 'Loading...';

  @override
  String get retry => 'Retry';

  @override
  String get cancel => 'Cancel';

  @override
  String get ok => 'OK';

  @override
  String get done => 'Done';

  @override
  String get historyEmptyTitle => 'No history yet';

  @override
  String get historyEmptySubtitle => 'Your conversations will appear here';

  @override
  String get historyStatsSessions => 'Sessions';

  @override
  String get historyStatsTotal => 'Total';

  @override
  String get historyStatsIntensity => 'Intensity';

  @override
  String get historyRecent => 'Recent Sessions';

  @override
  String get historyWeek => 'This Week';

  @override
  String get resourcesTitle => 'Resources';

  @override
  String get resourcesBannerTitle => 'In Crisis? Call 3114';

  @override
  String get resourcesBannerSubtitle => 'Free, confidential, 24/7';

  @override
  String get resourcesEmergencyNumbers => 'Emergency Numbers';

  @override
  String get resourcesSupportLines => 'Support Lines';

  @override
  String get resourcesCopingTechniques => 'Coping Techniques';

  @override
  String get resourcesInternationalHelp => 'International Help';

  @override
  String get resourcesMedicalDisclaimer =>
      'This app does not replace professional medical advice. In case of emergency, call 112.';

  @override
  String get resourceSuicidePrevention => 'Suicide Prevention';

  @override
  String get resourceEuropeanEmergency => 'European Emergency';

  @override
  String get resourceMedicalEmergency => 'Emergency Medical Services';

  @override
  String get resourceSOSFriendship => 'SOS Friendship';

  @override
  String get resourceYouthHealth => 'Youth Health Line';

  @override
  String get resourceRedCross => 'Red Cross Listening';

  @override
  String get techniqueBreathing => 'Box Breathing';

  @override
  String get techniqueBreathingDesc => '4-4-4-4 technique for calm';

  @override
  String get techniqueGrounding => '5-4-3-2-1 Grounding';

  @override
  String get techniqueGroundingDesc => 'Use your senses to ground yourself';

  @override
  String get techniqueRelaxation => 'Muscle Relaxation';

  @override
  String get techniqueRelaxationDesc => 'Tension-release technique';

  @override
  String get settingsTitle => 'Settings';

  @override
  String get settingsProfile => 'Profile';

  @override
  String get settingsPanicMode => 'Panic Mode';

  @override
  String get settingsAppearance => 'Appearance';

  @override
  String get settingsDataPrivacy => 'Data & Privacy';

  @override
  String get settingsVoiceGuidance => 'Voice Guidance';

  @override
  String get settingsVoiceGuidanceSubtitle =>
      'Spoken instructions during exercises';

  @override
  String get settingsHaptic => 'Haptic Feedback';

  @override
  String get settingsHapticSubtitle => 'Vibrations during exercises';

  @override
  String get settingsBreathingSpeed => 'Breathing Speed';

  @override
  String get settingsBreathingSpeedSubtitle => 'Adjust exercise pace';

  @override
  String get settingsDailyCheckIn => 'Daily Check-in';

  @override
  String get settingsDailyCheckInSubtitle =>
      'Gentle reminder to take care of yourself';

  @override
  String get settingsExportData => 'Export Data';

  @override
  String get settingsExportDataSubtitle => 'Download your history';

  @override
  String get settingsClearData => 'Clear History';

  @override
  String get settingsClearDataSubtitle => 'Delete all data';

  @override
  String get settingsPrivacyPolicy => 'Privacy Policy';

  @override
  String get settingsTerms => 'Terms of Service';

  @override
  String get settingsAboutApp => 'About HOPE';

  @override
  String get settingsFeedback => 'Send Feedback';

  @override
  String get settingsFeedbackSubtitle => 'Help us improve HOPE';

  @override
  String get settingsLoginSoon => 'Login coming soon';

  @override
  String get settingsExportConfirm => 'Export your Data';

  @override
  String get settingsClearConfirm => 'Delete All Data?';

  @override
  String get settingsFeedbackSuccess => 'Thanks for your feedback!';

  @override
  String get settingsSpeedSlow => 'Slow';

  @override
  String get settingsSpeedNormal => 'Normal';

  @override
  String get settingsSpeedFast => 'Fast';

  @override
  String get settingsThemeSystem => 'System';

  @override
  String get settingsThemeLight => 'Light';

  @override
  String get settingsThemeDark => 'Dark';

  @override
  String get settingsWelcome => 'Welcome';

  @override
  String get settingsAnonymous => 'Anonymous User';

  @override
  String get settingsIrreversible => 'This action is IRREVERSIBLE.';

  @override
  String get settingsDeleteAction => 'Delete';

  @override
  String get settingsExportAction => 'Export';

  @override
  String get settingsCancel => 'Cancel';

  @override
  String get crisisFlowTitle => 'You\'re not alone';

  @override
  String get crisisFlowOr => 'or';

  @override
  String get crisisFlowExercisePrompt =>
      'If you prefer, we can try calming exercises together.';

  @override
  String get crisisFlowCompanionNeeded => 'I just need someone to be with me';

  @override
  String get homeSubtitle => 'Your safe space';

  @override
  String get homeSupportMessage =>
      'You are stronger than you think. We\'re here whenever you need us.';

  @override
  String get quickActionBreathe => 'Breathe';

  @override
  String get quickActionGrounding => 'Ground';

  @override
  String get quickActionCrisisNumber => 'Crisis';

  @override
  String get crisisSubtitle => 'Professional help is always available';

  @override
  String get crisisSuicidePreventionTitle => 'Suicide Prevention';

  @override
  String get crisisSuicidePreventionDescription => '24/7 crisis support line';

  @override
  String get crisisEuropeanEmergencyTitle => 'European Emergency';

  @override
  String get crisisEuropeanEmergencyDescription =>
      'Emergency services across Europe';

  @override
  String get crisisSOSFriendshipTitle => 'SOS Friendship';

  @override
  String get crisisSOSFriendshipDescription => 'Listening and support service';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE is not a substitute for professional help. If you are in danger, call emergency services.';

  @override
  String get chatNoInternet => 'No internet connection';

  @override
  String get chatOfflineMode => 'Offline mode: limited responses';

  @override
  String get chatReconnected => '✓ Connected - full AI responses available';

  @override
  String get chatWelcomeOnline =>
      'Hello, I\'m here to listen. How are you feeling today?';

  @override
  String get chatWelcomeOffline => 'Hello, I\'m here to listen. (Offline mode)';

  @override
  String get chatStreamError => 'Sorry, an error occurred. Please try again.';

  @override
  String get chatCamera => 'Camera';

  @override
  String get chatGallery => 'Gallery';

  @override
  String get chatImageReady => 'Image ready';
}
