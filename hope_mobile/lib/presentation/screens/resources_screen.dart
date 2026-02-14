/// Resources Screen - Verified Crisis Resources
/// 
/// PRODUCTION: All resources are localized.
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/theme/app_theme.dart';
import '../../l10n/generated/app_localizations.dart';

/// Verified crisis resource model.
class CrisisResource {
  final String name;
  final String description;
  final String phone;
  final String? url;
  final bool is24h;
  final bool isFree;
  final IconData icon;
  
  const CrisisResource({
    required this.name,
    required this.description,
    required this.phone,
    this.url,
    this.is24h = false,
    this.isFree = true,
    this.icon = Icons.phone,
  });
}

class ResourcesScreen extends StatelessWidget {
  const ResourcesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    
    // Define resources here to access l10n
    final emergencyNumbers = [
      CrisisResource(
        name: l10n.resourceSuicidePrevention,
        description: l10n.resourcesBannerSubtitle,
        phone: '3114',
        is24h: true,
        icon: Icons.emergency,
      ),
      CrisisResource(
        name: l10n.resourceEuropeanEmergency,
        description: l10n.resourceEuropeanEmergency,
        phone: '112',
        is24h: true,
        icon: Icons.local_hospital,
      ),
      CrisisResource(
        name: l10n.resourceMedicalEmergency,
        description: l10n.resourceMedicalEmergency,
        phone: '15',
        is24h: true,
        icon: Icons.medical_services,
      ),
    ];

    final supportLines = [
      CrisisResource(
        name: l10n.resourceSOSFriendship,
        description: l10n.resourceSOSFriendship,
        phone: '09 72 39 40 50',
        is24h: true,
        url: 'https://www.sos-amitie.com',
        icon: Icons.support_agent,
      ),
      CrisisResource(
        name: l10n.resourceYouthHealth,
        description: l10n.resourceYouthHealth,
        phone: '0 800 235 236',
        isFree: true,
        url: 'https://www.filsantejeunes.com',
        icon: Icons.people,
      ),
      CrisisResource(
        name: l10n.resourceRedCross,
        description: l10n.resourceRedCross,
        phone: '0 800 858 858',
        isFree: true,
        url: 'https://www.croix-rouge.fr',
        icon: Icons.health_and_safety,
      ),
    ];

    final internationalFallback = [
      CrisisResource(
        name: 'Find A Helpline',
        description: l10n.resourcesInternationalHelp,
        phone: '',
        url: 'https://findahelpline.com',
        icon: Icons.public,
      ),
      CrisisResource(
        name: 'IASP Crisis Centers',
        description: l10n.resourcesInternationalHelp,
        phone: '',
        url: 'https://www.iasp.info/resources/Crisis_Centres/',
        icon: Icons.language,
      ),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.resourcesTitle),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Emergency banner
          _buildEmergencyBanner(context, l10n),
          
          const SizedBox(height: 24),
          
          // Emergency numbers
          _buildSection(
            context,
            title: l10n.resourcesEmergencyNumbers,
            icon: Icons.emergency,
            children: emergencyNumbers
                .map((r) => _buildResourceTile(context, r, l10n))
                .toList(),
          ),
          
          const SizedBox(height: 24),
          
          // Support lines
          _buildSection(
            context,
            title: l10n.resourcesSupportLines,
            icon: Icons.phone_in_talk,
            children: supportLines
                .map((r) => _buildResourceTile(context, r, l10n))
                .toList(),
          ),
          
          const SizedBox(height: 24),
          
          // Coping techniques
          _buildSection(
            context,
            title: l10n.resourcesCopingTechniques,
            icon: Icons.self_improvement,
            children: [
              _buildTechniqueTile(
                context,
                title: l10n.techniqueBreathing,
                subtitle: l10n.techniqueBreathingDesc,
                icon: Icons.air,
              ),
              _buildTechniqueTile(
                context,
                title: l10n.techniqueGrounding,
                subtitle: l10n.techniqueGroundingDesc,
                icon: Icons.visibility,
              ),
              _buildTechniqueTile(
                context,
                title: l10n.techniqueRelaxation,
                subtitle: l10n.techniqueRelaxationDesc,
                icon: Icons.accessibility_new,
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // International fallback
          _buildSection(
            context,
            title: l10n.resourcesInternationalHelp,
            icon: Icons.public,
            children: internationalFallback
                .map((r) => _buildResourceTile(context, r, l10n))
                .toList(),
          ),
          
          const SizedBox(height: 24),
          
          // Disclaimer
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Text(
              l10n.resourcesMedicalDisclaimer,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmergencyBanner(BuildContext context, AppLocalizations l10n) {
    return InkWell(
      onTap: () => _callNumber('3114'),
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.crisisColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.crisisColor.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.crisisColor,
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.phone, color: Colors.white),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    l10n.resourcesBannerTitle,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: AppTheme.crisisColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    l10n.resourcesBannerSubtitle,
                    style: const TextStyle(fontSize: 13),
                  ),
                ],
              ),
            ),
            Icon(Icons.call, color: AppTheme.crisisColor),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(
    BuildContext context, {
    required String title,
    required IconData icon,
    required List<Widget> children,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Icon(icon, color: AppTheme.panicAccent, size: 20),
            const SizedBox(width: 8),
            Text(
              title,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ...children,
      ],
    );
  }

  Widget _buildResourceTile(BuildContext context, CrisisResource resource, AppLocalizations l10n) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: resource.is24h 
              ? AppTheme.crisisColor.withOpacity(0.1)
              : AppTheme.panicAccent.withOpacity(0.1),
          child: Icon(
            resource.icon, 
            color: resource.is24h ? AppTheme.crisisColor : AppTheme.panicAccent, 
            size: 20,
          ),
        ),
        title: Text(resource.name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(resource.description),
            if (resource.phone.isNotEmpty) ...[
              const SizedBox(height: 4),
              Wrap(
                spacing: 4,
                runSpacing: 4,
                crossAxisAlignment: WrapCrossAlignment.center,
                children: [
                  Text(
                    resource.phone,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: AppTheme.panicAccent,
                    ),
                  ),
                  if (resource.is24h) 
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: AppTheme.calmColor.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        '24h',
                        style: TextStyle(
                          fontSize: 10,
                          color: AppTheme.calmColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ],
        ),
        trailing: resource.phone.isNotEmpty 
            ? IconButton(
                icon: const Icon(Icons.call),
                color: AppTheme.crisisColor,
                onPressed: () => _callNumber(resource.phone),
              )
            : IconButton(
                icon: const Icon(Icons.open_in_new),
                onPressed: () => _openUrl(resource.url!),
              ),
        onTap: resource.phone.isNotEmpty 
            ? () => _callNumber(resource.phone)
            : () => _openUrl(resource.url!),
      ),
    );
  }

  Widget _buildTechniqueTile(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: AppTheme.panicAccent.withOpacity(0.1),
          child: Icon(icon, color: AppTheme.panicAccent, size: 20),
        ),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          // Navigate to technique detail
        },
      ),
    );
  }

  Future<void> _callNumber(String number) async {
    final cleanNumber = number.replaceAll(' ', '');
    final uri = Uri.parse('tel:$cleanNumber');
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }

  Future<void> _openUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}

