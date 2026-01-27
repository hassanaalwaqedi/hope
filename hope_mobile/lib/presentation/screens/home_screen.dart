/// HOPE Home Screen
/// 
/// Therapeutic, calming design for someone who may be in distress.
/// Every element is designed to reduce cognitive load and feel safe.
/// 
/// Design principles:
/// - ONE clear primary action (I need help)
/// - Calming colors and gentle animations
/// - Supportive messaging
/// - Easy access to crisis resources

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
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return BlocListener<PanicBloc, PanicSessionState>(
      listener: (context, state) {
        if (state.phase == PanicPhase.entering || state.phase == PanicPhase.active) {
          Navigator.of(context).push(
            PageRouteBuilder(
              pageBuilder: (_, __, ___) => const PanicActiveScreen(),
              transitionsBuilder: (_, animation, __, child) {
                return FadeTransition(opacity: animation, child: child);
              },
              transitionDuration: HopeAnimations.normal,
            ),
          );
        }
      },
      child: Scaffold(
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: isDark
                  ? [
                      HopeColors.charcoal,
                      HopeColors.charcoalLight,
                    ]
                  : [
                      HopeColors.cream,
                      HopeColors.warmWhite,
                    ],
            ),
          ),
          child: SafeArea(
            child: Stack(
              children: [
                // Subtle floating shapes - calming background
                _buildFloatingShapes(context, isDark),
                
                // Main content
                Padding(
                  padding: const EdgeInsets.all(HopeSpacing.lg),
                  child: Column(
                    children: [
                      const Spacer(flex: 1),
                      
                      // Welcoming header
                      _buildHeader(context),
                      
                      const Spacer(flex: 2),
                      
                      // Main panic button - breathing animation
                      const HopeButton(),
                      
                      const Spacer(flex: 2),
                      
                      // Supportive message
                      _buildSupportMessage(context, isDark),
                      
                      const SizedBox(height: HopeSpacing.xl),
                      
                      // Quick resources bar
                      _buildQuickResources(context, isDark),
                      
                      const SizedBox(height: HopeSpacing.md),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildFloatingShapes(BuildContext context, bool isDark) {
    return Positioned.fill(
      child: IgnorePointer(
        child: Stack(
          children: [
            Positioned(
              top: -50,
              right: -50,
              child: Container(
                width: 200,
                height: 200,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: (isDark ? HopeColors.nightSage : HopeColors.sage)
                      .withOpacity(0.05),
                ),
              ),
            ),
            Positioned(
              bottom: 100,
              left: -80,
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: (isDark ? HopeColors.teal : HopeColors.tealLight)
                      .withOpacity(0.04),
                ),
              ),
            ),
            Positioned(
              top: 200,
              right: -30,
              child: Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: (isDark ? HopeColors.amber : HopeColors.amberLight)
                      .withOpacity(0.05),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Column(
      children: [
        Text(
          'HOPE',
          style: Theme.of(context).textTheme.displayMedium?.copyWith(
                fontWeight: FontWeight.w700,
                letterSpacing: 6,
                color: Theme.of(context).colorScheme.primary,
              ),
        ),
        const SizedBox(height: HopeSpacing.sm),
        Text(
          'Je suis là pour toi',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).colorScheme.onSurface.withOpacity(0.7),
                fontWeight: FontWeight.w400,
              ),
        ),
      ],
    );
  }

  Widget _buildSupportMessage(BuildContext context, bool isDark) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: HopeSpacing.lg,
        vertical: HopeSpacing.md,
      ),
      decoration: BoxDecoration(
        color: (isDark ? HopeColors.onyx : HopeColors.surface)
            .withOpacity(isDark ? 0.6 : 0.8),
        borderRadius: BorderRadius.circular(HopeSpacing.radiusLg),
        border: Border.all(
          color: (isDark ? HopeColors.shadow : HopeColors.mist),
          width: 1,
        ),
      ),
      child: Text(
        'Prends ton temps. Tu n\'as rien à prouver.',
        textAlign: TextAlign.center,
        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontStyle: FontStyle.italic,
              color: Theme.of(context).colorScheme.onSurface.withOpacity(0.8),
            ),
      ),
    );
  }

  Widget _buildQuickResources(BuildContext context, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(HopeSpacing.md),
      decoration: BoxDecoration(
        color: (isDark ? HopeColors.onyx : HopeColors.surface),
        borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        boxShadow: HopeShadows.light,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _QuickActionButton(
            icon: Icons.air_rounded,
            label: 'Respirer',
            onTap: () {
              HapticFeedback.lightImpact();
              context.read<PanicBloc>().add(const PanicTriggered());
            },
          ),
          _QuickActionDivider(isDark: isDark),
          _QuickActionButton(
            icon: Icons.visibility_rounded,
            label: 'Ancrage',
            onTap: () {
              HapticFeedback.lightImpact();
              context.read<PanicBloc>().add(const PanicTriggered());
            },
          ),
          _QuickActionDivider(isDark: isDark),
          _QuickActionButton(
            icon: Icons.phone_rounded,
            label: '3114',
            isEmergency: true,
            onTap: () => _showCrisisResources(context),
          ),
        ],
      ),
    );
  }

  void _showCrisisResources(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (_) => _CrisisResourcesSheet(),
    );
  }
}

// ============================================================================
// HOPE BUTTON - Main interaction with breathing animation
// ============================================================================

class HopeButton extends StatefulWidget {
  const HopeButton({super.key});

  @override
  State<HopeButton> createState() => _HopeButtonState();
}

class _HopeButtonState extends State<HopeButton>
    with TickerProviderStateMixin {
  late AnimationController _breatheController;
  late AnimationController _glowController;
  late Animation<double> _breatheAnimation;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    
    // Breathing animation - slow, calming
    _breatheController = AnimationController(
      duration: HopeAnimations.breathe,
      vsync: this,
    )..repeat(reverse: true);
    
    _breatheAnimation = Tween<double>(begin: 1.0, end: 1.05).animate(
      CurvedAnimation(
        parent: _breatheController,
        curve: Curves.easeInOutSine,
      ),
    );
    
    // Glow animation - subtle pulse
    _glowController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    )..repeat(reverse: true);
    
    _glowAnimation = Tween<double>(begin: 0.3, end: 0.6).animate(
      CurvedAnimation(
        parent: _glowController,
        curve: Curves.easeInOutSine,
      ),
    );
  }

  @override
  void dispose() {
    _breatheController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final primaryColor = isDark ? HopeColors.nightSage : HopeColors.sage;
    
    return AnimatedBuilder(
      animation: Listenable.merge([_breatheAnimation, _glowAnimation]),
      builder: (context, child) {
        return Transform.scale(
          scale: _breatheAnimation.value,
          child: GestureDetector(
            onTap: () {
              HapticFeedback.mediumImpact();
              context.read<PanicBloc>().add(const PanicTriggered());
            },
            child: Container(
              width: HopeSpacing.panicButton,
              height: HopeSpacing.panicButton,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    primaryColor,
                    primaryColor.withOpacity(0.85),
                  ],
                  stops: const [0.5, 1.0],
                ),
                boxShadow: [
                  // Outer glow
                  BoxShadow(
                    color: primaryColor.withOpacity(_glowAnimation.value),
                    blurRadius: 40,
                    spreadRadius: 15,
                  ),
                  // Inner shadow
                  BoxShadow(
                    color: primaryColor.withOpacity(0.3),
                    blurRadius: 20,
                    spreadRadius: 5,
                  ),
                ],
              ),
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Heart icon with gentle pulse
                    Icon(
                      Icons.favorite_rounded,
                      color: Colors.white.withOpacity(0.95),
                      size: 36,
                    ),
                    const SizedBox(height: HopeSpacing.sm),
                    // Main text
                    Text(
                      'J\'ai besoin\nd\'aide',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontFamily: HopeTypography.fontFamily,
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: Colors.white,
                        height: 1.3,
                        letterSpacing: 0.3,
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

// ============================================================================
// QUICK ACTION BUTTON
// ============================================================================

class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool isEmergency;

  const _QuickActionButton({
    required this.icon,
    required this.label,
    required this.onTap,
    this.isEmergency = false,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final color = isEmergency
        ? (isDark ? HopeColors.coralLight : HopeColors.coral)
        : Theme.of(context).colorScheme.primary;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: HopeSpacing.md,
            vertical: HopeSpacing.sm,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 26,
                color: color,
              ),
              const SizedBox(height: HopeSpacing.xs),
              Text(
                label,
                style: Theme.of(context).textTheme.labelMedium?.copyWith(
                      color: color,
                      fontWeight: FontWeight.w500,
                    ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _QuickActionDivider extends StatelessWidget {
  final bool isDark;

  const _QuickActionDivider({required this.isDark});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 1,
      height: 40,
      color: isDark ? HopeColors.shadow : HopeColors.mist,
    );
  }
}

// ============================================================================
// CRISIS RESOURCES SHEET
// ============================================================================

class _CrisisResourcesSheet extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        color: isDark ? HopeColors.onyx : HopeColors.surface,
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(HopeSpacing.radiusXl),
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(HopeSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: isDark ? HopeColors.shadow : HopeColors.mist,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: HopeSpacing.lg),
              
              // Title
              Text(
                'Numéros d\'Urgence',
                style: Theme.of(context).textTheme.headlineSmall,
              ),
              const SizedBox(height: HopeSpacing.xs),
              Text(
                'Tu n\'es pas seul(e). De l\'aide est disponible.',
                style: Theme.of(context).textTheme.bodyMedium,
              ),
              const SizedBox(height: HopeSpacing.lg),
              
              // Emergency contacts
              _CrisisResourceTile(
                title: 'Prévention du Suicide',
                phone: '3114',
                description: 'Écoute professionnelle 24h/24',
                isPrimary: true,
              ),
              const SizedBox(height: HopeSpacing.md),
              _CrisisResourceTile(
                title: 'Urgences Européennes',
                phone: '112',
                description: 'Tous services d\'urgence',
              ),
              const SizedBox(height: HopeSpacing.md),
              _CrisisResourceTile(
                title: 'SOS Amitié',
                phone: '09 72 39 40 50',
                description: 'Écoute bienveillante 24h/24',
              ),
              
              const SizedBox(height: HopeSpacing.xl),
              
              // Safety message
              Container(
                padding: const EdgeInsets.all(HopeSpacing.md),
                decoration: BoxDecoration(
                  color: (isDark ? HopeColors.coralLight : HopeColors.coral)
                      .withOpacity(0.1),
                  borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
                  border: Border.all(
                    color: (isDark ? HopeColors.coralLight : HopeColors.coral)
                        .withOpacity(0.3),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline_rounded,
                      color: isDark ? HopeColors.coralLight : HopeColors.coral,
                      size: 20,
                    ),
                    const SizedBox(width: HopeSpacing.sm),
                    Expanded(
                      child: Text(
                        'En danger immédiat? Appelle le 15 (SAMU) ou 112',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: isDark
                                  ? HopeColors.coralLight
                                  : HopeColors.coral,
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: HopeSpacing.md),
            ],
          ),
        ),
      ),
    );
  }
}

class _CrisisResourceTile extends StatelessWidget {
  final String title;
  final String phone;
  final String description;
  final bool isPrimary;

  const _CrisisResourceTile({
    required this.title,
    required this.phone,
    required this.description,
    this.isPrimary = false,
  });

  Future<void> _callNumber(String number) async {
    final cleanNumber = number.replaceAll(' ', '');
    final uri = Uri.parse('tel:$cleanNumber');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => _callNumber(phone),
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        child: Container(
          padding: const EdgeInsets.all(HopeSpacing.md),
          decoration: BoxDecoration(
            color: isPrimary
                ? (isDark ? HopeColors.nightSage : HopeColors.sage)
                    .withOpacity(0.1)
                : (isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated),
            borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
            border: isPrimary
                ? Border.all(
                    color: (isDark ? HopeColors.nightSage : HopeColors.sage)
                        .withOpacity(0.3),
                  )
                : null,
          ),
          child: Row(
            children: [
              // Phone icon
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: (isDark ? HopeColors.nightSage : HopeColors.sage)
                      .withOpacity(isPrimary ? 0.2 : 0.1),
                  borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                ),
                child: Icon(
                  Icons.phone_rounded,
                  color: isDark ? HopeColors.nightSage : HopeColors.sage,
                  size: 22,
                ),
              ),
              const SizedBox(width: HopeSpacing.md),
              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      description,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              // Phone number
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: HopeSpacing.sm,
                  vertical: HopeSpacing.xs,
                ),
                decoration: BoxDecoration(
                  color: (isDark ? HopeColors.success : HopeColors.success)
                      .withOpacity(0.15),
                  borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                ),
                child: Text(
                  phone,
                  style: Theme.of(context).textTheme.labelMedium?.copyWith(
                        color: HopeColors.success,
                        fontWeight: FontWeight.w600,
                      ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
