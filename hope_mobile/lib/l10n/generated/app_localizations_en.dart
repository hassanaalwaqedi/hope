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
  String get settingsAbout => 'About HOPE';

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
}
