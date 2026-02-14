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
  String get settingsAbout => 'Acerca de';

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

  @override
  String get historyEmptyTitle => 'Aún no hay historial';

  @override
  String get historyEmptySubtitle => 'Tus conversaciones aparecerán aquí';

  @override
  String get historyStatsSessions => 'Sesiones';

  @override
  String get historyStatsTotal => 'Total';

  @override
  String get historyStatsIntensity => 'Intensidad';

  @override
  String get historyRecent => 'Sesiones Recientes';

  @override
  String get historyWeek => 'Esta Semana';

  @override
  String get resourcesTitle => 'Recursos';

  @override
  String get resourcesBannerTitle => '¿En crisis? Llama al 3114';

  @override
  String get resourcesBannerSubtitle => 'Gratis, confidencial, 24/7';

  @override
  String get resourcesEmergencyNumbers => 'Números de Emergencia';

  @override
  String get resourcesSupportLines => 'Líneas de Apoyo';

  @override
  String get resourcesCopingTechniques => 'Técnicas de Afrontamiento';

  @override
  String get resourcesInternationalHelp => 'Ayuda Internacional';

  @override
  String get resourcesMedicalDisclaimer =>
      'Esta app no reemplaza el consejo médico profesional. En caso de emergencia, llama al 112.';

  @override
  String get resourceSuicidePrevention => 'Prevención del Suicidio';

  @override
  String get resourceEuropeanEmergency => 'Emergencia Europea';

  @override
  String get resourceMedicalEmergency => 'Servicios Médicos de Emergencia';

  @override
  String get resourceSOSFriendship => 'SOS Amistad';

  @override
  String get resourceYouthHealth => 'Línea de Salud Juvenil';

  @override
  String get resourceRedCross => 'Cruz Roja Escucha';

  @override
  String get techniqueBreathing => 'Respiración Cuadrada';

  @override
  String get techniqueBreathingDesc => 'Técnica 4-4-4-4 para la calma';

  @override
  String get techniqueGrounding => 'Anclaje 5-4-3-2-1';

  @override
  String get techniqueGroundingDesc => 'Usa tus sentidos para anclarte';

  @override
  String get techniqueRelaxation => 'Relajación Muscular';

  @override
  String get techniqueRelaxationDesc => 'Técnica de tensión-relajación';

  @override
  String get settingsTitle => 'Ajustes';

  @override
  String get settingsProfile => 'Perfil';

  @override
  String get settingsPanicMode => 'Modo Pánico';

  @override
  String get settingsAppearance => 'Apariencia';

  @override
  String get settingsDataPrivacy => 'Datos y Privacidad';

  @override
  String get settingsVoiceGuidance => 'Guía de Voz';

  @override
  String get settingsVoiceGuidanceSubtitle =>
      'Instrucciones habladas durante los ejercicios';

  @override
  String get settingsHaptic => 'Retroalimentación Háptica';

  @override
  String get settingsHapticSubtitle => 'Vibraciones durante los ejercicios';

  @override
  String get settingsBreathingSpeed => 'Velocidad de Respiración';

  @override
  String get settingsBreathingSpeedSubtitle =>
      'Ajustar el ritmo de los ejercicios';

  @override
  String get settingsDailyCheckIn => 'Check-in Diario';

  @override
  String get settingsDailyCheckInSubtitle => 'Recordatorio para cuidar de ti';

  @override
  String get settingsExportData => 'Exportar Datos';

  @override
  String get settingsExportDataSubtitle => 'Descargar tu historial';

  @override
  String get settingsClearData => 'Borrar Historial';

  @override
  String get settingsClearDataSubtitle => 'Eliminar todos los datos';

  @override
  String get settingsPrivacyPolicy => 'Política de Privacidad';

  @override
  String get settingsTerms => 'Términos de Servicio';

  @override
  String get settingsAboutApp => 'Acerca de HOPE';

  @override
  String get settingsFeedback => 'Enviar Comentarios';

  @override
  String get settingsFeedbackSubtitle => 'Ayúdanos a mejorar HOPE';

  @override
  String get settingsLoginSoon => 'Inicio de sesión próximamente';

  @override
  String get settingsExportConfirm => 'Exportar tus Datos';

  @override
  String get settingsClearConfirm => '¿Eliminar Todos los Datos?';

  @override
  String get settingsFeedbackSuccess => '¡Gracias por tus comentarios!';

  @override
  String get settingsSpeedSlow => 'Lento';

  @override
  String get settingsSpeedNormal => 'Normal';

  @override
  String get settingsSpeedFast => 'Rápido';

  @override
  String get settingsThemeSystem => 'Sistema';

  @override
  String get settingsThemeLight => 'Claro';

  @override
  String get settingsThemeDark => 'Oscuro';

  @override
  String get settingsWelcome => 'Bienvenido';

  @override
  String get settingsAnonymous => 'Usuario Anónimo';

  @override
  String get settingsIrreversible => 'Esta acción es IRREVERSIBLE.';

  @override
  String get settingsDeleteAction => 'Eliminar';

  @override
  String get settingsExportAction => 'Exportar';

  @override
  String get settingsCancel => 'Cancelar';

  @override
  String get crisisFlowTitle => 'No estás solo/a';

  @override
  String get crisisFlowOr => 'o';

  @override
  String get crisisFlowExercisePrompt =>
      'Si lo prefieres, podemos probar ejercicios de relajación juntos.';

  @override
  String get crisisFlowCompanionNeeded =>
      'Solo necesito que alguien esté conmigo';

  @override
  String get homeSubtitle => 'Tu espacio seguro';

  @override
  String get homeSupportMessage =>
      'Eres más fuerte de lo que crees. Estamos aquí cuando nos necesites.';

  @override
  String get quickActionBreathe => 'Respirar';

  @override
  String get quickActionGrounding => 'Anclaje';

  @override
  String get quickActionCrisisNumber => 'Crisis';

  @override
  String get crisisSubtitle => 'La ayuda profesional siempre está disponible';

  @override
  String get crisisSuicidePreventionTitle => 'Prevención del Suicidio';

  @override
  String get crisisSuicidePreventionDescription =>
      'Línea de apoyo en crisis 24/7';

  @override
  String get crisisEuropeanEmergencyTitle => 'Emergencia Europea';

  @override
  String get crisisEuropeanEmergencyDescription =>
      'Servicios de emergencia en Europa';

  @override
  String get crisisSOSFriendshipTitle => 'SOS Amistad';

  @override
  String get crisisSOSFriendshipDescription => 'Servicio de escucha y apoyo';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE no sustituye la ayuda profesional. Si estás en peligro, llama a los servicios de emergencia.';

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
