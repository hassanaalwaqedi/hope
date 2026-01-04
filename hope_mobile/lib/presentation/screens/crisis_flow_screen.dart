/// Crisis Flow Screen for Critical Panic
/// 
/// PRODUCTION: Real French crisis resources.
/// Primary: France | Fallback: European 112
/// 
/// Emphasizes human resources and support options.
/// Large tap targets, clear messaging, emergency contact options.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/theme/app_theme.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../panic/ux/panic_analytics.dart';
import '../../panic/ux/panic_state_classifier.dart';

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
  
  @override
  void initState() {
    super.initState();
    _analytics.logCrisisFlowEntered(
      fromState: PanicUXState.CRITICAL_PANIC,
      trigger: 'automatic_routing',
    );
  }

  @override
  Widget build(BuildContext context) {
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
                const SizedBox(height: 40),
                
                // Main message
                const Icon(
                  Icons.favorite,
                  color: Colors.white,
                  size: 48,
                ),
                const SizedBox(height: 24),
                const Text(
                  "Tu n'es pas seul(e)",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w300,
                    color: Colors.white,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 12),
                Text(
                  "Je suis là avec toi.\nTu comptes, et de l'aide est disponible.",
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.white.withOpacity(0.7),
                    height: 1.5,
                  ),
                ),
                
                const SizedBox(height: 48),
                
                // REAL French crisis resources
                _buildCrisisCard(
                  icon: Icons.phone,
                  title: 'Numéro National de Prévention du Suicide',
                  subtitle: 'Appeler le 3114 (24h/24, gratuit)',
                  onTap: () => _handleCrisisCall('3114'),
                  primary: true,
                ),
                const SizedBox(height: 12),
                _buildCrisisCard(
                  icon: Icons.local_hospital,
                  title: 'Urgences Européennes',
                  subtitle: 'Appeler le 112',
                  onTap: () => _handleCrisisCall('112'),
                ),
                const SizedBox(height: 12),
                _buildCrisisCard(
                  icon: Icons.medical_services,
                  title: 'SAMU',
                  subtitle: 'Appeler le 15',
                  onTap: () => _handleCrisisCall('15'),
                ),
                const SizedBox(height: 12),
                _buildCrisisCard(
                  icon: Icons.favorite_border,
                  title: 'SOS Amitié',
                  subtitle: '09 72 39 40 50 (24h/24)',
                  onTap: () => _handleCrisisCall('0972394050'),
                ),
                
                const SizedBox(height: 32),
                
                // Divider
                Row(
                  children: [
                    Expanded(child: Divider(color: Colors.white.withOpacity(0.2))),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'ou',
                        style: TextStyle(color: Colors.white.withOpacity(0.5)),
                      ),
                    ),
                    Expanded(child: Divider(color: Colors.white.withOpacity(0.2))),
                  ],
                ),
                
                const SizedBox(height: 32),
                
                // Continue with app option
                if (widget.config['allowExerciseFallback'] as bool? ?? true) ...[
                  Text(
                    "Si tu préfères, nous pouvons essayer des exercices de calme ensemble.",
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
                        label: const Text('Essayer des exercices de respiration'),
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(color: Colors.white.withOpacity(0.3)),
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          foregroundColor: Colors.white70,
                        ),
                      ),
                    ),
                  ] else ...[
                    _buildExerciseOptions(),
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
                    'HOPE est un outil de soutien, pas un remplacement pour une aide professionnelle. '
                    'Si vous êtes en danger immédiat, contactez les services d\'urgence au 15 ou 112.',
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

  Widget _buildExerciseOptions() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: _buildExerciseButton(
                icon: Icons.air,
                label: 'Respirer',
                onTap: () => _startExercise('breathing'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildExerciseButton(
                icon: Icons.visibility,
                label: 'Ancrage',
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
              "J'ai juste besoin que quelqu'un soit avec moi",
              style: TextStyle(color: Colors.white.withOpacity(0.6)),
            ),
          ),
        ),
      ],
    );
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
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Appel du $number...'),
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
