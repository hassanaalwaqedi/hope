/// Resources Screen - Real Crisis Resources for France
/// 
/// PRODUCTION: All resources are verified French crisis services.
/// Primary: France | Fallback: International
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/theme/app_theme.dart';

/// Verified French crisis resource.
class CrisisResource {
  final String name;
  final String nameEn;
  final String description;
  final String phone;
  final String? sms;
  final String? url;
  final bool is24h;
  final bool isFree;
  final IconData icon;
  
  const CrisisResource({
    required this.name,
    required this.nameEn,
    required this.description,
    required this.phone,
    this.sms,
    this.url,
    this.is24h = false,
    this.isFree = true,
    this.icon = Icons.phone,
  });
}

/// Verified French crisis resources.
/// Source: Verified government and established NGO sources.
class FrenchCrisisResources {
  static const List<CrisisResource> emergencyNumbers = [
    CrisisResource(
      name: 'Numéro National de Prévention du Suicide',
      nameEn: 'National Suicide Prevention Number',
      description: 'Ligne nationale gratuite, confidentielle, 24h/24',
      phone: '3114',
      is24h: true,
      isFree: true,
      icon: Icons.emergency,
    ),
    CrisisResource(
      name: 'Urgences Européennes',
      nameEn: 'European Emergency',
      description: 'Numéro d\'urgence européen - Police, Pompiers, SAMU',
      phone: '112',
      is24h: true,
      isFree: true,
      icon: Icons.local_hospital,
    ),
    CrisisResource(
      name: 'SAMU',
      nameEn: 'Emergency Medical Services',
      description: 'Service d\'aide médicale urgente',
      phone: '15',
      is24h: true,
      isFree: true,
      icon: Icons.medical_services,
    ),
  ];

  static const List<CrisisResource> supportLines = [
    CrisisResource(
      name: 'SOS Amitié',
      nameEn: 'SOS Friendship',
      description: 'Écoute anonyme pour personnes en détresse',
      phone: '09 72 39 40 50',
      is24h: true,
      isFree: true,
      url: 'https://www.sos-amitie.com',
      icon: Icons.favorite,
    ),
    CrisisResource(
      name: 'Fil Santé Jeunes',
      nameEn: 'Youth Health Line',
      description: 'Pour les 12-25 ans, anonyme et gratuit',
      phone: '0 800 235 236',
      is24h: false,
      isFree: true,
      url: 'https://www.filsantejeunes.com',
      icon: Icons.people,
    ),
    CrisisResource(
      name: 'SOS Suicide Phénix',
      nameEn: 'SOS Suicide Phoenix',
      description: 'Association d\'aide aux personnes en détresse',
      phone: '01 40 44 46 45',
      is24h: false,
      isFree: true,
      url: 'https://www.sos-suicide-phenix.org',
      icon: Icons.support,
    ),
    CrisisResource(
      name: 'Croix-Rouge Écoute',
      nameEn: 'Red Cross Listening',
      description: 'Soutien psychologique par la Croix-Rouge',
      phone: '0 800 858 858',
      is24h: false,
      isFree: true,
      url: 'https://www.croix-rouge.fr',
      icon: Icons.health_and_safety,
    ),
  ];

  static const List<CrisisResource> internationalFallback = [
    CrisisResource(
      name: 'Find A Helpline',
      nameEn: 'International Helplines',
      description: 'Trouver une ligne d\'écoute dans votre pays',
      phone: '',
      url: 'https://findahelpline.com',
      icon: Icons.public,
    ),
    CrisisResource(
      name: 'International Association for Suicide Prevention',
      nameEn: 'IASP Crisis Centers',
      description: 'Centres de crise internationaux',
      phone: '',
      url: 'https://www.iasp.info/resources/Crisis_Centres/',
      icon: Icons.language,
    ),
  ];
}

class ResourcesScreen extends StatelessWidget {
  const ResourcesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ressources'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Emergency banner
          _buildEmergencyBanner(context),
          
          const SizedBox(height: 24),
          
          // Emergency numbers
          _buildSection(
            context,
            title: 'Numéros d\'Urgence',
            titleEn: 'Emergency Numbers',
            icon: Icons.emergency,
            children: FrenchCrisisResources.emergencyNumbers
                .map((r) => _buildResourceTile(context, r))
                .toList(),
          ),
          
          const SizedBox(height: 24),
          
          // Support lines
          _buildSection(
            context,
            title: 'Lignes d\'Écoute',
            titleEn: 'Support Lines',
            icon: Icons.phone_in_talk,
            children: FrenchCrisisResources.supportLines
                .map((r) => _buildResourceTile(context, r))
                .toList(),
          ),
          
          const SizedBox(height: 24),
          
          // Coping techniques (real, verified)
          _buildSection(
            context,
            title: 'Techniques de Gestion',
            titleEn: 'Coping Techniques',
            icon: Icons.self_improvement,
            children: [
              _buildTechniqueTile(
                context,
                title: 'Respiration Carrée',
                subtitle: 'Technique 4-4-4-4 pour le calme',
                icon: Icons.air,
              ),
              _buildTechniqueTile(
                context,
                title: 'Ancrage 5-4-3-2-1',
                subtitle: 'Utilisez vos sens pour vous ancrer',
                icon: Icons.visibility,
              ),
              _buildTechniqueTile(
                context,
                title: 'Relaxation Musculaire',
                subtitle: 'Technique de tension-relâchement',
                icon: Icons.accessibility_new,
              ),
            ],
          ),
          
          const SizedBox(height: 24),
          
          // International fallback
          _buildSection(
            context,
            title: 'Aide Internationale',
            titleEn: 'International Help',
            icon: Icons.public,
            children: FrenchCrisisResources.internationalFallback
                .map((r) => _buildResourceTile(context, r))
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
              'Cette application ne remplace pas un suivi médical professionnel. '
              'En cas d\'urgence vitale, appelez le 15 (SAMU) ou le 112.',
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

  Widget _buildEmergencyBanner(BuildContext context) {
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
                    'En crise ? Appelez le 3114',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: AppTheme.crisisColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Gratuit, confidentiel, 24h/24',
                    style: TextStyle(fontSize: 13),
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
    required String titleEn,
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

  Widget _buildResourceTile(BuildContext context, CrisisResource resource) {
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
                      child: Text(
                        '24h/24',
                        style: TextStyle(
                          fontSize: 10,
                          color: AppTheme.calmColor,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  if (resource.isFree) 
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: Colors.green.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: const Text(
                        'Gratuit',
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.green,
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
