/// HOPE Settings Screen - Therapeutic Design
/// 
/// Production-grade settings with calming, professional design.
/// All settings are REAL, PERSISTED, and APPLIED.
/// 
/// Design principles:
/// - Grouped sections for clarity
/// - Warm, consistent styling
/// - Accessible touch targets
/// - Professional appearance

import 'package:flutter/material.dart';
import '../../l10n/generated/app_localizations.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:share_plus/share_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';

import '../../core/theme/app_theme.dart';
import '../../core/theme/hope_icons.dart';
import '../../core/settings/settings_service.dart';
import '../../core/settings/settings_bloc.dart';
import '../../core/settings/legal_documents.dart';
import '../../main.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  PackageInfo? _packageInfo;
  
  @override
  void initState() {
    super.initState();
    _loadPackageInfo();
  }
  
  Future<void> _loadPackageInfo() async {
    try {
      final info = await PackageInfo.fromPlatform();
      setState(() => _packageInfo = info);
    } catch (e) {
      debugPrint('Failed to load package info: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return BlocConsumer<SettingsBloc, SettingsState>(
      listener: (context, state) {
        if (state.exportFilePath != null) {
          _showExportSuccessDialog(context, state.exportFilePath!);
        }
        
        if (state.deletionComplete) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(AppLocalizations.of(context)!.done),
              backgroundColor: HopeColors.success,
              behavior: SnackBarBehavior.floating,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
              ),
            ),
          );
        }
        
        if (state.status == SettingsStatus.error && state.errorMessage != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(state.errorMessage!),
              backgroundColor: HopeColors.coral,
              behavior: SnackBarBehavior.floating,
            ),
          );
        }
      },
      builder: (context, state) {
        final settings = state.settings;
        final l10n = AppLocalizations.of(context)!;
        final isLoading = state.status == SettingsStatus.saving ||
                         state.status == SettingsStatus.exporting ||
                         state.status == SettingsStatus.deleting;
        
        return Scaffold(
          backgroundColor: isDark ? HopeColors.charcoal : HopeColors.cream,
          appBar: AppBar(
            title: Text(l10n.settingsTitle),
            centerTitle: true,
            actions: [
              if (isLoading)
                Padding(
                  padding: const EdgeInsets.all(HopeSpacing.md),
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ),
            ],
          ),
          body: ListView(
            padding: const EdgeInsets.all(HopeSpacing.md),
            children: [
              // Profile section
              _buildProfileCard(context, isDark),
              
              const SizedBox(height: HopeSpacing.lg),
              
              // Panic settings
              _SettingsSection(
                title: l10n.settingsPanicMode,
                iconWidget: HopeIcons.butterfly(size: 18),
                isDark: isDark,
                children: [
                  _SwitchTile(
                    title: l10n.settingsVoiceGuidance,
                    subtitle: l10n.settingsVoiceGuidanceSubtitle,
                    icon: Icons.volume_up_rounded,
                    value: settings.voiceGuidance,
                    onChanged: (v) => context.read<SettingsBloc>().add(VoiceGuidanceToggled(v)),
                    isDark: isDark,
                  ),
                  _SwitchTile(
                    title: l10n.settingsHaptic,
                    subtitle: l10n.settingsHapticSubtitle,
                    icon: Icons.vibration_rounded,
                    value: settings.hapticFeedback,
                    onChanged: (v) => context.read<SettingsBloc>().add(HapticFeedbackToggled(v)),
                    isDark: isDark,
                  ),
                  _DropdownTile(
                    title: l10n.settingsBreathingSpeed,
                    subtitle: l10n.settingsBreathingSpeedSubtitle,
                    icon: Icons.speed_rounded,
                    value: settings.breathingSpeed,
                    options: const ['slow', 'normal', 'fast'],
                    displayNames: {'slow': l10n.settingsSpeedSlow, 'normal': l10n.settingsSpeedNormal, 'fast': l10n.settingsSpeedFast},
                    onChanged: (v) => context.read<SettingsBloc>().add(BreathingSpeedChanged(v!)),
                    isDark: isDark,
                  ),
                ],
              ),
              
              const SizedBox(height: HopeSpacing.md),
              
              // Notifications
              _SettingsSection(
                title: l10n.settingsNotifications,
                icon: Icons.notifications_rounded,
                isDark: isDark,
                children: [
                  _SwitchTile(
                    title: l10n.settingsDailyCheckIn,
                    subtitle: l10n.settingsDailyCheckInSubtitle,
                    icon: Icons.calendar_today_rounded,
                    value: settings.dailyCheckIn,
                    onChanged: (v) => context.read<SettingsBloc>().add(DailyCheckInToggled(v)),
                    isDark: isDark,
                  ),
                ],
              ),
              
              const SizedBox(height: HopeSpacing.md),
              
              // Appearance
              _SettingsSection(
                title: l10n.settingsAppearance,
                icon: Icons.palette_rounded,
                isDark: isDark,
                children: [
                  _ThemeTile(
                    preference: settings.themePreference,
                    isDark: isDark,
                    onChanged: (newPref) {
                      context.read<SettingsBloc>().add(ThemePreferenceChanged(newPref));
                      HopeApp.setThemeMode(context, 
                        newPref == ThemePreference.dark ? ThemeMode.dark :
                        newPref == ThemePreference.light ? ThemeMode.light :
                        ThemeMode.system
                      );
                    },
                  ),
                ],
              ),
              
              const SizedBox(height: HopeSpacing.md),
              
              // Language
              _SettingsSection(
                title: l10n.settingsLanguage,
                icon: Icons.translate_rounded,
                isDark: isDark,
                children: [
                  _DropdownTile(
                    title: l10n.settingsLanguage,
                    subtitle: l10n.settingsLanguage,
                    icon: Icons.language_rounded,
                    value: settingsService.settings.languageCode ?? 'en',
                    options: const ['en', 'fr', 'ar', 'de', 'it', 'ko'],
                    displayNames: const {
                      'en': '🇬🇧 English',
                      'fr': '🇫🇷 Français',
                      'ar': '🇸🇦 العربية',
                      'de': '🇩🇪 Deutsch',
                      'it': '🇮🇹 Italiano',
                      'ko': '🇰🇷 한국어',
                    },
                    onChanged: (v) {
                      if (v != null) {
                        HopeApp.setLocale(context, Locale(v));
                      }
                    },
                    isDark: isDark,
                  ),
                ],
              ),
              
              const SizedBox(height: HopeSpacing.md),
              
              // Data & Privacy
              _SettingsSection(
                title: l10n.settingsDataPrivacy,
                icon: Icons.shield_rounded,
                isDark: isDark,
                children: [
                  _ActionTile(
                    title: l10n.settingsExportData,
                    subtitle: l10n.settingsExportDataSubtitle,
                    icon: Icons.download_rounded,
                    onTap: () => _showExportConfirmDialog(context, isDark),
                    isLoading: state.status == SettingsStatus.exporting,
                    isDark: isDark,
                  ),
                  _ActionTile(
                    title: l10n.settingsClearData,
                    subtitle: l10n.settingsClearDataSubtitle,
                    icon: Icons.delete_outline_rounded,
                    onTap: () => _showClearDataDialog(context, isDark),
                    isDestructive: true,
                    isLoading: state.status == SettingsStatus.deleting,
                    isDark: isDark,
                  ),
                  _ActionTile(
                    title: l10n.settingsPrivacyPolicy,
                    subtitle: 'Version ${LegalDocuments.privacyPolicyVersion}',
                    icon: Icons.privacy_tip_rounded,
                    onTap: () => _showLegalDocument(context, LegalDocuments.privacyPolicy, isDark),
                    isDark: isDark,
                  ),
                ],
              ),
              
              const SizedBox(height: HopeSpacing.md),
              
              // About
              _SettingsSection(
                title: l10n.settingsAbout,
                icon: Icons.info_rounded,
                isDark: isDark,
                children: [
                  _ActionTile(
                    title: l10n.settingsAboutApp,
                    subtitle: _packageInfo != null 
                        ? 'Version ${_packageInfo!.version} (${_packageInfo!.buildNumber})'
                        : 'Version 1.0.0',
                    iconWidget: HopeIcons.butterfly(size: 20),
                    onTap: () => _showAboutDialog(context, isDark),
                    isDark: isDark,
                  ),
                  _ActionTile(
                    title: l10n.settingsTerms,
                    subtitle: 'Version ${LegalDocuments.termsVersion}',
                    icon: Icons.description_rounded,
                    onTap: () => _showLegalDocument(context, LegalDocuments.termsOfService, isDark),
                    isDark: isDark,
                  ),
                  _ActionTile(
                    title: l10n.settingsFeedback,
                    subtitle: l10n.settingsFeedbackSubtitle,
                    icon: Icons.feedback_rounded,
                    onTap: () => _showFeedbackDialog(context, isDark),
                    isDark: isDark,
                  ),
                ],
              ),
              
              const SizedBox(height: HopeSpacing.xl),
              
              // Disclaimer
              _buildDisclaimer(context, isDark),
              
              const SizedBox(height: HopeSpacing.lg),
            ],
          ),
        );
      },
    );
  }

  Widget _buildProfileCard(BuildContext context, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(HopeSpacing.lg),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: isDark
              ? [HopeColors.nightSage.withOpacity(0.2), HopeColors.onyx]
              : [HopeColors.sage.withOpacity(0.15), HopeColors.surface],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        boxShadow: HopeShadows.light,
      ),
      child: Row(
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
            ),
            child: const Icon(Icons.person_rounded, color: Colors.white, size: 28),
          ),
          const SizedBox(width: HopeSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  AppLocalizations.of(context)!.settingsWelcome,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  AppLocalizations.of(context)!.settingsAnonymous,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
              ],
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: (isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated),
              borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
            ),
            child: IconButton(
              icon: const Icon(Icons.login_rounded),
              tooltip: AppLocalizations.of(context)!.settingsLoginSoon,
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(AppLocalizations.of(context)!.settingsLoginSoon),
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDisclaimer(BuildContext context, bool isDark) {
    return Container(
      padding: const EdgeInsets.all(HopeSpacing.md),
      decoration: BoxDecoration(
        color: (isDark ? HopeColors.amber : HopeColors.amber).withOpacity(0.1),
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        border: Border.all(
          color: HopeColors.amber.withOpacity(0.3),
        ),
      ),
      child: Column(
        children: [
          Icon(Icons.smart_toy_rounded, color: HopeColors.amber, size: 24),
          const SizedBox(height: HopeSpacing.sm),
          Text(
            AppLocalizations.of(context)!.aiOnlyDisclaimer,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: isDark ? HopeColors.moonlightDim : HopeColors.slateLight,
            ),
          ),
        ],
      ),
    );
  }

  void _showExportConfirmDialog(BuildContext context, bool isDark) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: isDark ? HopeColors.onyx : HopeColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        title: Text(AppLocalizations.of(context)!.settingsExportConfirm),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Ce fichier contiendra:', style: Theme.of(context).textTheme.bodyMedium),
            const SizedBox(height: HopeSpacing.sm),
            _buildBulletPoint(context, 'Historique des conversations'),
            _buildBulletPoint(context, 'Sessions de panique'),
            _buildBulletPoint(context, 'Tes réglages'),
            const SizedBox(height: HopeSpacing.md),
            Text(
              'Aucune donnée système n\'est incluse.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(AppLocalizations.of(context)!.settingsCancel),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<SettingsBloc>().add(const DataExportRequested());
            },
            child: Text(AppLocalizations.of(context)!.settingsExportAction),
          ),
        ],
      ),
    );
  }

  Widget _buildBulletPoint(BuildContext context, String text) {
    return Padding(
      padding: const EdgeInsets.only(left: HopeSpacing.sm, bottom: HopeSpacing.xs),
      child: Row(
        children: [
          Container(
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.primary,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: HopeSpacing.sm),
          Text(text, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }

  void _showExportSuccessDialog(BuildContext context, String filePath) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: isDark ? HopeColors.onyx : HopeColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        icon: Icon(Icons.check_circle_rounded, color: HopeColors.success, size: 48),
        title: Text(AppLocalizations.of(context)!.done),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(AppLocalizations.of(context)!.settingsExportDataSubtitle),
            const SizedBox(height: HopeSpacing.md),
            Container(
              padding: const EdgeInsets.all(HopeSpacing.sm),
              decoration: BoxDecoration(
                color: (isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated),
                borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
              ),
              child: Text(
                filePath.split('/').last,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(AppLocalizations.of(context)!.done),
          ),
          FilledButton.icon(
            onPressed: () {
              Navigator.pop(context);
              Share.shareXFiles([XFile(filePath)], text: 'HOPE Data Export');
            },
            icon: const Icon(Icons.share_rounded, size: 18),
            label: const Text('Partager'),
          ),
        ],
      ),
    );
  }

  void _showClearDataDialog(BuildContext context, bool isDark) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: isDark ? HopeColors.onyx : HopeColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        icon: Icon(Icons.warning_rounded, color: HopeColors.coral, size: 48),
        title: Text(AppLocalizations.of(context)!.settingsClearConfirm),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Cette action supprimera définitivement:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: HopeSpacing.sm),
            _buildBulletPoint(context, 'Tout l\'historique de chat'),
            _buildBulletPoint(context, 'Toutes les sessions de panique'),
            _buildBulletPoint(context, 'Tous les réglages'),
            const SizedBox(height: HopeSpacing.md),
            Container(
              padding: const EdgeInsets.all(HopeSpacing.sm),
              decoration: BoxDecoration(
                color: HopeColors.coral.withOpacity(0.1),
                borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
              ),
              child: Row(
                children: [
                  Icon(Icons.warning_rounded, color: HopeColors.coral, size: 18),
                  const SizedBox(width: HopeSpacing.sm),
                  Expanded(
                    child: Text(
                      AppLocalizations.of(context)!.settingsIrreversible,
                      style: TextStyle(
                        color: HopeColors.coral,
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(AppLocalizations.of(context)!.settingsCancel),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: HopeColors.coral),
            onPressed: () {
              Navigator.pop(context);
              context.read<SettingsBloc>().add(const DataDeletionRequested());
            },
            child: Text(AppLocalizations.of(context)!.settingsDeleteAction),
          ),
        ],
      ),
    );
  }

  void _showLegalDocument(BuildContext context, LegalDocument document, bool isDark) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => Scaffold(
          backgroundColor: isDark ? HopeColors.charcoal : HopeColors.cream,
          appBar: AppBar(
            title: Text(document.title),
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(HopeSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Version info
                Container(
                  padding: const EdgeInsets.all(HopeSpacing.md),
                  decoration: BoxDecoration(
                    color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.info_outline_rounded,
                        size: 20,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                      const SizedBox(width: HopeSpacing.sm),
                      Text(
                        'Version ${document.version} • Mise à jour ${document.lastUpdated.day}/${document.lastUpdated.month}/${document.lastUpdated.year}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: HopeSpacing.md),
                
                // Content
                SelectableText(
                  document.content,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    height: 1.7,
                  ),
                ),
                
                const SizedBox(height: HopeSpacing.xl),
                
                // Accept button
                SizedBox(
                  width: double.infinity,
                  child: FilledButton(
                    onPressed: () {
                      if (document.title == 'Privacy Policy') {
                        context.read<SettingsBloc>().add(
                          PrivacyPolicyAccepted(document.version),
                        );
                      } else {
                        context.read<SettingsBloc>().add(
                          TermsAccepted(document.version),
                        );
                      }
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('${document.title} accepté'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    },
                    child: Text(AppLocalizations.of(context)!.consentContinue),
                  ),
                ),
                const SizedBox(height: HopeSpacing.lg),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showAboutDialog(BuildContext context, bool isDark) {
    showAboutDialog(
      context: context,
      applicationName: 'HOPE',
      applicationVersion: _packageInfo?.version ?? '1.0.0',
      applicationIcon: Container(
        width: 48,
        height: 48,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primary,
          borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        ),
        child: HopeIcons.butterfly(size: 24, color: Colors.white),
      ),
      applicationLegalese: '© 2026 HOPE Team.',
      children: [
        const SizedBox(height: HopeSpacing.md),
        const Text(
          'HOPE - Healing-Oriented Panic Engine\n\n'
          'Une application d\'accompagnement lors des crises de panique, '
          'avec une IA bienveillante et des exercices de respiration.',
        ),
        const SizedBox(height: HopeSpacing.md),
        const Divider(),
        const SizedBox(height: HopeSpacing.sm),
        _buildAboutRow('IA Provider', 'Google Gemini'),
        _buildAboutRow('Environnement', const bool.fromEnvironment('dart.vm.product') ? 'Production' : 'Développement'),
        _buildAboutRow('Build', _packageInfo?.buildNumber ?? '1'),
      ],
    );
  }

  Widget _buildAboutRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: HopeSpacing.xs),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: Theme.of(context).textTheme.bodySmall),
          Text(value, style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w500,
          )),
        ],
      ),
    );
  }

  void _showFeedbackDialog(BuildContext context, bool isDark) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: isDark ? HopeColors.onyx : HopeColors.surface,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        title: Text(AppLocalizations.of(context)!.settingsFeedback),
        content: TextField(
          controller: controller,
          maxLines: 4,
          decoration: InputDecoration(
            hintText: 'Comment pouvons-nous améliorer HOPE?',
            filled: true,
            fillColor: isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(AppLocalizations.of(context)!.settingsCancel),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(AppLocalizations.of(context)!.settingsFeedbackSuccess),
                  behavior: SnackBarBehavior.floating,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
                  ),
                ),
              );
            },
            child: Text(AppLocalizations.of(context)!.chatSendButton),
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// SETTINGS SECTION - Grouped settings with header
// ============================================================================

class _SettingsSection extends StatelessWidget {
  final String title;
  final IconData? icon;
  final Widget? iconWidget;
  final bool isDark;
  final List<Widget> children;

  const _SettingsSection({
    required this.title,
    this.icon,
    this.iconWidget,
    required this.isDark,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Section header
        Padding(
          padding: const EdgeInsets.only(
            left: HopeSpacing.xs,
            bottom: HopeSpacing.sm,
          ),
          child: Row(
            children: [
              if (iconWidget != null)
                iconWidget!
              else if (icon != null)
                Icon(
                  icon,
                  size: 18,
                  color: Theme.of(context).colorScheme.primary,
                ),
              const SizedBox(width: HopeSpacing.sm),
              Text(
                title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: Theme.of(context).colorScheme.primary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        // Section content
        Container(
          decoration: BoxDecoration(
            color: isDark ? HopeColors.onyx : HopeColors.surface,
            borderRadius: BorderRadius.circular(HopeSpacing.radiusLg),
            boxShadow: HopeShadows.light,
          ),
          child: Column(
            children: children,
          ),
        ),
      ],
    );
  }
}

// ============================================================================
// SWITCH TILE
// ============================================================================

class _SwitchTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final bool value;
  final ValueChanged<bool> onChanged;
  final bool isDark;

  const _SwitchTile({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.value,
    required this.onChanged,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: HopeSpacing.md,
        vertical: HopeSpacing.xs,
      ),
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
        ),
        child: Icon(icon, color: Theme.of(context).colorScheme.primary, size: 20),
      ),
      title: Text(title, style: Theme.of(context).textTheme.titleSmall),
      subtitle: Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
      trailing: Switch(
        value: value,
        onChanged: (v) {
          HapticFeedback.selectionClick();
          onChanged(v);
        },
      ),
    );
  }
}

// ============================================================================
// DROPDOWN TILE
// ============================================================================

class _DropdownTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final String value;
  final List<String> options;
  final Map<String, String> displayNames;
  final ValueChanged<String?> onChanged;
  final bool isDark;

  const _DropdownTile({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.value,
    required this.options,
    required this.displayNames,
    required this.onChanged,
    required this.isDark,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: HopeSpacing.md,
        vertical: HopeSpacing.xs,
      ),
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
        ),
        child: Icon(icon, color: Theme.of(context).colorScheme.primary, size: 20),
      ),
      title: Text(title, style: Theme.of(context).textTheme.titleSmall),
      subtitle: Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: HopeSpacing.sm),
        decoration: BoxDecoration(
          color: isDark ? HopeColors.onyxLight : HopeColors.surfaceElevated,
          borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
        ),
        child: DropdownButton<String>(
          value: value,
          underline: const SizedBox(),
          icon: Icon(Icons.keyboard_arrow_down_rounded, size: 20),
          items: options.map((o) => DropdownMenuItem(
            value: o, 
            child: Text(displayNames[o] ?? o),
          )).toList(),
          onChanged: (v) {
            HapticFeedback.selectionClick();
            onChanged(v);
          },
        ),
      ),
    );
  }
}

// ============================================================================
// THEME TILE
// ============================================================================

class _ThemeTile extends StatelessWidget {
  final ThemePreference preference;
  final bool isDark;
  final ValueChanged<ThemePreference> onChanged;

  const _ThemeTile({
    required this.preference,
    required this.isDark,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(HopeSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
                ),
                child: Icon(
                  preference == ThemePreference.dark ? Icons.dark_mode_rounded :
                  preference == ThemePreference.light ? Icons.light_mode_rounded :
                  Icons.brightness_auto_rounded,
                  color: Theme.of(context).colorScheme.primary,
                  size: 20,
                ),
              ),
              const SizedBox(width: HopeSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(AppLocalizations.of(context)!.settingsTheme, style: Theme.of(context).textTheme.titleSmall),
                    Text(AppLocalizations.of(context)!.settingsAppearance, style: Theme.of(context).textTheme.bodySmall),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: HopeSpacing.md),
          SegmentedButton<ThemePreference>(
            segments: [
              ButtonSegment(
                value: ThemePreference.system,
                icon: Icon(Icons.brightness_auto_rounded, size: 18),
                label: Text(AppLocalizations.of(context)!.settingsThemeSystem),
              ),
              ButtonSegment(
                value: ThemePreference.light,
                icon: Icon(Icons.light_mode_rounded, size: 18),
                label: Text(AppLocalizations.of(context)!.settingsThemeLight),
              ),
              ButtonSegment(
                value: ThemePreference.dark,
                icon: Icon(Icons.dark_mode_rounded, size: 18),
                label: Text(AppLocalizations.of(context)!.settingsThemeDark),
              ),
            ],
            selected: {preference},
            onSelectionChanged: (selection) {
              HapticFeedback.selectionClick();
              onChanged(selection.first);
            },
          ),
        ],
      ),
    );
  }
}

// ============================================================================
// ACTION TILE
// ============================================================================

class _ActionTile extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData? icon;
  final Widget? iconWidget;
  final VoidCallback onTap;
  final bool isDestructive;
  final bool isLoading;
  final bool isDark;

  const _ActionTile({
    required this.title,
    required this.subtitle,
    this.icon,
    this.iconWidget,
    required this.onTap,
    required this.isDark,
    this.isDestructive = false,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final color = isDestructive ? HopeColors.coral : Theme.of(context).colorScheme.primary;
    
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(
        horizontal: HopeSpacing.md,
        vertical: HopeSpacing.xs,
      ),
      leading: isLoading
          ? SizedBox(
              width: 40,
              height: 40,
              child: Center(
                child: SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: color),
                ),
              ),
            )
          : Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(HopeSpacing.radiusSm),
              ),
              child: iconWidget ?? Icon(icon, color: color, size: 20),
            ),
      title: Text(
        title,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
          color: isDestructive ? HopeColors.coral : null,
        ),
      ),
      subtitle: Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
      trailing: Icon(
        Icons.chevron_right_rounded,
        color: isDark ? HopeColors.moonlightMuted : HopeColors.slateMuted,
      ),
      onTap: isLoading ? null : () {
        HapticFeedback.selectionClick();
        onTap();
      },
    );
  }
}
