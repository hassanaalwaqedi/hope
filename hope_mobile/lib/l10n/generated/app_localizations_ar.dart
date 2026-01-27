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
  String get settingsTheme => 'المظهر';

  @override
  String get settingsNotifications => 'الإشعارات';

  @override
  String get settingsPrivacy => 'الخصوصية والبيانات';

  @override
  String get settingsAbout => 'عن HOPE';

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
}
