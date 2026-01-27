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
    Locale('fr')
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
  /// **'About HOPE'**
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
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'de', 'en', 'es', 'fr'].contains(locale.languageCode);

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
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
