// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Spanish Castilian (`es`).
class AppLocalizationsEs extends AppLocalizations {
  AppLocalizationsEs([String locale = 'es']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => 'Inicio';

  @override
  String get navChat => 'Chat';

  @override
  String get navHistory => 'Historial';

  @override
  String get navResources => 'Recursos';

  @override
  String get navSettings => 'Ajustes';

  @override
  String get panicButtonText => 'Necesito ayuda ahora';

  @override
  String get panicButtonSubtext => 'Toca si estás teniendo un ataque de pánico';

  @override
  String get breathingTitle => 'Ejercicio de Respiración';

  @override
  String get breatheIn => 'Inhala';

  @override
  String get holdBreath => 'Mantén';

  @override
  String get breatheOut => 'Exhala';

  @override
  String get groundingTitle => 'Ejercicio de Anclaje';

  @override
  String get groundingInstructions => 'Mira a tu alrededor y encuentra:';

  @override
  String groundingSee(int count) {
    return '$count cosas que puedas ver';
  }

  @override
  String groundingTouch(int count) {
    return '$count cosas que puedas tocar';
  }

  @override
  String groundingHear(int count) {
    return '$count cosas que puedas escuchar';
  }

  @override
  String groundingSmell(int count) {
    return '$count cosas que puedas oler';
  }

  @override
  String groundingTaste(int count) {
    return '$count cosa que puedas saborear';
  }

  @override
  String get chatWelcome => 'Estoy aquí contigo. ¿Cómo te sientes ahora mismo?';

  @override
  String get chatInputHint => 'Escribe cómo te sientes...';

  @override
  String get chatSendButton => 'Enviar';

  @override
  String get crisisTitle => 'Apoyo en Crisis';

  @override
  String crisisEmergency(String number) {
    return 'Emergencias: $number';
  }

  @override
  String get crisisHotline => 'Línea de Crisis';

  @override
  String get crisisAvailable247 => 'Disponible 24/7';

  @override
  String get crisisCall => 'Llamar Ahora';

  @override
  String get humanSupportNotice =>
      'HOPE proporciona solo soporte con IA. Para asistencia humana, contacta los recursos de crisis arriba.';

  @override
  String get aiOnlyDisclaimer =>
      'Este es un asistente de IA, no un consejero humano';

  @override
  String get settingsLanguage => 'Idioma';

  @override
  String get settingsTheme => 'Tema';

  @override
  String get settingsNotifications => 'Notificaciones';

  @override
  String get settingsPrivacy => 'Privacidad y Datos';

  @override
  String get settingsAbout => 'Acerca de HOPE';

  @override
  String get consentTitle => 'Bienvenido a HOPE';

  @override
  String get consentTerms => 'Acepto los Términos de Servicio';

  @override
  String get consentPrivacy => 'Acepto la Política de Privacidad';

  @override
  String get consentAge => 'Confirmo que tengo 13 años o más';

  @override
  String get consentContinue => 'Continuar';

  @override
  String get errorGeneric => 'Algo salió mal. Por favor, inténtalo de nuevo.';

  @override
  String get errorNetwork =>
      'No se puede conectar. Verifica tu conexión a Internet.';

  @override
  String get loading => 'Cargando...';

  @override
  String get retry => 'Reintentar';

  @override
  String get cancel => 'Cancelar';

  @override
  String get ok => 'OK';

  @override
  String get done => 'Listo';
}
