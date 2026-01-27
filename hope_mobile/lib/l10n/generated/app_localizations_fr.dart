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
  String get settingsAbout => 'À propos de HOPE';

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
}
