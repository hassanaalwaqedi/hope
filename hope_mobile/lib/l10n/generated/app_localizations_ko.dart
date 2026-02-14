// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Korean (`ko`).
class AppLocalizationsKo extends AppLocalizations {
  AppLocalizationsKo([String locale = 'ko']) : super(locale);

  @override
  String get appTitle => 'HOPE';

  @override
  String get navHome => '홈';

  @override
  String get navChat => '채팅';

  @override
  String get navHistory => '기록';

  @override
  String get navResources => '리소스';

  @override
  String get navSettings => '설정';

  @override
  String get panicButtonText => '지금 도움이 필요해요';

  @override
  String get panicButtonSubtext => '공황 발작 중이라면 터치하세요';

  @override
  String get breathingTitle => '호흡 운동';

  @override
  String get breatheIn => '숨 들이마시기';

  @override
  String get holdBreath => '숨 참기';

  @override
  String get breatheOut => '숨 내쉬기';

  @override
  String get groundingTitle => '그라운딩 운동';

  @override
  String get groundingInstructions => '주변을 둘러보고 다음을 찾으세요:';

  @override
  String groundingSee(int count) {
    return '볼 수 있는 것 $count가지';
  }

  @override
  String groundingTouch(int count) {
    return '만질 수 있는 것 $count가지';
  }

  @override
  String groundingHear(int count) {
    return '들을 수 있는 것 $count가지';
  }

  @override
  String groundingSmell(int count) {
    return '냄새 맡을 수 있는 것 $count가지';
  }

  @override
  String groundingTaste(int count) {
    return '맛볼 수 있는 것 $count가지';
  }

  @override
  String get chatWelcome => '제가 여기 있습니다. 지금 기분이 어떠신가요?';

  @override
  String get chatInputHint => '현재 기분을 입력하세요...';

  @override
  String get chatSendButton => '전송';

  @override
  String get crisisTitle => '위기 지원';

  @override
  String crisisEmergency(String number) {
    return '응급: $number';
  }

  @override
  String get crisisHotline => '위기 핫라인';

  @override
  String get crisisAvailable247 => '24시간 연중무휴';

  @override
  String get crisisCall => '지금 전화하기';

  @override
  String get humanSupportNotice =>
      'HOPE는 AI 기반 지원만 제공합니다. 사람의 도움이 필요하면 위의 위기 리소스에 연락하세요.';

  @override
  String get aiOnlyDisclaimer => '이것은 AI 도우미이며, 인간 상담사가 아닙니다';

  @override
  String get settingsLanguage => '언어';

  @override
  String get settingsTheme => '테마';

  @override
  String get settingsNotifications => '알림';

  @override
  String get settingsPrivacy => '개인정보 및 데이터';

  @override
  String get settingsAbout => '정보';

  @override
  String get consentTitle => 'HOPE에 오신 것을 환영합니다';

  @override
  String get consentTerms => '서비스 이용약관에 동의합니다';

  @override
  String get consentPrivacy => '개인정보 처리방침에 동의합니다';

  @override
  String get consentAge => '만 13세 이상임을 확인합니다';

  @override
  String get consentContinue => '계속';

  @override
  String get errorGeneric => '문제가 발생했습니다. 다시 시도해 주세요.';

  @override
  String get errorNetwork => '연결할 수 없습니다. 인터넷 연결을 확인해 주세요.';

  @override
  String get loading => '로딩 중...';

  @override
  String get retry => '재시도';

  @override
  String get cancel => '취소';

  @override
  String get ok => '확인';

  @override
  String get done => '완료';

  @override
  String get historyEmptyTitle => '아직 기록이 없습니다';

  @override
  String get historyEmptySubtitle => '대화 내용이 여기에 표시됩니다';

  @override
  String get historyStatsSessions => '세션';

  @override
  String get historyStatsTotal => '총계';

  @override
  String get historyStatsIntensity => '강도';

  @override
  String get historyRecent => '최근 세션';

  @override
  String get historyWeek => '이번 주';

  @override
  String get resourcesTitle => '리소스';

  @override
  String get resourcesBannerTitle => '위기 상황인가요? 3114로 전화하세요';

  @override
  String get resourcesBannerSubtitle => '무료, 비밀 보장, 24/7';

  @override
  String get resourcesEmergencyNumbers => '응급 전화번호';

  @override
  String get resourcesSupportLines => '지원 라인';

  @override
  String get resourcesCopingTechniques => '대처 기술';

  @override
  String get resourcesInternationalHelp => '국제 지원';

  @override
  String get resourcesMedicalDisclaimer =>
      '이 앱은 전문적인 의학적 조언을 대체하지 않습니다. 응급 상황 시 112로 전화하세요.';

  @override
  String get resourceSuicidePrevention => '자살 예방';

  @override
  String get resourceEuropeanEmergency => '유럽 응급 번호';

  @override
  String get resourceMedicalEmergency => '응급 의료 서비스';

  @override
  String get resourceSOSFriendship => 'SOS 우정';

  @override
  String get resourceYouthHealth => '청소년 건강 라인';

  @override
  String get resourceRedCross => '적십자 경청';

  @override
  String get techniqueBreathing => '상자 호흡';

  @override
  String get techniqueBreathingDesc => '진정을 위한 4-4-4-4 기법';

  @override
  String get techniqueGrounding => '5-4-3-2-1 그라운딩';

  @override
  String get techniqueGroundingDesc => '오감을 사용하여 안정을 찾으세요';

  @override
  String get techniqueRelaxation => '근육 이완';

  @override
  String get techniqueRelaxationDesc => '긴장-이완 기법';

  @override
  String get settingsTitle => '설정';

  @override
  String get settingsProfile => '프로필';

  @override
  String get settingsPanicMode => '공황 모드';

  @override
  String get settingsAppearance => '외관';

  @override
  String get settingsDataPrivacy => '데이터 및 개인정보';

  @override
  String get settingsVoiceGuidance => '음성 안내';

  @override
  String get settingsVoiceGuidanceSubtitle => '운동 중 음성 지침';

  @override
  String get settingsHaptic => '햅틱 피드백';

  @override
  String get settingsHapticSubtitle => '운동 중 진동';

  @override
  String get settingsBreathingSpeed => '호흡 속도';

  @override
  String get settingsBreathingSpeedSubtitle => '운동 속도 조절';

  @override
  String get settingsDailyCheckIn => '일일 체크인';

  @override
  String get settingsDailyCheckInSubtitle => '자신을 돌보는 부드러운 알림';

  @override
  String get settingsExportData => '데이터 내보내기';

  @override
  String get settingsExportDataSubtitle => '기록 다운로드';

  @override
  String get settingsClearData => '기록 지우기';

  @override
  String get settingsClearDataSubtitle => '모든 데이터 삭제';

  @override
  String get settingsPrivacyPolicy => '개인정보 처리방침';

  @override
  String get settingsTerms => '이용 약관';

  @override
  String get settingsAboutApp => 'HOPE 정보';

  @override
  String get settingsFeedback => '피드백 보내기';

  @override
  String get settingsFeedbackSubtitle => 'HOPE 개선에 도움을 주세요';

  @override
  String get settingsLoginSoon => '로그인 곧 제공 예정';

  @override
  String get settingsExportConfirm => '데이터 내보내기';

  @override
  String get settingsClearConfirm => '모든 데이터 삭제?';

  @override
  String get settingsFeedbackSuccess => '피드백 감사합니다!';

  @override
  String get settingsSpeedSlow => '느림';

  @override
  String get settingsSpeedNormal => '보통';

  @override
  String get settingsSpeedFast => '빠름';

  @override
  String get settingsThemeSystem => '시스템';

  @override
  String get settingsThemeLight => '라이트';

  @override
  String get settingsThemeDark => '다크';

  @override
  String get settingsWelcome => '환영합니다';

  @override
  String get settingsAnonymous => '익명 사용자';

  @override
  String get settingsIrreversible => '이 작업은 되돌릴 수 없습니다.';

  @override
  String get settingsDeleteAction => '삭제';

  @override
  String get settingsExportAction => '내보내기';

  @override
  String get settingsCancel => '취소';

  @override
  String get crisisFlowTitle => '혼자가 아닙니다';

  @override
  String get crisisFlowOr => '또는';

  @override
  String get crisisFlowExercisePrompt => '원하신다면 함께 진정 운동을 해볼 수 있습니다.';

  @override
  String get crisisFlowCompanionNeeded => '누군가와 함께 있고 싶어요';

  @override
  String get homeSubtitle => '당신의 안전한 공간';

  @override
  String get homeSupportMessage => '당신은 생각보다 강합니다. 필요할 때 언제든 여기 있습니다.';

  @override
  String get quickActionBreathe => '호흡';

  @override
  String get quickActionGrounding => '그라운딩';

  @override
  String get quickActionCrisisNumber => '위기';

  @override
  String get crisisSubtitle => '전문적인 도움은 항상 이용 가능합니다';

  @override
  String get crisisSuicidePreventionTitle => '자살 예방';

  @override
  String get crisisSuicidePreventionDescription => '24시간 위기 상담 전화';

  @override
  String get crisisEuropeanEmergencyTitle => '유럽 응급 번호';

  @override
  String get crisisEuropeanEmergencyDescription => '유럽 전역 응급 서비스';

  @override
  String get crisisSOSFriendshipTitle => 'SOS 우정';

  @override
  String get crisisSOSFriendshipDescription => '경청 및 지원 서비스';

  @override
  String get crisisEmergencyDisclaimer =>
      'HOPE는 전문적인 도움을 대체하지 않습니다. 위험한 상황이라면 응급 서비스에 전화하세요.';

  @override
  String get chatNoInternet => '인터넷 연결 없음';

  @override
  String get chatOfflineMode => '오프라인 모드: 제한된 응답';

  @override
  String get chatReconnected => '✓ 연결됨 - 전체 AI 응답 이용 가능';

  @override
  String get chatWelcomeOnline =>
      '안녕하세요, 당신의 이야기를 들을 준비가 되어 있습니다. 오늘 기분이 어떠신가요?';

  @override
  String get chatWelcomeOffline => '안녕하세요, 당신의 이야기를 들을 준비가 되어 있습니다. (오프라인 모드)';

  @override
  String get chatStreamError => '죄송합니다, 오류가 발생했습니다. 다시 시도해 주세요.';

  @override
  String get chatCamera => '카메라';

  @override
  String get chatGallery => '갤러리';

  @override
  String get chatImageReady => '이미지 준비 완료';
}
