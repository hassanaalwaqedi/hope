import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_de.dart';
import 'app_localizations_en.dart';
import 'app_localizations_es.dart';
import 'app_localizations_fr.dart';
import 'app_localizations_it.dart';
import 'app_localizations_ko.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'generated/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('de'),
    Locale('en'),
    Locale('es'),
    Locale('fr'),
    Locale('it'),
    Locale('ko')
  ];

  /// Application title
  ///
  /// In en, this message translates to:
  /// **'HOPE'**
  String get appTitle;

  /// Home navigation label
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get navHome;

  /// Chat navigation label
  ///
  /// In en, this message translates to:
  /// **'Chat'**
  String get navChat;

  /// History navigation label
  ///
  /// In en, this message translates to:
  /// **'History'**
  String get navHistory;

  /// Resources navigation label
  ///
  /// In en, this message translates to:
  /// **'Resources'**
  String get navResources;

  /// Settings navigation label
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get navSettings;

  /// Main panic button text
  ///
  /// In en, this message translates to:
  /// **'I need help now'**
  String get panicButtonText;

  /// Instructions below panic button
  ///
  /// In en, this message translates to:
  /// **'Tap if you\'re having a panic attack'**
  String get panicButtonSubtext;

  /// Title for breathing exercise screen
  ///
  /// In en, this message translates to:
  /// **'Breathing Exercise'**
  String get breathingTitle;

  /// Breathing instruction - inhale
  ///
  /// In en, this message translates to:
  /// **'Breathe in'**
  String get breatheIn;

  /// Breathing instruction - hold
  ///
  /// In en, this message translates to:
  /// **'Hold'**
  String get holdBreath;

  /// Breathing instruction - exhale
  ///
  /// In en, this message translates to:
  /// **'Breathe out'**
  String get breatheOut;

  /// Title for grounding exercise
  ///
  /// In en, this message translates to:
  /// **'Grounding Exercise'**
  String get groundingTitle;

  /// 5-4-3-2-1 grounding intro
  ///
  /// In en, this message translates to:
  /// **'Look around and find:'**
  String get groundingInstructions;

  /// See instruction
  ///
  /// In en, this message translates to:
  /// **'{count} things you can see'**
  String groundingSee(int count);

  /// Touch instruction
  ///
  /// In en, this message translates to:
  /// **'{count} things you can touch'**
  String groundingTouch(int count);

  /// Hear instruction
  ///
  /// In en, this message translates to:
  /// **'{count} things you can hear'**
  String groundingHear(int count);

  /// Smell instruction
  ///
  /// In en, this message translates to:
  /// **'{count} things you can smell'**
  String groundingSmell(int count);

  /// Taste instruction
  ///
  /// In en, this message translates to:
  /// **'{count} thing you can taste'**
  String groundingTaste(int count);

  /// Initial chat welcome message
  ///
  /// In en, this message translates to:
  /// **'I\'m here with you. How are you feeling right now?'**
  String get chatWelcome;

  /// Chat input placeholder
  ///
  /// In en, this message translates to:
  /// **'Type how you\'re feeling...'**
  String get chatInputHint;

  /// Send message button
  ///
  /// In en, this message translates to:
  /// **'Send'**
  String get chatSendButton;

  /// Crisis resources screen title
  ///
  /// In en, this message translates to:
  /// **'Crisis Support'**
  String get crisisTitle;

  /// Emergency number display
  ///
  /// In en, this message translates to:
  /// **'Emergency: {number}'**
  String crisisEmergency(String number);

  /// Crisis hotline label
  ///
  /// In en, this message translates to:
  /// **'Crisis Hotline'**
  String get crisisHotline;

  /// 24/7 availability indicator
  ///
  /// In en, this message translates to:
  /// **'Available 24/7'**
  String get crisisAvailable247;

  /// Call button text
  ///
  /// In en, this message translates to:
  /// **'Call Now'**
  String get crisisCall;

  /// Notice that no human support is available
  ///
  /// In en, this message translates to:
  /// **'HOPE provides AI-powered support only. For human assistance, please contact the crisis resources above.'**
  String get humanSupportNotice;

  /// AI-only disclaimer
  ///
  /// In en, this message translates to:
  /// **'This is an AI assistant, not a human counselor'**
  String get aiOnlyDisclaimer;

  /// Language setting label
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get settingsLanguage;

  /// Theme setting label
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get settingsTheme;

  /// Notifications setting label
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get settingsNotifications;

  /// Privacy setting label
  ///
  /// In en, this message translates to:
  /// **'Privacy & Data'**
  String get settingsPrivacy;

  /// About section label
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get settingsAbout;

  /// Consent screen title
  ///
  /// In en, this message translates to:
  /// **'Welcome to HOPE'**
  String get consentTitle;

  /// Terms checkbox label
  ///
  /// In en, this message translates to:
  /// **'I accept the Terms of Service'**
  String get consentTerms;

  /// Privacy checkbox label
  ///
  /// In en, this message translates to:
  /// **'I accept the Privacy Policy'**
  String get consentPrivacy;

  /// Age confirmation checkbox
  ///
  /// In en, this message translates to:
  /// **'I confirm I am 13 years or older'**
  String get consentAge;

  /// Continue button
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get consentContinue;

  /// Generic error message
  ///
  /// In en, this message translates to:
  /// **'Something went wrong. Please try again.'**
  String get errorGeneric;

  /// Network error message
  ///
  /// In en, this message translates to:
  /// **'Unable to connect. Please check your internet connection.'**
  String get errorNetwork;

  /// Loading indicator text
  ///
  /// In en, this message translates to:
  /// **'Loading...'**
  String get loading;

  /// Retry button text
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// Cancel button text
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// OK button text
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// Done button text
  ///
  /// In en, this message translates to:
  /// **'Done'**
  String get done;

  /// No description provided for @historyEmptyTitle.
  ///
  /// In en, this message translates to:
  /// **'No history yet'**
  String get historyEmptyTitle;

  /// No description provided for @historyEmptySubtitle.
  ///
  /// In en, this message translates to:
  /// **'Your conversations will appear here'**
  String get historyEmptySubtitle;

  /// No description provided for @historyStatsSessions.
  ///
  /// In en, this message translates to:
  /// **'Sessions'**
  String get historyStatsSessions;

  /// No description provided for @historyStatsTotal.
  ///
  /// In en, this message translates to:
  /// **'Total'**
  String get historyStatsTotal;

  /// No description provided for @historyStatsIntensity.
  ///
  /// In en, this message translates to:
  /// **'Intensity'**
  String get historyStatsIntensity;

  /// No description provided for @historyRecent.
  ///
  /// In en, this message translates to:
  /// **'Recent Sessions'**
  String get historyRecent;

  /// No description provided for @historyWeek.
  ///
  /// In en, this message translates to:
  /// **'This Week'**
  String get historyWeek;

  /// No description provided for @resourcesTitle.
  ///
  /// In en, this message translates to:
  /// **'Resources'**
  String get resourcesTitle;

  /// No description provided for @resourcesBannerTitle.
  ///
  /// In en, this message translates to:
  /// **'In Crisis? Call 3114'**
  String get resourcesBannerTitle;

  /// No description provided for @resourcesBannerSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Free, confidential, 24/7'**
  String get resourcesBannerSubtitle;

  /// No description provided for @resourcesEmergencyNumbers.
  ///
  /// In en, this message translates to:
  /// **'Emergency Numbers'**
  String get resourcesEmergencyNumbers;

  /// No description provided for @resourcesSupportLines.
  ///
  /// In en, this message translates to:
  /// **'Support Lines'**
  String get resourcesSupportLines;

  /// No description provided for @resourcesCopingTechniques.
  ///
  /// In en, this message translates to:
  /// **'Coping Techniques'**
  String get resourcesCopingTechniques;

  /// No description provided for @resourcesInternationalHelp.
  ///
  /// In en, this message translates to:
  /// **'International Help'**
  String get resourcesInternationalHelp;

  /// No description provided for @resourcesMedicalDisclaimer.
  ///
  /// In en, this message translates to:
  /// **'This app does not replace professional medical advice. In case of emergency, call 112.'**
  String get resourcesMedicalDisclaimer;

  /// No description provided for @resourceSuicidePrevention.
  ///
  /// In en, this message translates to:
  /// **'Suicide Prevention'**
  String get resourceSuicidePrevention;

  /// No description provided for @resourceEuropeanEmergency.
  ///
  /// In en, this message translates to:
  /// **'European Emergency'**
  String get resourceEuropeanEmergency;

  /// No description provided for @resourceMedicalEmergency.
  ///
  /// In en, this message translates to:
  /// **'Emergency Medical Services'**
  String get resourceMedicalEmergency;

  /// No description provided for @resourceSOSFriendship.
  ///
  /// In en, this message translates to:
  /// **'SOS Friendship'**
  String get resourceSOSFriendship;

  /// No description provided for @resourceYouthHealth.
  ///
  /// In en, this message translates to:
  /// **'Youth Health Line'**
  String get resourceYouthHealth;

  /// No description provided for @resourceRedCross.
  ///
  /// In en, this message translates to:
  /// **'Red Cross Listening'**
  String get resourceRedCross;

  /// No description provided for @techniqueBreathing.
  ///
  /// In en, this message translates to:
  /// **'Box Breathing'**
  String get techniqueBreathing;

  /// No description provided for @techniqueBreathingDesc.
  ///
  /// In en, this message translates to:
  /// **'4-4-4-4 technique for calm'**
  String get techniqueBreathingDesc;

  /// No description provided for @techniqueGrounding.
  ///
  /// In en, this message translates to:
  /// **'5-4-3-2-1 Grounding'**
  String get techniqueGrounding;

  /// No description provided for @techniqueGroundingDesc.
  ///
  /// In en, this message translates to:
  /// **'Use your senses to ground yourself'**
  String get techniqueGroundingDesc;

  /// No description provided for @techniqueRelaxation.
  ///
  /// In en, this message translates to:
  /// **'Muscle Relaxation'**
  String get techniqueRelaxation;

  /// No description provided for @techniqueRelaxationDesc.
  ///
  /// In en, this message translates to:
  /// **'Tension-release technique'**
  String get techniqueRelaxationDesc;

  /// No description provided for @settingsTitle.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settingsTitle;

  /// No description provided for @settingsProfile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get settingsProfile;

  /// No description provided for @settingsPanicMode.
  ///
  /// In en, this message translates to:
  /// **'Panic Mode'**
  String get settingsPanicMode;

  /// No description provided for @settingsAppearance.
  ///
  /// In en, this message translates to:
  /// **'Appearance'**
  String get settingsAppearance;

  /// No description provided for @settingsDataPrivacy.
  ///
  /// In en, this message translates to:
  /// **'Data & Privacy'**
  String get settingsDataPrivacy;

  /// No description provided for @settingsVoiceGuidance.
  ///
  /// In en, this message translates to:
  /// **'Voice Guidance'**
  String get settingsVoiceGuidance;

  /// No description provided for @settingsVoiceGuidanceSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Spoken instructions during exercises'**
  String get settingsVoiceGuidanceSubtitle;

  /// No description provided for @settingsHaptic.
  ///
  /// In en, this message translates to:
  /// **'Haptic Feedback'**
  String get settingsHaptic;

  /// No description provided for @settingsHapticSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Vibrations during exercises'**
  String get settingsHapticSubtitle;

  /// No description provided for @settingsBreathingSpeed.
  ///
  /// In en, this message translates to:
  /// **'Breathing Speed'**
  String get settingsBreathingSpeed;

  /// No description provided for @settingsBreathingSpeedSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Adjust exercise pace'**
  String get settingsBreathingSpeedSubtitle;

  /// No description provided for @settingsDailyCheckIn.
  ///
  /// In en, this message translates to:
  /// **'Daily Check-in'**
  String get settingsDailyCheckIn;

  /// No description provided for @settingsDailyCheckInSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Gentle reminder to take care of yourself'**
  String get settingsDailyCheckInSubtitle;

  /// No description provided for @settingsExportData.
  ///
  /// In en, this message translates to:
  /// **'Export Data'**
  String get settingsExportData;

  /// No description provided for @settingsExportDataSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Download your history'**
  String get settingsExportDataSubtitle;

  /// No description provided for @settingsClearData.
  ///
  /// In en, this message translates to:
  /// **'Clear History'**
  String get settingsClearData;

  /// No description provided for @settingsClearDataSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Delete all data'**
  String get settingsClearDataSubtitle;

  /// No description provided for @settingsPrivacyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get settingsPrivacyPolicy;

  /// No description provided for @settingsTerms.
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get settingsTerms;

  /// No description provided for @settingsAboutApp.
  ///
  /// In en, this message translates to:
  /// **'About HOPE'**
  String get settingsAboutApp;

  /// No description provided for @settingsFeedback.
  ///
  /// In en, this message translates to:
  /// **'Send Feedback'**
  String get settingsFeedback;

  /// No description provided for @settingsFeedbackSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Help us improve HOPE'**
  String get settingsFeedbackSubtitle;

  /// No description provided for @settingsLoginSoon.
  ///
  /// In en, this message translates to:
  /// **'Login coming soon'**
  String get settingsLoginSoon;

  /// No description provided for @settingsExportConfirm.
  ///
  /// In en, this message translates to:
  /// **'Export your Data'**
  String get settingsExportConfirm;

  /// No description provided for @settingsClearConfirm.
  ///
  /// In en, this message translates to:
  /// **'Delete All Data?'**
  String get settingsClearConfirm;

  /// No description provided for @settingsFeedbackSuccess.
  ///
  /// In en, this message translates to:
  /// **'Thanks for your feedback!'**
  String get settingsFeedbackSuccess;

  /// No description provided for @settingsSpeedSlow.
  ///
  /// In en, this message translates to:
  /// **'Slow'**
  String get settingsSpeedSlow;

  /// No description provided for @settingsSpeedNormal.
  ///
  /// In en, this message translates to:
  /// **'Normal'**
  String get settingsSpeedNormal;

  /// No description provided for @settingsSpeedFast.
  ///
  /// In en, this message translates to:
  /// **'Fast'**
  String get settingsSpeedFast;

  /// No description provided for @settingsThemeSystem.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get settingsThemeSystem;

  /// No description provided for @settingsThemeLight.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get settingsThemeLight;

  /// No description provided for @settingsThemeDark.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get settingsThemeDark;

  /// No description provided for @settingsWelcome.
  ///
  /// In en, this message translates to:
  /// **'Welcome'**
  String get settingsWelcome;

  /// No description provided for @settingsAnonymous.
  ///
  /// In en, this message translates to:
  /// **'Anonymous User'**
  String get settingsAnonymous;

  /// No description provided for @settingsIrreversible.
  ///
  /// In en, this message translates to:
  /// **'This action is IRREVERSIBLE.'**
  String get settingsIrreversible;

  /// No description provided for @settingsDeleteAction.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get settingsDeleteAction;

  /// No description provided for @settingsExportAction.
  ///
  /// In en, this message translates to:
  /// **'Export'**
  String get settingsExportAction;

  /// No description provided for @settingsCancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get settingsCancel;

  /// No description provided for @crisisFlowTitle.
  ///
  /// In en, this message translates to:
  /// **'You\'re not alone'**
  String get crisisFlowTitle;

  /// No description provided for @crisisFlowOr.
  ///
  /// In en, this message translates to:
  /// **'or'**
  String get crisisFlowOr;

  /// No description provided for @crisisFlowExercisePrompt.
  ///
  /// In en, this message translates to:
  /// **'If you prefer, we can try calming exercises together.'**
  String get crisisFlowExercisePrompt;

  /// No description provided for @crisisFlowCompanionNeeded.
  ///
  /// In en, this message translates to:
  /// **'I just need someone to be with me'**
  String get crisisFlowCompanionNeeded;

  /// No description provided for @homeSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Your safe space'**
  String get homeSubtitle;

  /// No description provided for @homeSupportMessage.
  ///
  /// In en, this message translates to:
  /// **'You are stronger than you think. We\'re here whenever you need us.'**
  String get homeSupportMessage;

  /// No description provided for @quickActionBreathe.
  ///
  /// In en, this message translates to:
  /// **'Breathe'**
  String get quickActionBreathe;

  /// No description provided for @quickActionGrounding.
  ///
  /// In en, this message translates to:
  /// **'Ground'**
  String get quickActionGrounding;

  /// No description provided for @quickActionCrisisNumber.
  ///
  /// In en, this message translates to:
  /// **'Crisis'**
  String get quickActionCrisisNumber;

  /// No description provided for @crisisSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Professional help is always available'**
  String get crisisSubtitle;

  /// No description provided for @crisisSuicidePreventionTitle.
  ///
  /// In en, this message translates to:
  /// **'Suicide Prevention'**
  String get crisisSuicidePreventionTitle;

  /// No description provided for @crisisSuicidePreventionDescription.
  ///
  /// In en, this message translates to:
  /// **'24/7 crisis support line'**
  String get crisisSuicidePreventionDescription;

  /// No description provided for @crisisEuropeanEmergencyTitle.
  ///
  /// In en, this message translates to:
  /// **'European Emergency'**
  String get crisisEuropeanEmergencyTitle;

  /// No description provided for @crisisEuropeanEmergencyDescription.
  ///
  /// In en, this message translates to:
  /// **'Emergency services across Europe'**
  String get crisisEuropeanEmergencyDescription;

  /// No description provided for @crisisSOSFriendshipTitle.
  ///
  /// In en, this message translates to:
  /// **'SOS Friendship'**
  String get crisisSOSFriendshipTitle;

  /// No description provided for @crisisSOSFriendshipDescription.
  ///
  /// In en, this message translates to:
  /// **'Listening and support service'**
  String get crisisSOSFriendshipDescription;

  /// No description provided for @crisisEmergencyDisclaimer.
  ///
  /// In en, this message translates to:
  /// **'HOPE is not a substitute for professional help. If you are in danger, call emergency services.'**
  String get crisisEmergencyDisclaimer;

  /// No description provided for @chatNoInternet.
  ///
  /// In en, this message translates to:
  /// **'No internet connection'**
  String get chatNoInternet;

  /// No description provided for @chatOfflineMode.
  ///
  /// In en, this message translates to:
  /// **'Offline mode: limited responses'**
  String get chatOfflineMode;

  /// No description provided for @chatReconnected.
  ///
  /// In en, this message translates to:
  /// **'✓ Connected - full AI responses available'**
  String get chatReconnected;

  /// No description provided for @chatWelcomeOnline.
  ///
  /// In en, this message translates to:
  /// **'Hello, I\'m here to listen. How are you feeling today?'**
  String get chatWelcomeOnline;

  /// No description provided for @chatWelcomeOffline.
  ///
  /// In en, this message translates to:
  /// **'Hello, I\'m here to listen. (Offline mode)'**
  String get chatWelcomeOffline;

  /// No description provided for @chatStreamError.
  ///
  /// In en, this message translates to:
  /// **'Sorry, an error occurred. Please try again.'**
  String get chatStreamError;

  /// No description provided for @chatCamera.
  ///
  /// In en, this message translates to:
  /// **'Camera'**
  String get chatCamera;

  /// No description provided for @chatGallery.
  ///
  /// In en, this message translates to:
  /// **'Gallery'**
  String get chatGallery;

  /// No description provided for @chatImageReady.
  ///
  /// In en, this message translates to:
  /// **'Image ready'**
  String get chatImageReady;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) => <String>[
        'ar',
        'de',
        'en',
        'es',
        'fr',
        'it',
        'ko'
      ].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'de':
      return AppLocalizationsDe();
    case 'en':
      return AppLocalizationsEn();
    case 'es':
      return AppLocalizationsEs();
    case 'fr':
      return AppLocalizationsFr();
    case 'it':
      return AppLocalizationsIt();
    case 'ko':
      return AppLocalizationsKo();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
