// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for French (`fr`).
class AppLocalizationsFr extends AppLocalizations {
  AppLocalizationsFr([String locale = 'fr']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => 'Accueil';

  @override
  String get navChat => 'Discussion';

  @override
  String get navHistory => 'Historique';

  @override
  String get navResources => 'Ressources';

  @override
  String get navSettings => 'Paramètres';

  @override
  String get panicButtonText => 'J\'ai besoin d\'aide maintenant';

  @override
  String get panicButtonSubtext => 'Appuyez si vous avez une crise de panique';

  @override
  String get breathingTitle => 'Exercice de Respiration';

  @override
  String get breatheIn => 'Inspirez';

  @override
  String get holdBreath => 'Retenez';

  @override
  String get breatheOut => 'Expirez';

  @override
  String get groundingTitle => 'Exercice d\'Ancrage';

  @override
  String get groundingInstructions => 'Regardez autour de vous et trouvez :';

  @override
  String groundingSee(int count) {
    return '$count choses que vous voyez';
  }

  @override
  String groundingTouch(int count) {
    return '$count choses que vous touchez';
  }

  @override
  String groundingHear(int count) {
    return '$count choses que vous entendez';
  }

  @override
  String groundingSmell(int count) {
    return '$count choses que vous sentez';
  }

  @override
  String groundingTaste(int count) {
    return '$count chose que vous goûtez';
  }

  @override
  String get chatWelcome =>
      'Je suis là avec toi. Comment te sens-tu en ce moment ?';

  @override
  String get chatInputHint => 'Exprimez ce que vous ressentez...';

  @override
  String get chatSendButton => 'Envoyer';

  @override
  String get crisisTitle => 'Soutien en Crise';

  @override
  String crisisEmergency(String number) {
    return 'Urgences : $number';
  }

  @override
  String get crisisHotline => 'Ligne de Crise';

  @override
  String get crisisAvailable247 => 'Disponible 24h/24';

  @override
  String get crisisCall => 'Appeler';

  @override
  String get humanSupportNotice =>
      'HOPE fournit uniquement un soutien par IA. Pour une assistance humaine, contactez les ressources de crise ci-dessus.';

  @override
  String get aiOnlyDisclaimer =>
      'Ceci est un assistant IA, pas un conseiller humain';

  @override
  String get settingsLanguage => 'Langue';

  @override
  String get settingsTheme => 'Thème';

  @override
  String get settingsNotifications => 'Notifications';

  @override
  String get settingsPrivacy => 'Confidentialité et Données';

  @override
  String get settingsAbout => 'À Propos';

  @override
  String get consentTitle => 'Bienvenue sur HOPE';

  @override
  String get consentTerms => 'J\'accepte les Conditions d\'Utilisation';

  @override
  String get consentPrivacy => 'J\'accepte la Politique de Confidentialité';

  @override
  String get consentAge => 'Je confirme avoir 13 ans ou plus';

  @override
  String get consentContinue => 'Continuer';

  @override
  String get errorGeneric => 'Une erreur s\'est produite. Veuillez réessayer.';

  @override
  String get errorNetwork =>
      'Connexion impossible. Vérifiez votre connexion Internet.';

  @override
  String get loading => 'Chargement...';

  @override
  String get retry => 'Réessayer';

  @override
  String get cancel => 'Annuler';

  @override
  String get ok => 'OK';

  @override
  String get done => 'Terminé';

  @override
  String get historyEmptyTitle => 'Pas encore de sessions';

  @override
  String get historyEmptySubtitle => 'Vos sessions apparaîtront ici';

  @override
  String get historyStatsSessions => 'Sessions';

  @override
  String get historyStatsTotal => 'Total';

  @override
  String get historyStatsIntensity => 'Intensité';

  @override
  String get historyRecent => 'Sessions récentes';

  @override
  String get historyWeek => 'Cette semaine';

  @override
  String get resourcesTitle => 'Ressources';

  @override
  String get resourcesBannerTitle => 'En crise ? Appelez le 3114';

  @override
  String get resourcesBannerSubtitle => 'Gratuit, confidentiel, 24h/24';

  @override
  String get resourcesEmergencyNumbers => 'Numéros d\'Urgence';

  @override
  String get resourcesSupportLines => 'Lignes d\'Écoute';

  @override
  String get resourcesCopingTechniques => 'Techniques de Gestion';

  @override
  String get resourcesInternationalHelp => 'Aide Internationale';

  @override
  String get resourcesMedicalDisclaimer =>
      'Cette application ne remplace pas un avis médical professionnel. En cas d\'urgence, appelez le 112.';

  @override
  String get resourceSuicidePrevention => 'Prévention du Suicide';

  @override
  String get resourceEuropeanEmergency => 'Urgences Européennes';

  @override
  String get resourceMedicalEmergency => 'SAMU';

  @override
  String get resourceSOSFriendship => 'SOS Amitié';

  @override
  String get resourceYouthHealth => 'Fil Santé Jeunes';

  @override
  String get resourceRedCross => 'Croix-Rouge Écoute';

  @override
  String get techniqueBreathing => 'Respiration Carrée';

  @override
  String get techniqueBreathingDesc => 'Technique 4-4-4-4 pour le calme';

  @override
  String get techniqueGrounding => 'Ancrage 5-4-3-2-1';

  @override
  String get techniqueGroundingDesc => 'Utilisez vos sens pour vous ancrer';

  @override
  String get techniqueRelaxation => 'Relaxation Musculaire';

  @override
  String get techniqueRelaxationDesc => 'Technique de tension-relâchement';

  @override
  String get settingsTitle => 'Réglages';

  @override
  String get settingsProfile => 'Profil';

  @override
  String get settingsPanicMode => 'Mode Panique';

  @override
  String get settingsAppearance => 'Apparence';

  @override
  String get settingsDataPrivacy => 'Données & Confidentialité';

  @override
  String get settingsVoiceGuidance => 'Guidance Vocale';

  @override
  String get settingsVoiceGuidanceSubtitle =>
      'Instructions parlées pendant les exercices';

  @override
  String get settingsHaptic => 'Retour Haptique';

  @override
  String get settingsHapticSubtitle => 'Vibrations pendant les exercices';

  @override
  String get settingsBreathingSpeed => 'Vitesse de Respiration';

  @override
  String get settingsBreathingSpeedSubtitle =>
      'Ajuster le rythme des exercices';

  @override
  String get settingsDailyCheckIn => 'Check-in Quotidien';

  @override
  String get settingsDailyCheckInSubtitle =>
      'Rappel bienveillant pour prendre soin de toi';

  @override
  String get settingsExportData => 'Exporter les Données';

  @override
  String get settingsExportDataSubtitle => 'Télécharger ton historique';

  @override
  String get settingsClearData => 'Effacer l\'Historique';

  @override
  String get settingsClearDataSubtitle => 'Supprimer toutes les données';

  @override
  String get settingsPrivacyPolicy => 'Politique de Confidentialité';

  @override
  String get settingsTerms => 'Conditions d\'Utilisation';

  @override
  String get settingsAboutApp => 'À Propos de HOPE';

  @override
  String get settingsFeedback => 'Envoyer un Feedback';

  @override
  String get settingsFeedbackSubtitle => 'Aide-nous à améliorer HOPE';

  @override
  String get settingsLoginSoon => 'Connexion bientôt disponible';

  @override
  String get settingsExportConfirm => 'Exporter tes Données';

  @override
  String get settingsClearConfirm => 'Supprimer Toutes les Données?';

  @override
  String get settingsFeedbackSuccess => 'Merci pour ton feedback!';

  @override
  String get settingsSpeedSlow => 'Lent';

  @override
  String get settingsSpeedNormal => 'Normal';

  @override
  String get settingsSpeedFast => 'Rapide';

  @override
  String get settingsThemeSystem => 'Système';

  @override
  String get settingsThemeLight => 'Clair';

  @override
  String get settingsThemeDark => 'Sombre';

  @override
  String get settingsWelcome => 'Bienvenue';

  @override
  String get settingsAnonymous => 'Utilisateur Anonyme';

  @override
  String get settingsIrreversible => 'Cette action est IRRÉVERSIBLE.';

  @override
  String get settingsDeleteAction => 'Supprimer';

  @override
  String get settingsExportAction => 'Exporter';

  @override
  String get settingsCancel => 'Annuler';

  @override
  String get crisisFlowTitle => 'Tu n\'es pas seul(e)';

  @override
  String get crisisFlowOr => 'ou';

  @override
  String get crisisFlowExercisePrompt =>
      'Si tu préfères, nous pouvons essayer des exercices de calme ensemble.';

  @override
  String get crisisFlowCompanionNeeded =>
      'J\'ai juste besoin que quelqu\'un soit avec moi';

  @override
  String get homeSubtitle => 'Ton espace sûr';

  @override
  String get homeSupportMessage =>
      'Tu es plus fort(e) que tu ne le penses. Nous sommes là quand tu as besoin de nous.';

  @override
  String get quickActionBreathe => 'Respirer';

  @override
  String get quickActionGrounding => 'Ancrage';

  @override
  String get quickActionCrisisNumber => 'Crise';

  @override
  String get crisisSubtitle =>
      'L\'aide professionnelle est toujours disponible';

  @override
  String get crisisSuicidePreventionTitle => 'Prévention du Suicide';

  @override
  String get crisisSuicidePreventionDescription =>
      'Ligne de soutien en crise 24h/24';

  @override
  String get crisisEuropeanEmergencyTitle => 'Urgences Européennes';

  @override
  String get crisisEuropeanEmergencyDescription =>
      'Services d\'urgence en Europe';

  @override
  String get crisisSOSFriendshipTitle => 'SOS Amitié';

  @override
  String get crisisSOSFriendshipDescription =>
      'Service d\'écoute et de soutien';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE ne remplace pas l\'aide professionnelle. Si vous êtes en danger, appelez les services d\'urgence.';

  @override
  String get chatNoInternet => 'Pas de connexion internet';

  @override
  String get chatOfflineMode => 'Mode hors-ligne : réponses limitées';

  @override
  String get chatReconnected =>
      '✓ Connexion rétablie - réponses complètes disponibles';

  @override
  String get chatWelcomeOnline =>
      'Bonjour, je suis là pour t\'écouter. Comment te sens-tu aujourd\'hui ?';

  @override
  String get chatWelcomeOffline =>
      'Bonjour, je suis là pour t\'écouter. (Mode hors-ligne)';

  @override
  String get chatStreamError =>
      'Désolé, une erreur est survenue. Veuillez réessayer.';

  @override
  String get chatCamera => 'Appareil photo';

  @override
  String get chatGallery => 'Galerie';

  @override
  String get chatImageReady => 'Image prête';
}
