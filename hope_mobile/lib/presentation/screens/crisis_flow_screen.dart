/// Crisis Flow Screen for Critical Panic
/// 
/// PRODUCTION: Dynamic country-aware crisis resources from backend.
/// Fetches resources based on user's country setting.
/// 
/// IMPORTANT: Explicitly clarifies AI-only support - no human escalation.
/// Large tap targets, clear messaging, emergency contact options.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:dio/dio.dart';
import '../../core/theme/app_theme.dart';
import '../../core/theme/hope_icons.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../panic/ux/panic_analytics.dart';
import '../../panic/ux/panic_state_classifier.dart';
import '../../l10n/generated/app_localizations.dart';

/// Crisis resource model fetched from backend
class CrisisResource {
  final String name;
  final String type;
  final String contact;
  final String description;
  final bool available247;
  
  CrisisResource({
    required this.name,
    required this.type,
    required this.contact,
    required this.description,
    required this.available247,
  });
  
  factory CrisisResource.fromJson(Map<String, dynamic> json) {
    return CrisisResource(
      name: json['name'] ?? '',
      type: json['type'] ?? 'hotline',
      contact: json['contact'] ?? '',
      description: json['description'] ?? '',
      available247: json['available_24_7'] ?? false,
    );
  }
}

class CrisisFlowScreen extends StatefulWidget {
  final Map<String, dynamic> config;
  
  const CrisisFlowScreen({
    super.key,
    this.config = const {},
  });

  @override
  State<CrisisFlowScreen> createState() => _CrisisFlowScreenState();
}

class _CrisisFlowScreenState extends State<CrisisFlowScreen> {
  final _analytics = PanicAnalytics.instance;
  bool _acknowledged = false;
  bool _loading = true;
  String _emergencyNumber = '112';  // European default
  String _countryName = '';
  List<CrisisResource> _resources = [];
  String? _error;
  
  @override
  void initState() {
    super.initState();
    _analytics.logCrisisFlowEntered(
      fromState: PanicUXState.CRITICAL_PANIC,
      trigger: 'automatic_routing',
    );
    _loadCrisisResources();
  }
  
  Future<void> _loadCrisisResources() async {
    try {
      final dio = Dio(BaseOptions(
        baseUrl: 'http://10.0.2.2:8000',  // Android emulator localhost
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 5),
      ));
      
      // Get country code from config or default to user's locale
      final countryCode = widget.config['countryCode'] as String? ?? 
          WidgetsBinding.instance.platformDispatcher.locale.countryCode ?? 'US';
      final language = WidgetsBinding.instance.platformDispatcher.locale.languageCode;
      
      final response = await dio.post('/api/v1/resources/crisis', data: {
        'country_code': countryCode,
        'language': language,
      });
      
      if (response.statusCode == 200 && response.data != null) {
        final data = response.data as Map<String, dynamic>;
        setState(() {
          _emergencyNumber = data['emergency_number'] ?? '112';
          _countryName = data['country_name'] ?? '';
          _resources = (data['resources'] as List<dynamic>?)
              ?.map((r) => CrisisResource.fromJson(r as Map<String, dynamic>))
              .toList() ?? [];
          _loading = false;
        });
      } else {
        _useFallbackResources();
      }
    } catch (e) {
      // Use fallback resources on network error
      _useFallbackResources();
    }
  }
  
  void _useFallbackResources() {
    // Fallback to European emergency (112)
    setState(() {
      _emergencyNumber = '112';
      _countryName = 'Europe';
      _resources = [
        CrisisResource(
          name: 'Emergency Services',
          type: 'hotline',
          contact: '112',
          description: 'European Emergency Number',
          available247: true,
        ),
      ];
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        // Block back navigation in crisis flow
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF1A1A2E),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 20),
                
                // AI-ONLY NOTICE - CRITICAL FOR HUMAN ESCALATION CLARITY
                _buildAiOnlyNotice(l10n),
                
                const SizedBox(height: 24),
                
                // Main message
                HopeIcons.butterfly(
                  size: 48,
                  color: Colors.white,
                ),
                const SizedBox(height: 16),
                Text(
                  _getLocalizedTitle(l10n),
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w300,
                    color: Colors.white,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  l10n.chatWelcome,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white.withOpacity(0.7),
                    height: 1.5,
                  ),
                ),
                
                const SizedBox(height: 32),
                
                // Crisis resources from backend
                if (_loading)
                  const Center(
                    child: CircularProgressIndicator(color: Colors.white70),
                  )
                else if (_error != null)
                  _buildErrorCard()
                else ...[
                  // Emergency number first
                  _buildCrisisCard(
                    icon: Icons.local_hospital,
                    title: l10n.crisisEmergency(_emergencyNumber),
                    subtitle: l10n.crisisAvailable247,
                    onTap: () => _handleCrisisCall(_emergencyNumber),
                    primary: true,
                  ),
                  
                  const SizedBox(height: 12),
                  
                  // Dynamic resources from backend
                  ..._resources.map((resource) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: _buildCrisisCard(
                      icon: _getResourceIcon(resource.type),
                      title: resource.name,
                      subtitle: resource.contact + 
                          (resource.available247 ? ' (${l10n.crisisAvailable247})' : ''),
                      onTap: () => _handleCrisisCall(
                        resource.contact.replaceAll(RegExp(r'[^0-9+]'), ''),
                      ),
                    ),
                  )),
                ],
                
                const SizedBox(height: 24),
                
                // Divider with "or"
                Row(
                  children: [
                    Expanded(child: Divider(color: Colors.white.withOpacity(0.2))),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        _getLocalizedOr(),
                        style: TextStyle(color: Colors.white.withOpacity(0.5)),
                      ),
                    ),
                    Expanded(child: Divider(color: Colors.white.withOpacity(0.2))),
                  ],
                ),
                
                const SizedBox(height: 24),
                
                // Continue with app option
                if (widget.config['allowExerciseFallback'] as bool? ?? true) ...[
                  Text(
                    _getLocalizedExercisePrompt(),
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white.withOpacity(0.6),
                    ),
                  ),
                  const SizedBox(height: 16),
                  
                  if (!_acknowledged) ...[
                    SizedBox(
                      width: double.infinity,
                      child: OutlinedButton.icon(
                        onPressed: _acknowledgeAndContinue,
                        icon: const Icon(Icons.air),
                        label: Text(l10n.breathingTitle),
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(color: Colors.white.withOpacity(0.3)),
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          foregroundColor: Colors.white70,
                        ),
                      ),
                    ),
                  ] else ...[
                    _buildExerciseOptions(l10n),
                  ],
                ],
                
                const SizedBox(height: 32),
                
                // Disclaimer
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.05),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    l10n.humanSupportNotice,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white.withOpacity(0.5),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// CRITICAL: AI-Only notice banner - makes it clear no human is available
  Widget _buildAiOnlyNotice(AppLocalizations l10n) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.orange.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.smart_toy_outlined,
            color: Colors.orange,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              l10n.aiOnlyDisclaimer,
              style: const TextStyle(
                fontSize: 13,
                color: Colors.orange,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard() {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            l10n.errorNetwork,
            style: const TextStyle(color: Colors.white70),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 12),
          OutlinedButton(
            onPressed: () {
              setState(() => _loading = true);
              _loadCrisisResources();
            },
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.white70,
              side: const BorderSide(color: Colors.white30),
            ),
            child: Text(l10n.retry),
          ),
        ],
      ),
    );
  }

  IconData _getResourceIcon(String type) {
    switch (type) {
      case 'text':
        return Icons.message;
      case 'chat':
        return Icons.chat;
      case 'website':
        return Icons.language;
      default:
        return Icons.phone;
    }
  }

  String _getLocalizedTitle(AppLocalizations l10n) {
    final locale = Localizations.localeOf(context).languageCode;
    switch (locale) {
      case 'fr':
        return "Tu n'es pas seul(e)";
      case 'ar':
        return "أنت لست وحدك";
      case 'de':
        return "Du bist nicht allein";
      case 'es':
        return "No estás solo/a";
      default:
        return "You're not alone";
    }
  }

  String _getLocalizedOr() {
    final locale = Localizations.localeOf(context).languageCode;
    switch (locale) {
      case 'fr':
        return 'ou';
      case 'ar':
        return 'أو';
      case 'de':
        return 'oder';
      case 'es':
        return 'o';
      default:
        return 'or';
    }
  }

  String _getLocalizedExercisePrompt() {
    final locale = Localizations.localeOf(context).languageCode;
    switch (locale) {
      case 'fr':
        return "Si tu préfères, nous pouvons essayer des exercices de calme ensemble.";
      case 'ar':
        return "إذا كنت تفضل، يمكننا تجربة تمارين الاسترخاء معًا.";
      case 'de':
        return "Wenn du möchtest, können wir gemeinsam Entspannungsübungen machen.";
      case 'es':
        return "Si lo prefieres, podemos probar ejercicios de relajación juntos.";
      default:
        return "If you prefer, we can try calming exercises together.";
    }
  }

  Widget _buildCrisisCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
    bool primary = false,
  }) {
    return Material(
      color: primary 
          ? AppTheme.crisisColor.withOpacity(0.2)
          : Colors.white.withOpacity(0.05),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: () {
          HapticFeedback.mediumImpact();
          onTap();
        },
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: primary 
                      ? AppTheme.crisisColor 
                      : Colors.white.withOpacity(0.1),
                ),
                child: Icon(
                  icon,
                  color: primary ? Colors.white : Colors.white70,
                  size: 28,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: primary ? Colors.white : Colors.white70,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      style: TextStyle(
                        fontSize: 14,
                        color: primary 
                            ? Colors.white.withOpacity(0.8)
                            : Colors.white.withOpacity(0.5),
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.call,
                color: primary ? Colors.white : Colors.white.withOpacity(0.3),
                size: 24,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildExerciseOptions(AppLocalizations l10n) {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildExerciseButton(
                icon: Icons.air,
                label: l10n.breatheIn.split(' ').first, // "Breathe"
                onTap: () => _startExercise('breathing'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildExerciseButton(
                icon: Icons.visibility,
                label: l10n.groundingTitle.split(' ').first, // "Grounding"
                onTap: () => _startExercise('grounding'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: TextButton(
            onPressed: () {
              context.read<PanicBloc>().add(const ExerciseTransitionRequested(
                fromExercise: 'crisis',
                toExercise: 'hold',
              ));
            },
            child: Text(
              _getLocalizedCompanionText(),
              style: TextStyle(color: Colors.white.withOpacity(0.6)),
            ),
          ),
        ),
      ],
    );
  }

  String _getLocalizedCompanionText() {
    final locale = Localizations.localeOf(context).languageCode;
    switch (locale) {
      case 'fr':
        return "J'ai juste besoin que quelqu'un soit avec moi";
      case 'ar':
        return "أحتاج فقط أن يكون شخص ما معي";
      case 'de':
        return "Ich brauche nur jemanden, der bei mir ist";
      case 'es':
        return "Solo necesito que alguien esté conmigo";
      default:
        return "I just need someone to be with me";
    }
  }

  Widget _buildExerciseButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return OutlinedButton.icon(
      onPressed: onTap,
      icon: Icon(icon),
      label: Text(label),
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: Colors.white.withOpacity(0.3)),
        padding: const EdgeInsets.symmetric(vertical: 16),
        foregroundColor: Colors.white70,
      ),
    );
  }

  Future<void> _handleCrisisCall(String number) async {
    _analytics.logCrisisResourceUsed(resource: number);
    
    final uri = Uri.parse('tel:$number');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (mounted) {
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${l10n.crisisCall}: $number'),
            backgroundColor: AppTheme.crisisColor,
          ),
        );
      }
    }
  }

  void _acknowledgeAndContinue() {
    HapticFeedback.lightImpact();
    setState(() => _acknowledged = true);
  }

  void _startExercise(String exerciseType) {
    HapticFeedback.mediumImpact();
    _analytics.logExerciseTransition(
      fromExercise: 'crisis',
      toExercise: exerciseType,
      durationMs: 0,
      wasAutomatic: false,
    );
    context.read<PanicBloc>().add(ExerciseTransitionRequested(
      fromExercise: 'crisis',
      toExercise: exerciseType,
    ));
  }
}
