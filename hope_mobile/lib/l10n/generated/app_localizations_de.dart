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
  String get settingsTheme => 'Thema';

  @override
  String get settingsNotifications => 'Benachrichtigungen';

  @override
  String get settingsPrivacy => 'Datenschutz';

  @override
  String get settingsAbout => 'Über';

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

  @override
  String get historyEmptyTitle => 'Noch keine Sitzungen';

  @override
  String get historyEmptySubtitle => 'Ihre Gespräche werden hier erscheinen';

  @override
  String get historyStatsSessions => 'Sitzungen';

  @override
  String get historyStatsTotal => 'Gesamt';

  @override
  String get historyStatsIntensity => 'Intensität';

  @override
  String get historyRecent => 'Letzte Sitzungen';

  @override
  String get historyWeek => 'Diese Woche';

  @override
  String get resourcesTitle => 'Ressourcen';

  @override
  String get resourcesBannerTitle => 'In der Krise? Rufen Sie 3114 an';

  @override
  String get resourcesBannerSubtitle => 'Kostenlos, vertraulich, 24/7';

  @override
  String get resourcesEmergencyNumbers => 'Notrufnummern';

  @override
  String get resourcesSupportLines => 'Hilfslinien';

  @override
  String get resourcesCopingTechniques => 'Bewältigungstechniken';

  @override
  String get resourcesInternationalHelp => 'Internationale Hilfe';

  @override
  String get resourcesMedicalDisclaimer =>
      'Diese App ersetzt keinen professionellen ärztlichen Rat. Im Notfall 112 anrufen.';

  @override
  String get resourceSuicidePrevention => 'Suizidprävention';

  @override
  String get resourceEuropeanEmergency => 'Europäischer Notruf';

  @override
  String get resourceMedicalEmergency => 'Notarzt';

  @override
  String get resourceSOSFriendship => 'SOS Freundschaft';

  @override
  String get resourceYouthHealth => 'Jugendgesundheitstelefon';

  @override
  String get resourceRedCross => 'Rotes Kreuz Zuhören';

  @override
  String get techniqueBreathing => 'Box-Atmung';

  @override
  String get techniqueBreathingDesc => '4-4-4-4 Technik zur Beruhigung';

  @override
  String get techniqueGrounding => '5-4-3-2-1 Erdung';

  @override
  String get techniqueGroundingDesc => 'Nutzen Sie Ihre Sinne zur Erdung';

  @override
  String get techniqueRelaxation => 'Muskelentspannung';

  @override
  String get techniqueRelaxationDesc => 'Anspannungs-Entspannungs-Technik';

  @override
  String get settingsTitle => 'Einstellungen';

  @override
  String get settingsProfile => 'Profil';

  @override
  String get settingsPanicMode => 'Panikmodus';

  @override
  String get settingsAppearance => 'Aussehen';

  @override
  String get settingsDataPrivacy => 'Daten & Datenschutz';

  @override
  String get settingsVoiceGuidance => 'Sprachführung';

  @override
  String get settingsVoiceGuidanceSubtitle =>
      'Gesprochene Anweisungen während der Übungen';

  @override
  String get settingsHaptic => 'Haptisches Feedback';

  @override
  String get settingsHapticSubtitle => 'Vibrationen während der Übungen';

  @override
  String get settingsBreathingSpeed => 'Atemgeschwindigkeit';

  @override
  String get settingsBreathingSpeedSubtitle => 'Übungstempo anpassen';

  @override
  String get settingsDailyCheckIn => 'Tgl. Check-in';

  @override
  String get settingsDailyCheckInSubtitle =>
      'Sanfte Erinnerung, auf sich selbst zu achten';

  @override
  String get settingsExportData => 'Daten exportieren';

  @override
  String get settingsExportDataSubtitle => 'Verlauf herunterladen';

  @override
  String get settingsClearData => 'Verlauf löschen';

  @override
  String get settingsClearDataSubtitle => 'Alle Daten löschen';

  @override
  String get settingsPrivacyPolicy => 'Datenschutzerklärung';

  @override
  String get settingsTerms => 'Nutzungsbedingungen';

  @override
  String get settingsAboutApp => 'Über HOPE';

  @override
  String get settingsFeedback => 'Feedback senden';

  @override
  String get settingsFeedbackSubtitle => 'Helfen Sie uns, HOPE zu verbessern';

  @override
  String get settingsLoginSoon => 'Anmeldung bald verfügbar';

  @override
  String get settingsExportConfirm => 'Daten exportieren';

  @override
  String get settingsClearConfirm => 'Alle Daten löschen?';

  @override
  String get settingsFeedbackSuccess => 'Danke für Ihr Feedback!';

  @override
  String get settingsSpeedSlow => 'Langsam';

  @override
  String get settingsSpeedNormal => 'Normal';

  @override
  String get settingsSpeedFast => 'Schnell';

  @override
  String get settingsThemeSystem => 'System';

  @override
  String get settingsThemeLight => 'Hell';

  @override
  String get settingsThemeDark => 'Dunkel';

  @override
  String get settingsWelcome => 'Willkommen';

  @override
  String get settingsAnonymous => 'Anonymer Benutzer';

  @override
  String get settingsIrreversible => 'Diese Aktion ist UNWIDERRUFLICH.';

  @override
  String get settingsDeleteAction => 'Löschen';

  @override
  String get settingsExportAction => 'Exportieren';

  @override
  String get settingsCancel => 'Abbrechen';

  @override
  String get crisisFlowTitle => 'Du bist nicht allein';

  @override
  String get crisisFlowOr => 'oder';

  @override
  String get crisisFlowExercisePrompt =>
      'Wenn du möchtest, können wir gemeinsam Entspannungsübungen machen.';

  @override
  String get crisisFlowCompanionNeeded =>
      'Ich brauche nur jemanden, der bei mir ist';

  @override
  String get homeSubtitle => 'Dein sicherer Ort';

  @override
  String get homeSupportMessage =>
      'Du bist stärker als du denkst. Wir sind hier, wann immer du uns brauchst.';

  @override
  String get quickActionBreathe => 'Atmen';

  @override
  String get quickActionGrounding => 'Erdung';

  @override
  String get quickActionCrisisNumber => 'Krise';

  @override
  String get crisisSubtitle => 'Professionelle Hilfe ist immer verfügbar';

  @override
  String get crisisSuicidePreventionTitle => 'Suizidprävention';

  @override
  String get crisisSuicidePreventionDescription => '24/7 Krisenhotline';

  @override
  String get crisisEuropeanEmergencyTitle => 'Europäischer Notruf';

  @override
  String get crisisEuropeanEmergencyDescription => 'Notdienste in ganz Europa';

  @override
  String get crisisSOSFriendshipTitle => 'SOS Freundschaft';

  @override
  String get crisisSOSFriendshipDescription =>
      'Zuhör- und Unterstützungsdienst';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE ersetzt keine professionelle Hilfe. Wenn Sie in Gefahr sind, rufen Sie den Notdienst an.';

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
