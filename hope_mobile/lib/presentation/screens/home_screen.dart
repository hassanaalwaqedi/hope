/// Enhanced Home Screen with better layout and animations
/// PRODUCTION: Real French crisis resources
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../panic/bloc/panic_bloc.dart';
import '../../panic/panic_state.dart';
import '../../core/theme/app_theme.dart';
import 'panic_active_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocListener<PanicBloc, PanicSessionState>(
      listener: (context, state) {
        if (state.phase == PanicPhase.entering || state.phase == PanicPhase.active) {
          Navigator.of(context).push(
            PageRouteBuilder(
              pageBuilder: (_, __, ___) => const PanicActiveScreen(),
              transitionsBuilder: (_, animation, __, child) {
                return FadeTransition(opacity: animation, child: child);
              },
              transitionDuration: const Duration(milliseconds: 400),
            ),
          );
        }
      },
      child: Scaffold(
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Theme.of(context).scaffoldBackgroundColor,
                Theme.of(context).scaffoldBackgroundColor.withBlue(
                  (Theme.of(context).scaffoldBackgroundColor.blue * 1.1).clamp(0, 255).toInt(),
                ),
              ],
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  const Spacer(flex: 2),
                  
                  // Logo/Title
                  Column(
                    children: [
                      Text(
                        'HOPE',
                        style: Theme.of(context).textTheme.displaySmall?.copyWith(
                          fontWeight: FontWeight.w700,
                          letterSpacing: 8,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Tu n\'es pas seul(e)',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          color: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
                          fontWeight: FontWeight.w400,
                        ),
                      ),
                    ],
                  ),
                  
                  const Spacer(flex: 2),
                  
                  // Main panic button
                  const PanicEntryButton(),
                  
                  const Spacer(),
                  
                  // Quick resources
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surface.withOpacity(0.5),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _buildQuickAction(
                          context,
                          icon: Icons.air,
                          label: 'Respirer',
                          onTap: () {
                            HapticFeedback.lightImpact();
                            context.read<PanicBloc>().add(const PanicTriggered());
                          },
                        ),
                        _buildQuickAction(
                          context,
                          icon: Icons.remove_red_eye_outlined,
                          label: 'Ancrage',
                          onTap: () {
                            HapticFeedback.lightImpact();
                            context.read<PanicBloc>().add(const PanicTriggered());
                          },
                        ),
                        _buildQuickAction(
                          context,
                          icon: Icons.phone,
                          label: '3114',
                          onTap: () => _showCrisisResources(context),
                        ),
                      ],
                    ),
                  ),
                  
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuickAction(
    BuildContext context, {
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 28, color: AppTheme.panicAccent),
            const SizedBox(height: 4),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }

  void _showCrisisResources(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Colors.grey[400],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text(
              'Numéros d\'Urgence',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            _buildResourceTile(
              context,
              title: 'Prévention du Suicide',
              phone: '3114',
              available: '24h/24',
              onTap: () => _callNumber('3114'),
            ),
            _buildResourceTile(
              context,
              title: 'Urgences Européennes',
              phone: '112',
              available: '24h/24',
              onTap: () => _callNumber('112'),
            ),
            _buildResourceTile(
              context,
              title: 'SOS Amitié',
              phone: '09 72 39 40 50',
              available: '24h/24',
              onTap: () => _callNumber('0972394050'),
            ),
            const SizedBox(height: 16),
            Text(
              'Si vous êtes en danger immédiat, appelez le 15 (SAMU) ou le 112.',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Future<void> _callNumber(String number) async {
    final uri = Uri.parse('tel:$number');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  Widget _buildResourceTile(
    BuildContext context, {
    required String title,
    required String phone,
    required String available,
    VoidCallback? onTap,
  }) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(title),
      subtitle: Text(phone),
      trailing: Chip(
        label: Text(available),
        backgroundColor: AppTheme.calmColor.withOpacity(0.1),
        side: BorderSide.none,
        labelStyle: TextStyle(color: AppTheme.calmColor, fontSize: 12),
      ),
      onTap: onTap,
    );
  }
}

class PanicEntryButton extends StatefulWidget {
  const PanicEntryButton({super.key});

  @override
  State<PanicEntryButton> createState() => _PanicEntryButtonState();
}

class _PanicEntryButtonState extends State<PanicEntryButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);
    
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.1).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _pulseAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _pulseAnimation.value,
          child: GestureDetector(
            onTap: () {
              HapticFeedback.heavyImpact();
              context.read<PanicBloc>().add(const PanicTriggered());
            },
            child: Container(
              width: PanicUiConstants.panicButtonSize,
              height: PanicUiConstants.panicButtonSize,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppTheme.panicAccent,
                    AppTheme.panicAccent.withOpacity(0.8),
                  ],
                ),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.panicAccent.withOpacity(0.4),
                    blurRadius: 30,
                    spreadRadius: 10,
                  ),
                ],
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(
                      Icons.favorite,
                      color: Colors.white,
                      size: 32,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'J\'ai besoin\nd\'aide',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: Colors.white,
                        fontWeight: FontWeight.w600,
                        height: 1.2,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
