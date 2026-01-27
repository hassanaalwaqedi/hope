/// Voice Panic BLoC
/// 
/// Manages hands-free panic support flow.
/// Coordinates STT, TTS, and panic state for voice-first interaction.
/// 
/// This is NOT a chatbot - it's a LIFE-SAFETY voice support system.

import 'dart:async';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

import '../voice_stt_service.dart';
import '../voice_tts_service.dart';
import '../../../l10n/generated/app_localizations.dart';

// Events

abstract class VoicePanicEvent extends Equatable {
  const VoicePanicEvent();
  
  @override
  List<Object?> get props => [];
}

/// Start voice-first panic session
class VoicePanicStarted extends VoicePanicEvent {
  final String languageCode;
  final String countryCode;
  
  const VoicePanicStarted({
    this.languageCode = 'en',
    this.countryCode = 'US',
  });
  
  @override
  List<Object?> get props => [languageCode, countryCode];
}

/// User spoke - process voice input
class VoiceInputReceived extends VoicePanicEvent {
  final VoiceRecognitionResult result;
  
  const VoiceInputReceived(this.result);
  
  @override
  List<Object?> get props => [result];
}

/// AI response received - speak it
class VoiceResponseReady extends VoicePanicEvent {
  final String response;
  final String? severity;
  
  const VoiceResponseReady({
    required this.response,
    this.severity,
  });
  
  @override
  List<Object?> get props => [response, severity];
}

/// Start breathing exercise voice guidance
class VoiceBreathingStarted extends VoicePanicEvent {
  const VoiceBreathingStarted();
}

/// Start grounding exercise voice guidance
class VoiceGroundingStarted extends VoicePanicEvent {
  const VoiceGroundingStarted();
}

/// Toggle listening on/off
class VoiceListeningToggled extends VoicePanicEvent {
  const VoiceListeningToggled();
}

/// Stop voice session
class VoicePanicEnded extends VoicePanicEvent {
  const VoicePanicEnded();
}

/// Speak crisis resources
class VoiceCrisisResourcesRequested extends VoicePanicEvent {
  final String emergencyNumber;
  final String hotlineName;
  final String hotlineNumber;
  
  const VoiceCrisisResourcesRequested({
    required this.emergencyNumber,
    required this.hotlineName,
    required this.hotlineNumber,
  });
  
  @override
  List<Object?> get props => [emergencyNumber, hotlineName, hotlineNumber];
}

// States

enum VoicePanicPhase {
  idle,
  initializing,
  listening,
  processing,
  speaking,
  breathing,
  grounding,
  crisis,
  error,
}

class VoicePanicState extends Equatable {
  final VoicePanicPhase phase;
  final String? lastTranscript;
  final String? lastResponse;
  final String? errorMessage;
  final bool isListening;
  final bool isSpeaking;
  final double soundLevel;
  final String languageCode;
  final int breathingPhase; // 0=inhale, 1=hold, 2=exhale
  final int breathingCount;
  final int groundingStep; // 1-5 for 5-4-3-2-1
  
  const VoicePanicState({
    this.phase = VoicePanicPhase.idle,
    this.lastTranscript,
    this.lastResponse,
    this.errorMessage,
    this.isListening = false,
    this.isSpeaking = false,
    this.soundLevel = 0,
    this.languageCode = 'en',
    this.breathingPhase = 0,
    this.breathingCount = 0,
    this.groundingStep = 5,
  });
  
  VoicePanicState copyWith({
    VoicePanicPhase? phase,
    String? lastTranscript,
    String? lastResponse,
    String? errorMessage,
    bool? isListening,
    bool? isSpeaking,
    double? soundLevel,
    String? languageCode,
    int? breathingPhase,
    int? breathingCount,
    int? groundingStep,
  }) {
    return VoicePanicState(
      phase: phase ?? this.phase,
      lastTranscript: lastTranscript ?? this.lastTranscript,
      lastResponse: lastResponse ?? this.lastResponse,
      errorMessage: errorMessage,
      isListening: isListening ?? this.isListening,
      isSpeaking: isSpeaking ?? this.isSpeaking,
      soundLevel: soundLevel ?? this.soundLevel,
      languageCode: languageCode ?? this.languageCode,
      breathingPhase: breathingPhase ?? this.breathingPhase,
      breathingCount: breathingCount ?? this.breathingCount,
      groundingStep: groundingStep ?? this.groundingStep,
    );
  }
  
  @override
  List<Object?> get props => [
    phase,
    lastTranscript,
    lastResponse,
    errorMessage,
    isListening,
    isSpeaking,
    soundLevel,
    languageCode,
    breathingPhase,
    breathingCount,
    groundingStep,
  ];
}

/// Voice Panic BLoC
/// 
/// Coordinates voice input/output for hands-free panic support.
class VoicePanicBloc extends Bloc<VoicePanicEvent, VoicePanicState> {
  final VoiceSttService _stt;
  final VoiceTtsService _tts;
  
  Timer? _breathingTimer;
  int _breathingCycleCount = 0;
  
  VoicePanicBloc({
    required VoiceSttService sttService,
    required VoiceTtsService ttsService,
  }) : _stt = sttService,
       _tts = ttsService,
       super(const VoicePanicState()) {
    
    // Register event handlers
    on<VoicePanicStarted>(_onPanicStarted);
    on<VoiceInputReceived>(_onInputReceived);
    on<VoiceResponseReady>(_onResponseReady);
    on<VoiceBreathingStarted>(_onBreathingStarted);
    on<VoiceGroundingStarted>(_onGroundingStarted);
    on<VoiceListeningToggled>(_onListeningToggled);
    on<VoicePanicEnded>(_onPanicEnded);
    on<VoiceCrisisResourcesRequested>(_onCrisisResources);
    
    // Set up service callbacks
    _setupCallbacks();
  }
  
  void _setupCallbacks() {
    _stt.onResult = (result) {
      add(VoiceInputReceived(result));
    };
    
    _stt.onStateChange = (state) {
      emit(this.state.copyWith(
        isListening: state == VoiceListeningState.listening,
      ));
    };
    
    _stt.onSoundLevel = (level) {
      emit(this.state.copyWith(soundLevel: level));
    };
    
    _stt.onError = (error) {
      emit(this.state.copyWith(
        phase: VoicePanicPhase.error,
        errorMessage: error,
      ));
    };
    
    _tts.onStateChange = (state) {
      emit(this.state.copyWith(
        isSpeaking: state == VoiceSpeakingState.speaking,
      ));
    };
    
    _tts.onError = (error) {
      // TTS error - fallback to text display
      emit(this.state.copyWith(
        phase: VoicePanicPhase.error,
        errorMessage: error,
      ));
    };
  }
  
  Future<void> _onPanicStarted(
    VoicePanicStarted event,
    Emitter<VoicePanicState> emit,
  ) async {
    emit(state.copyWith(
      phase: VoicePanicPhase.initializing,
      languageCode: event.languageCode,
    ));
    
    // Initialize services
    final sttReady = await _stt.initialize();
    final ttsReady = await _tts.initialize();
    
    if (!sttReady && !ttsReady) {
      emit(state.copyWith(
        phase: VoicePanicPhase.error,
        errorMessage: 'Voice not available on this device',
      ));
      return;
    }
    
    // Set language
    _stt.setLanguage(event.languageCode);
    await _tts.setLanguage(event.languageCode);
    
    // Speak welcome message
    await _tts.setMode(VoiceMode.panic);
    final welcome = _getWelcomeMessage(event.languageCode);
    await _tts.speak(welcome, immediate: true);
    
    emit(state.copyWith(
      phase: VoicePanicPhase.listening,
      lastResponse: welcome,
    ));
    
    // Start listening
    await _stt.startPanicListening(locale: event.languageCode);
  }
  
  Future<void> _onInputReceived(
    VoiceInputReceived event,
    Emitter<VoicePanicState> emit,
  ) async {
    if (!event.result.isFinal) {
      // Partial result - update transcript
      emit(state.copyWith(
        lastTranscript: event.result.transcript,
      ));
      return;
    }
    
    // Final result - process
    emit(state.copyWith(
      phase: VoicePanicPhase.processing,
      lastTranscript: event.result.transcript,
    ));
    
    // Check for voice commands
    final command = _detectVoiceCommand(event.result.transcript);
    if (command != null) {
      await _handleVoiceCommand(command, emit);
      return;
    }
    
    // Otherwise, this will be sent to the backend for AI processing
    // The caller should handle sending to API and then call VoiceResponseReady
  }
  
  Future<void> _onResponseReady(
    VoiceResponseReady event,
    Emitter<VoicePanicState> emit,
  ) async {
    emit(state.copyWith(
      phase: VoicePanicPhase.speaking,
      lastResponse: event.response,
    ));
    
    // Speak the response
    await _tts.speakForPanic(event.response);
    
    // Resume listening after speaking
    emit(state.copyWith(phase: VoicePanicPhase.listening));
    await _stt.startPanicListening(locale: state.languageCode);
  }
  
  Future<void> _onBreathingStarted(
    VoiceBreathingStarted event,
    Emitter<VoicePanicState> emit,
  ) async {
    await _stt.stopListening();
    await _tts.setMode(VoiceMode.breathing);
    
    emit(state.copyWith(
      phase: VoicePanicPhase.breathing,
      breathingPhase: 0,
      breathingCount: 0,
    ));
    
    // Start breathing cycle
    _startBreathingCycle(emit);
  }
  
  void _startBreathingCycle(Emitter<VoicePanicState>? emit) {
    _breathingCycleCount = 0;
    _runBreathingPhase(0, emit);
  }
  
  void _runBreathingPhase(int phase, Emitter<VoicePanicState>? emitter) async {
    if (state.phase != VoicePanicPhase.breathing) return;
    
    final instructions = _getBreathingInstructions(state.languageCode);
    final durations = [4, 4, 4]; // 4-4-4 breathing
    
    final instruction = instructions[phase];
    final duration = durations[phase];
    
    // Speak instruction
    await _tts.speakBreathingInstruction(instruction, duration);
    
    // Wait for phase duration
    _breathingTimer?.cancel();
    _breathingTimer = Timer(Duration(seconds: duration), () {
      final nextPhase = (phase + 1) % 3;
      
      if (nextPhase == 0) {
        _breathingCycleCount++;
      }
      
      // After 5 cycles, offer to continue or stop
      if (_breathingCycleCount >= 5 && nextPhase == 0) {
        _offerBreathingChoice();
        return;
      }
      
      _runBreathingPhase(nextPhase, null);
    });
  }
  
  Future<void> _offerBreathingChoice() async {
    final message = _getContinueMessage(state.languageCode);
    await _tts.speak(message, immediate: true);
    
    // Resume listening for response
    add(const VoiceListeningToggled());
  }
  
  Future<void> _onGroundingStarted(
    VoiceGroundingStarted event,
    Emitter<VoicePanicState> emit,
  ) async {
    await _stt.stopListening();
    await _tts.setMode(VoiceMode.panic);
    
    emit(state.copyWith(
      phase: VoicePanicPhase.grounding,
      groundingStep: 5,
    ));
    
    // Start grounding exercise
    await _runGroundingExercise(emit);
  }
  
  Future<void> _runGroundingExercise(Emitter<VoicePanicState> emit) async {
    final prompts = _getGroundingPrompts(state.languageCode);
    
    for (int step = 5; step >= 1; step--) {
      if (state.phase != VoicePanicPhase.grounding) return;
      
      emit(state.copyWith(groundingStep: step));
      
      await _tts.speakGroundingPrompt(prompts[5 - step], pauseMs: 5000);
      
      // Wait for user to process
      await Future.delayed(const Duration(seconds: 5));
    }
    
    // Completion message
    final complete = _getGroundingComplete(state.languageCode);
    await _tts.speak(complete, immediate: true);
    
    emit(state.copyWith(phase: VoicePanicPhase.listening));
    await _stt.startPanicListening(locale: state.languageCode);
  }
  
  Future<void> _onCrisisResources(
    VoiceCrisisResourcesRequested event,
    Emitter<VoicePanicState> emit,
  ) async {
    emit(state.copyWith(phase: VoicePanicPhase.crisis));
    
    await _tts.setMode(VoiceMode.panic);
    
    // Speak emergency info
    final intro = _getCrisisIntro(state.languageCode);
    await _tts.speak(intro, immediate: true);
    
    await Future.delayed(const Duration(seconds: 2));
    
    // Speak hotline number clearly
    await _tts.speakCrisisInfo(event.hotlineName, event.hotlineNumber);
    
    await Future.delayed(const Duration(seconds: 2));
    
    // Resume listening
    emit(state.copyWith(phase: VoicePanicPhase.listening));
    await _stt.startPanicListening(locale: state.languageCode);
  }
  
  Future<void> _onListeningToggled(
    VoiceListeningToggled event,
    Emitter<VoicePanicState> emit,
  ) async {
    if (_stt.isListening) {
      await _stt.stopListening();
      emit(state.copyWith(isListening: false));
    } else {
      await _stt.startPanicListening(locale: state.languageCode);
      emit(state.copyWith(
        phase: VoicePanicPhase.listening,
        isListening: true,
      ));
    }
  }
  
  Future<void> _onPanicEnded(
    VoicePanicEnded event,
    Emitter<VoicePanicState> emit,
  ) async {
    _breathingTimer?.cancel();
    await _stt.stopListening();
    await _tts.stop();
    
    emit(const VoicePanicState());
  }
  
  // Voice command detection
  
  String? _detectVoiceCommand(String transcript) {
    final lower = transcript.toLowerCase().trim();
    
    // Breathing commands
    if (_matchesCommand(lower, ['breathing', 'breathe', 'respirer', 'atmen', 'respirar', 'تنفس'])) {
      return 'breathing';
    }
    
    // Grounding commands
    if (_matchesCommand(lower, ['grounding', 'ground', 'ancrage', 'erdung', 'anclaje', 'تثبيت'])) {
      return 'grounding';
    }
    
    // Help commands
    if (_matchesCommand(lower, ['help', 'aide', 'hilfe', 'ayuda', 'مساعدة', 'need help'])) {
      return 'help';
    }
    
    // Stop commands
    if (_matchesCommand(lower, ['stop', 'arrêter', 'stopp', 'parar', 'توقف'])) {
      return 'stop';
    }
    
    // Crisis commands
    if (_matchesCommand(lower, ['crisis', 'emergency', 'urgence', 'notfall', 'emergencia', 'طوارئ'])) {
      return 'crisis';
    }
    
    return null;
  }
  
  bool _matchesCommand(String input, List<String> commands) {
    return commands.any((cmd) => input.contains(cmd));
  }
  
  Future<void> _handleVoiceCommand(String command, Emitter<VoicePanicState> emit) async {
    switch (command) {
      case 'breathing':
        add(const VoiceBreathingStarted());
        break;
      case 'grounding':
        add(const VoiceGroundingStarted());
        break;
      case 'stop':
        _breathingTimer?.cancel();
        await _tts.stop();
        emit(state.copyWith(phase: VoicePanicPhase.listening));
        await _stt.startPanicListening(locale: state.languageCode);
        break;
      case 'crisis':
        // Caller should handle providing crisis resources
        break;
      case 'help':
        final helpMsg = _getHelpMessage(state.languageCode);
        await _tts.speakForPanic(helpMsg);
        emit(state.copyWith(phase: VoicePanicPhase.listening));
        await _stt.startPanicListening(locale: state.languageCode);
        break;
    }
  }
  
  // Localized messages
  
  String _getWelcomeMessage(String lang) {
    const messages = {
      'en': "I'm here with you. You can speak to me, or say 'breathing' for a breathing exercise.",
      'fr': "Je suis là avec toi. Tu peux me parler, ou dire 'respirer' pour un exercice de respiration.",
      'ar': "أنا هنا معك. يمكنك التحدث معي، أو قل 'تنفس' لتمرين التنفس.",
      'de': "Ich bin bei dir. Du kannst mit mir sprechen, oder sag 'atmen' für eine Atemübung.",
      'es': "Estoy aquí contigo. Puedes hablarme, o di 'respirar' para un ejercicio de respiración.",
    };
    return messages[lang] ?? messages['en']!;
  }
  
  List<String> _getBreathingInstructions(String lang) {
    const instructions = {
      'en': ['Breathe in', 'Hold', 'Breathe out'],
      'fr': ['Inspirez', 'Retenez', 'Expirez'],
      'ar': ['استنشق', 'احبس', 'ازفر'],
      'de': ['Einatmen', 'Halten', 'Ausatmen'],
      'es': ['Inhala', 'Mantén', 'Exhala'],
    };
    return instructions[lang] ?? instructions['en']!;
  }
  
  String _getContinueMessage(String lang) {
    const messages = {
      'en': "How are you feeling? Say 'continue' for more breathing, or 'stop' when you're ready.",
      'fr': "Comment te sens-tu? Dis 'continuer' pour plus de respiration, ou 'arrêter' quand tu es prêt.",
      'ar': "كيف تشعر؟ قل 'استمر' لمزيد من التنفس، أو 'توقف' عندما تكون جاهزًا.",
      'de': "Wie fühlst du dich? Sag 'weiter' für mehr Atmung, oder 'stopp' wenn du bereit bist.",
      'es': "¿Cómo te sientes? Di 'continuar' para más respiración, o 'parar' cuando estés listo.",
    };
    return messages[lang] ?? messages['en']!;
  }
  
  List<String> _getGroundingPrompts(String lang) {
    const prompts = {
      'en': [
        'Look around and name 5 things you can see',
        'Now, 4 things you can touch',
        '3 things you can hear',
        '2 things you can smell',
        '1 thing you can taste',
      ],
      'fr': [
        'Regarde autour de toi et nomme 5 choses que tu vois',
        'Maintenant, 4 choses que tu peux toucher',
        '3 choses que tu peux entendre',
        '2 choses que tu peux sentir',
        '1 chose que tu peux goûter',
      ],
      'ar': [
        'انظر حولك وسمِّ 5 أشياء تراها',
        'الآن، 4 أشياء يمكنك لمسها',
        '3 أشياء يمكنك سماعها',
        '2 شيئين يمكنك شمهما',
        'شيء واحد يمكنك تذوقه',
      ],
      'de': [
        'Schau dich um und nenne 5 Dinge, die du siehst',
        'Jetzt, 4 Dinge, die du berühren kannst',
        '3 Dinge, die du hören kannst',
        '2 Dinge, die du riechen kannst',
        '1 Ding, das du schmecken kannst',
      ],
      'es': [
        'Mira a tu alrededor y nombra 5 cosas que ves',
        'Ahora, 4 cosas que puedes tocar',
        '3 cosas que puedes escuchar',
        '2 cosas que puedes oler',
        '1 cosa que puedes saborear',
      ],
    };
    return prompts[lang] ?? prompts['en']!;
  }
  
  String _getGroundingComplete(String lang) {
    const messages = {
      'en': "Well done. You've completed the grounding exercise. How are you feeling now?",
      'fr': "Bravo. Tu as terminé l'exercice d'ancrage. Comment te sens-tu maintenant?",
      'ar': "أحسنت. لقد أكملت تمرين التثبيت. كيف تشعر الآن؟",
      'de': "Gut gemacht. Du hast die Erdungsübung abgeschlossen. Wie fühlst du dich jetzt?",
      'es': "Bien hecho. Has completado el ejercicio de anclaje. ¿Cómo te sientes ahora?",
    };
    return messages[lang] ?? messages['en']!;
  }
  
  String _getCrisisIntro(String lang) {
    const messages = {
      'en': "Here is a crisis hotline you can call right now",
      'fr': "Voici une ligne de crise que tu peux appeler maintenant",
      'ar': "إليك خط أزمات يمكنك الاتصال به الآن",
      'de': "Hier ist eine Krisenhotline, die du jetzt anrufen kannst",
      'es': "Aquí hay una línea de crisis que puedes llamar ahora",
    };
    return messages[lang] ?? messages['en']!;
  }
  
  String _getHelpMessage(String lang) {
    const messages = {
      'en': "I can help you with breathing exercises, grounding, or connect you with crisis resources. What would you like?",
      'fr': "Je peux t'aider avec des exercices de respiration, d'ancrage, ou te connecter avec des ressources de crise. Que souhaites-tu?",
      'ar': "يمكنني مساعدتك في تمارين التنفس والتثبيت، أو ربطك بموارد الأزمات. ماذا تريد؟",
      'de': "Ich kann dir bei Atemübungen, Erdung helfen oder dich mit Krisenressourcen verbinden. Was möchtest du?",
      'es': "Puedo ayudarte con ejercicios de respiración, anclaje, o conectarte con recursos de crisis. ¿Qué te gustaría?",
    };
    return messages[lang] ?? messages['en']!;
  }
  
  @override
  Future<void> close() {
    _breathingTimer?.cancel();
    _stt.dispose();
    _tts.dispose();
    return super.close();
  }
}
