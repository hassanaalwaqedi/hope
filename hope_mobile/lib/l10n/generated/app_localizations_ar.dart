// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Arabic (`ar`).
class AppLocalizationsAr extends AppLocalizations {
  AppLocalizationsAr([String locale = 'ar']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => 'الرئيسية';

  @override
  String get navChat => 'المحادثة';

  @override
  String get navHistory => 'السجل';

  @override
  String get navResources => 'الموارد';

  @override
  String get navSettings => 'الإعدادات';

  @override
  String get panicButtonText => 'أحتاج المساعدة الآن';

  @override
  String get panicButtonSubtext => 'اضغط إذا كنت تعاني من نوبة هلع';

  @override
  String get breathingTitle => 'تمرين التنفس';

  @override
  String get breatheIn => 'استنشق';

  @override
  String get holdBreath => 'احبس';

  @override
  String get breatheOut => 'ازفر';

  @override
  String get groundingTitle => 'تمرين التثبيت';

  @override
  String get groundingInstructions => 'انظر حولك وابحث عن:';

  @override
  String groundingSee(int count) {
    return '$count أشياء تراها';
  }

  @override
  String groundingTouch(int count) {
    return '$count أشياء تلمسها';
  }

  @override
  String groundingHear(int count) {
    return '$count أشياء تسمعها';
  }

  @override
  String groundingSmell(int count) {
    return '$count أشياء تشمها';
  }

  @override
  String groundingTaste(int count) {
    return '$count شيء تتذوقه';
  }

  @override
  String get chatWelcome => 'أنا هنا معك. كيف تشعر الآن؟';

  @override
  String get chatInputHint => 'اكتب ما تشعر به...';

  @override
  String get chatSendButton => 'إرسال';

  @override
  String get crisisTitle => 'دعم الأزمات';

  @override
  String crisisEmergency(String number) {
    return 'الطوارئ: $number';
  }

  @override
  String get crisisHotline => 'خط الأزمات';

  @override
  String get crisisAvailable247 => 'متاح على مدار الساعة';

  @override
  String get crisisCall => 'اتصل الآن';

  @override
  String get humanSupportNotice =>
      'يوفر HOPE دعمًا بالذكاء الاصطناعي فقط. للحصول على مساعدة بشرية، يرجى الاتصال بموارد الأزمات أعلاه.';

  @override
  String get aiOnlyDisclaimer => 'هذا مساعد ذكاء اصطناعي، وليس مستشارًا بشريًا';

  @override
  String get settingsLanguage => 'اللغة';

  @override
  String get settingsTheme => 'السمة';

  @override
  String get settingsNotifications => 'الإشعارات';

  @override
  String get settingsPrivacy => 'الخصوصية والبيانات';

  @override
  String get settingsAbout => 'حول';

  @override
  String get consentTitle => 'مرحبًا بك في HOPE';

  @override
  String get consentTerms => 'أوافق على شروط الخدمة';

  @override
  String get consentPrivacy => 'أوافق على سياسة الخصوصية';

  @override
  String get consentAge => 'أؤكد أن عمري 13 سنة أو أكثر';

  @override
  String get consentContinue => 'متابعة';

  @override
  String get errorGeneric => 'حدث خطأ ما. يرجى المحاولة مرة أخرى.';

  @override
  String get errorNetwork => 'تعذر الاتصال. يرجى التحقق من اتصال الإنترنت.';

  @override
  String get loading => 'جاري التحميل...';

  @override
  String get retry => 'إعادة المحاولة';

  @override
  String get cancel => 'إلغاء';

  @override
  String get ok => 'موافق';

  @override
  String get done => 'تم';

  @override
  String get historyEmptyTitle => 'لا توجد جلسات بعد';

  @override
  String get historyEmptySubtitle => 'ستظهر محادثاتك هنا';

  @override
  String get historyStatsSessions => 'جلسات';

  @override
  String get historyStatsTotal => 'المجموع';

  @override
  String get historyStatsIntensity => 'الشدة';

  @override
  String get historyRecent => 'الجلسات الأخيرة';

  @override
  String get historyWeek => 'هذا الأسبوع';

  @override
  String get resourcesTitle => 'الموارد';

  @override
  String get resourcesBannerTitle => 'في أزمة؟ اتصل بـ 3114';

  @override
  String get resourcesBannerSubtitle => 'مجاني، سري، 24/7';

  @override
  String get resourcesEmergencyNumbers => 'أرقام الطوارئ';

  @override
  String get resourcesSupportLines => 'خطوط الدعم';

  @override
  String get resourcesCopingTechniques => 'تقنيات التأقلم';

  @override
  String get resourcesInternationalHelp => 'مساعدة دولية';

  @override
  String get resourcesMedicalDisclaimer =>
      'هذا التطبيق لا يحل محل المشورة الطبية المهنية. في حالة الطوارئ، اتصل بـ 112.';

  @override
  String get resourceSuicidePrevention => 'منع الانتحار';

  @override
  String get resourceEuropeanEmergency => 'الطوارئ الأوروبية';

  @override
  String get resourceMedicalEmergency => 'الخدمات الطبية الطارئة';

  @override
  String get resourceSOSFriendship => 'SOS صداقة';

  @override
  String get resourceYouthHealth => 'خط صحة الشباب';

  @override
  String get resourceRedCross => 'استماع الصليب الأحمر';

  @override
  String get techniqueBreathing => 'التنفس المربع';

  @override
  String get techniqueBreathingDesc => 'تقنية 4-4-4-4 للهدوء';

  @override
  String get techniqueGrounding => 'تثبيت 5-4-3-2-1';

  @override
  String get techniqueGroundingDesc => 'استخدم حواسك لتثبيت نفسك';

  @override
  String get techniqueRelaxation => 'استرخاء العضلات';

  @override
  String get techniqueRelaxationDesc => 'تقنية الشد والإرخاء';

  @override
  String get settingsTitle => 'الإعدادات';

  @override
  String get settingsProfile => 'الملف الشخصي';

  @override
  String get settingsPanicMode => 'وضع الذعر';

  @override
  String get settingsAppearance => 'المظهر';

  @override
  String get settingsDataPrivacy => 'البيانات والخصوصية';

  @override
  String get settingsVoiceGuidance => 'التوجيه الصوتي';

  @override
  String get settingsVoiceGuidanceSubtitle => 'تعليمات صوتية أثناء التمارين';

  @override
  String get settingsHaptic => 'الاهتزاز';

  @override
  String get settingsHapticSubtitle => 'اهتزازات أثناء التمارين';

  @override
  String get settingsBreathingSpeed => 'سرعة التنفس';

  @override
  String get settingsBreathingSpeedSubtitle => 'ضبط وتيرة التمارين';

  @override
  String get settingsDailyCheckIn => 'التفقد اليومي';

  @override
  String get settingsDailyCheckInSubtitle => 'تذكير لطيف للاعتناء بنفسك';

  @override
  String get settingsExportData => 'تصدير البيانات';

  @override
  String get settingsExportDataSubtitle => 'تنزيل سجلك';

  @override
  String get settingsClearData => 'مسح السجل';

  @override
  String get settingsClearDataSubtitle => 'حذف جميع البيانات';

  @override
  String get settingsPrivacyPolicy => 'سياسة الخصوصية';

  @override
  String get settingsTerms => 'شروط الخدمة';

  @override
  String get settingsAboutApp => 'حول HOPE';

  @override
  String get settingsFeedback => 'إرسال تعليقات';

  @override
  String get settingsFeedbackSubtitle => 'ساعدنا في تحسين HOPE';

  @override
  String get settingsLoginSoon => 'تسجيل الدخول قريباً';

  @override
  String get settingsExportConfirm => 'تصدير بياناتك';

  @override
  String get settingsClearConfirm => 'حذف جميع البيانات؟';

  @override
  String get settingsFeedbackSuccess => 'شكراً لتعليقاتك!';

  @override
  String get settingsSpeedSlow => 'بطيء';

  @override
  String get settingsSpeedNormal => 'عادي';

  @override
  String get settingsSpeedFast => 'سريع';

  @override
  String get settingsThemeSystem => 'النظام';

  @override
  String get settingsThemeLight => 'فاتح';

  @override
  String get settingsThemeDark => 'داكن';

  @override
  String get settingsWelcome => 'أهلاً بك';

  @override
  String get settingsAnonymous => 'مستخدم مجهول';

  @override
  String get settingsIrreversible => 'هذا الإجراء لا رجعة فيه.';

  @override
  String get settingsDeleteAction => 'حذف';

  @override
  String get settingsExportAction => 'تصدير';

  @override
  String get settingsCancel => 'إلغاء';

  @override
  String get crisisFlowTitle => 'أنت لست وحدك';

  @override
  String get crisisFlowOr => 'أو';

  @override
  String get crisisFlowExercisePrompt =>
      'إذا كنت تفضل، يمكننا تجربة تمارين الاسترخاء معًا.';

  @override
  String get crisisFlowCompanionNeeded => 'أحتاج فقط أن يكون شخص ما معي';

  @override
  String get homeSubtitle => 'مساحتك الآمنة';

  @override
  String get homeSupportMessage =>
      'أنت أقوى مما تعتقد. نحن هنا عندما تحتاج إلينا.';

  @override
  String get quickActionBreathe => 'تنفس';

  @override
  String get quickActionGrounding => 'تثبيت';

  @override
  String get quickActionCrisisNumber => 'أزمة';

  @override
  String get crisisSubtitle => 'المساعدة المهنية متاحة دائمًا';

  @override
  String get crisisSuicidePreventionTitle => 'منع الانتحار';

  @override
  String get crisisSuicidePreventionDescription =>
      'خط دعم الأزمات على مدار الساعة';

  @override
  String get crisisEuropeanEmergencyTitle => 'الطوارئ الأوروبية';

  @override
  String get crisisEuropeanEmergencyDescription => 'خدمات الطوارئ عبر أوروبا';

  @override
  String get crisisSOSFriendshipTitle => 'SOS صداقة';

  @override
  String get crisisSOSFriendshipDescription => 'خدمة الاستماع والدعم';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE ليس بديلاً عن المساعدة المهنية. إذا كنت في خطر، اتصل بخدمات الطوارئ.';

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
