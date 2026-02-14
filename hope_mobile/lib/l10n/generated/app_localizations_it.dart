// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Italian (`it`).
class AppLocalizationsIt extends AppLocalizations {
  AppLocalizationsIt([String locale = 'it']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => 'Home';

  @override
  String get navChat => 'Chat';

  @override
  String get navHistory => 'Cronologia';

  @override
  String get navResources => 'Risorse';

  @override
  String get navSettings => 'Impostazioni';

  @override
  String get panicButtonText => 'Ho bisogno di aiuto ora';

  @override
  String get panicButtonSubtext => 'Tocca se stai avendo un attacco di panico';

  @override
  String get breathingTitle => 'Esercizio di Respirazione';

  @override
  String get breatheIn => 'Inspira';

  @override
  String get holdBreath => 'Trattieni';

  @override
  String get breatheOut => 'Espira';

  @override
  String get groundingTitle => 'Esercizio di Ancoraggio';

  @override
  String get groundingInstructions => 'Guardati intorno e trova:';

  @override
  String groundingSee(int count) {
    return '$count cose che puoi vedere';
  }

  @override
  String groundingTouch(int count) {
    return '$count cose che puoi toccare';
  }

  @override
  String groundingHear(int count) {
    return '$count cose che puoi sentire';
  }

  @override
  String groundingSmell(int count) {
    return '$count cose che puoi annusare';
  }

  @override
  String groundingTaste(int count) {
    return '$count cosa che puoi gustare';
  }

  @override
  String get chatWelcome => 'Sono qui con te. Come ti senti adesso?';

  @override
  String get chatInputHint => 'Scrivi come ti senti...';

  @override
  String get chatSendButton => 'Invia';

  @override
  String get crisisTitle => 'Supporto Crisi';

  @override
  String crisisEmergency(String number) {
    return 'Emergenza: $number';
  }

  @override
  String get crisisHotline => 'Linea di Crisi';

  @override
  String get crisisAvailable247 => 'Disponibile 24/7';

  @override
  String get crisisCall => 'Chiama Ora';

  @override
  String get humanSupportNotice =>
      'HOPE fornisce solo supporto guidato dall\'IA. Per assistenza umana, contatta le risorse di crisi sopra indicate.';

  @override
  String get aiOnlyDisclaimer =>
      'Questo è un assistente IA, non un consulente umano';

  @override
  String get settingsLanguage => 'Lingua';

  @override
  String get settingsTheme => 'Tema';

  @override
  String get settingsNotifications => 'Notifiche';

  @override
  String get settingsPrivacy => 'Privacy e Dati';

  @override
  String get settingsAbout => 'Info';

  @override
  String get consentTitle => 'Benvenuto in HOPE';

  @override
  String get consentTerms => 'Accetto i Termini di Servizio';

  @override
  String get consentPrivacy => 'Accetto l\'Informativa sulla Privacy';

  @override
  String get consentAge => 'Confermo di avere 13 anni o più';

  @override
  String get consentContinue => 'Continua';

  @override
  String get errorGeneric => 'Qualcosa è andato storto. Riprova.';

  @override
  String get errorNetwork =>
      'Impossibile connettersi. Controlla la tua connessione internet.';

  @override
  String get loading => 'Caricamento...';

  @override
  String get retry => 'Riprova';

  @override
  String get cancel => 'Annulla';

  @override
  String get ok => 'OK';

  @override
  String get done => 'Fatto';

  @override
  String get historyEmptyTitle => 'Nessuna cronologia ancora';

  @override
  String get historyEmptySubtitle => 'Le tue conversazioni appariranno qui';

  @override
  String get historyStatsSessions => 'Sessioni';

  @override
  String get historyStatsTotal => 'Totale';

  @override
  String get historyStatsIntensity => 'Intensità';

  @override
  String get historyRecent => 'Sessioni Recenti';

  @override
  String get historyWeek => 'Questa Settimana';

  @override
  String get resourcesTitle => 'Risorse';

  @override
  String get resourcesBannerTitle => 'In Crisi? Chiama 3114';

  @override
  String get resourcesBannerSubtitle => 'Gratuito, confidenziale, 24/7';

  @override
  String get resourcesEmergencyNumbers => 'Numeri di Emergenza';

  @override
  String get resourcesSupportLines => 'Linee di Supporto';

  @override
  String get resourcesCopingTechniques => 'Tecniche di Coping';

  @override
  String get resourcesInternationalHelp => 'Aiuto Internazionale';

  @override
  String get resourcesMedicalDisclaimer =>
      'Questa app non sostituisce il parere medico professionale. In caso di emergenza, chiama il 112.';

  @override
  String get resourceSuicidePrevention => 'Prevenzione Suicidio';

  @override
  String get resourceEuropeanEmergency => 'Emergenza Europea';

  @override
  String get resourceMedicalEmergency => 'Servizi Medici di Emergenza';

  @override
  String get resourceSOSFriendship => 'SOS Amicizia';

  @override
  String get resourceYouthHealth => 'Linea Salute Giovani';

  @override
  String get resourceRedCross => 'Ascolto Croce Rossa';

  @override
  String get techniqueBreathing => 'Respirazione Quadrata';

  @override
  String get techniqueBreathingDesc => 'Tecnica 4-4-4-4 per la calma';

  @override
  String get techniqueGrounding => 'Ancoraggio 5-4-3-2-1';

  @override
  String get techniqueGroundingDesc => 'Usa i tuoi sensi per ancorarti';

  @override
  String get techniqueRelaxation => 'Rilassamento Muscolare';

  @override
  String get techniqueRelaxationDesc => 'Tecnica tensione-rilascio';

  @override
  String get settingsTitle => 'Impostazioni';

  @override
  String get settingsProfile => 'Profilo';

  @override
  String get settingsPanicMode => 'Modalità Panico';

  @override
  String get settingsAppearance => 'Aspetto';

  @override
  String get settingsDataPrivacy => 'Dati & Privacy';

  @override
  String get settingsVoiceGuidance => 'Guida Vocale';

  @override
  String get settingsVoiceGuidanceSubtitle =>
      'Istruzioni vocali durante gli esercizi';

  @override
  String get settingsHaptic => 'Feedback Tattile';

  @override
  String get settingsHapticSubtitle => 'Vibrazioni durante gli esercizi';

  @override
  String get settingsBreathingSpeed => 'Velocità Respirazione';

  @override
  String get settingsBreathingSpeedSubtitle => 'Regola il ritmo degli esercizi';

  @override
  String get settingsDailyCheckIn => 'Check-in Quotidiano';

  @override
  String get settingsDailyCheckInSubtitle =>
      'Promemoria gentile per prenderti cura di te';

  @override
  String get settingsExportData => 'Esporta Dati';

  @override
  String get settingsExportDataSubtitle => 'Scarica la tua cronologia';

  @override
  String get settingsClearData => 'Cancella Cronologia';

  @override
  String get settingsClearDataSubtitle => 'Elimina tutti i dati';

  @override
  String get settingsPrivacyPolicy => 'Privacy Policy';

  @override
  String get settingsTerms => 'Termini di Servizio';

  @override
  String get settingsAboutApp => 'Info su HOPE';

  @override
  String get settingsFeedback => 'Invia Feedback';

  @override
  String get settingsFeedbackSubtitle => 'Aiutaci a migliorare HOPE';

  @override
  String get settingsLoginSoon => 'Login presto disponibile';

  @override
  String get settingsExportConfirm => 'Esporta i tuoi Dati';

  @override
  String get settingsClearConfirm => 'Eliminare Tutti i Dati?';

  @override
  String get settingsFeedbackSuccess => 'Grazie per il tuo feedback!';

  @override
  String get settingsSpeedSlow => 'Lento';

  @override
  String get settingsSpeedNormal => 'Normale';

  @override
  String get settingsSpeedFast => 'Veloce';

  @override
  String get settingsThemeSystem => 'Sistema';

  @override
  String get settingsThemeLight => 'Chiaro';

  @override
  String get settingsThemeDark => 'Scuro';

  @override
  String get settingsWelcome => 'Benvenuto';

  @override
  String get settingsAnonymous => 'Utente Anonimo';

  @override
  String get settingsIrreversible => 'Questa azione è IRREVERSIBILE.';

  @override
  String get settingsDeleteAction => 'Elimina';

  @override
  String get settingsExportAction => 'Esporta';

  @override
  String get settingsCancel => 'Annulla';

  @override
  String get crisisFlowTitle => 'No estás solo/a';

  @override
  String get crisisFlowOr => 'o';

  @override
  String get crisisFlowExercisePrompt =>
      'Si lo prefieres, podemos probar ejercicios de relajación juntos.';

  @override
  String get crisisFlowCompanionNeeded =>
      'Ho solo bisogno che qualcuno sia con me';

  @override
  String get homeSubtitle => 'Il tuo spazio sicuro';

  @override
  String get homeSupportMessage =>
      'Sei più forte di quanto pensi. Siamo qui quando hai bisogno di noi.';

  @override
  String get quickActionBreathe => 'Respira';

  @override
  String get quickActionGrounding => 'Ancoraggio';

  @override
  String get quickActionCrisisNumber => 'Crisi';

  @override
  String get crisisSubtitle => 'L\'aiuto professionale è sempre disponibile';

  @override
  String get crisisSuicidePreventionTitle => 'Prevenzione Suicidio';

  @override
  String get crisisSuicidePreventionDescription =>
      'Linea di supporto crisi 24/7';

  @override
  String get crisisEuropeanEmergencyTitle => 'Emergenza Europea';

  @override
  String get crisisEuropeanEmergencyDescription =>
      'Servizi di emergenza in Europa';

  @override
  String get crisisSOSFriendshipTitle => 'SOS Amicizia';

  @override
  String get crisisSOSFriendshipDescription => 'Servizio di ascolto e supporto';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE non sostituisce l\'aiuto professionale. Se sei in pericolo, chiama i servizi di emergenza.';

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
