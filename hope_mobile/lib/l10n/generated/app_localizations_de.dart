// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for German (`de`).
class AppLocalizationsDe extends AppLocalizations {
  AppLocalizationsDe([String locale = 'de']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => 'Start';

  @override
  String get navChat => 'Chat';

  @override
  String get navHistory => 'Verlauf';

  @override
  String get navResources => 'Ressourcen';

  @override
  String get navSettings => 'Einstellungen';

  @override
  String get panicButtonText => 'Ich brauche jetzt Hilfe';

  @override
  String get panicButtonSubtext =>
      'Tippen Sie, wenn Sie eine Panikattacke haben';

  @override
  String get breathingTitle => 'Atemübung';

  @override
  String get breatheIn => 'Einatmen';

  @override
  String get holdBreath => 'Halten';

  @override
  String get breatheOut => 'Ausatmen';

  @override
  String get groundingTitle => 'Erdungsübung';

  @override
  String get groundingInstructions => 'Schauen Sie sich um und finden Sie:';

  @override
  String groundingSee(int count) {
    return '$count Dinge, die Sie sehen können';
  }

  @override
  String groundingTouch(int count) {
    return '$count Dinge, die Sie berühren können';
  }

  @override
  String groundingHear(int count) {
    return '$count Dinge, die Sie hören können';
  }

  @override
  String groundingSmell(int count) {
    return '$count Dinge, die Sie riechen können';
  }

  @override
  String groundingTaste(int count) {
    return '$count Ding, das Sie schmecken können';
  }

  @override
  String get chatWelcome => 'Ich bin hier bei dir. Wie fühlst du dich gerade?';

  @override
  String get chatInputHint => 'Beschreiben Sie, wie Sie sich fühlen...';

  @override
  String get chatSendButton => 'Senden';

  @override
  String get crisisTitle => 'Krisenunterstützung';

  @override
  String crisisEmergency(String number) {
    return 'Notruf: $number';
  }

  @override
  String get crisisHotline => 'Krisenhotline';

  @override
  String get crisisAvailable247 => 'Rund um die Uhr erreichbar';

  @override
  String get crisisCall => 'Jetzt anrufen';

  @override
  String get humanSupportNotice =>
      'HOPE bietet nur KI-gestützte Unterstützung. Für menschliche Hilfe wenden Sie sich bitte an die oben genannten Krisenressourcen.';

  @override
  String get aiOnlyDisclaimer =>
      'Dies ist ein KI-Assistent, kein menschlicher Berater';

  @override
  String get settingsLanguage => 'Sprache';

  @override
  String get settingsTheme => 'Design';

  @override
  String get settingsNotifications => 'Benachrichtigungen';

  @override
  String get settingsPrivacy => 'Datenschutz';

  @override
  String get settingsAbout => 'Über HOPE';

  @override
  String get consentTitle => 'Willkommen bei HOPE';

  @override
  String get consentTerms => 'Ich akzeptiere die Nutzungsbedingungen';

  @override
  String get consentPrivacy => 'Ich akzeptiere die Datenschutzrichtlinie';

  @override
  String get consentAge => 'Ich bestätige, dass ich 13 Jahre oder älter bin';

  @override
  String get consentContinue => 'Weiter';

  @override
  String get errorGeneric =>
      'Etwas ist schief gelaufen. Bitte versuchen Sie es erneut.';

  @override
  String get errorNetwork =>
      'Verbindung nicht möglich. Bitte überprüfen Sie Ihre Internetverbindung.';

  @override
  String get loading => 'Wird geladen...';

  @override
  String get retry => 'Erneut versuchen';

  @override
  String get cancel => 'Abbrechen';

  @override
  String get ok => 'OK';

  @override
  String get done => 'Fertig';
}
