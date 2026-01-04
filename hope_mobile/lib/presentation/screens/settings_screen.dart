/// Settings Screen - App configuration and profile
import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notificationsEnabled = true;
  bool _voiceGuidance = false;
  bool _hapticFeedback = true;
  bool _darkMode = false;
  String _breathingSpeed = 'Normal';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Profile section
          _buildProfileCard(context),
          
          const SizedBox(height: 24),
          
          // Panic settings
          _buildSectionHeader(context, 'Panic Mode'),
          _buildSwitchTile(
            title: 'Voice Guidance',
            subtitle: 'Spoken instructions during panic',
            icon: Icons.volume_up,
            value: _voiceGuidance,
            onChanged: (v) => setState(() => _voiceGuidance = v),
          ),
          _buildSwitchTile(
            title: 'Haptic Feedback',
            subtitle: 'Vibration during exercises',
            icon: Icons.vibration,
            value: _hapticFeedback,
            onChanged: (v) => setState(() => _hapticFeedback = v),
          ),
          _buildDropdownTile(
            title: 'Breathing Speed',
            subtitle: 'Adjust exercise pace',
            icon: Icons.speed,
            value: _breathingSpeed,
            options: ['Slow', 'Normal', 'Fast'],
            onChanged: (v) => setState(() => _breathingSpeed = v!),
          ),
          
          const SizedBox(height: 24),
          
          // Notifications
          _buildSectionHeader(context, 'Notifications'),
          _buildSwitchTile(
            title: 'Daily Check-in',
            subtitle: 'Gentle reminder to check in',
            icon: Icons.notifications,
            value: _notificationsEnabled,
            onChanged: (v) => setState(() => _notificationsEnabled = v),
          ),
          
          const SizedBox(height: 24),
          
          // Appearance
          _buildSectionHeader(context, 'Appearance'),
          _buildSwitchTile(
            title: 'Dark Mode',
            subtitle: 'Use dark theme',
            icon: Icons.dark_mode,
            value: _darkMode,
            onChanged: (v) => setState(() => _darkMode = v),
          ),
          
          const SizedBox(height: 24),
          
          // Data & Privacy
          _buildSectionHeader(context, 'Data & Privacy'),
          _buildActionTile(
            title: 'Export Data',
            subtitle: 'Download your session history',
            icon: Icons.download,
            onTap: () {},
          ),
          _buildActionTile(
            title: 'Clear History',
            subtitle: 'Delete all session data',
            icon: Icons.delete_outline,
            onTap: () => _showClearDataDialog(context),
            isDestructive: true,
          ),
          _buildActionTile(
            title: 'Privacy Policy',
            subtitle: 'How we protect your data',
            icon: Icons.privacy_tip,
            onTap: () {},
          ),
          
          const SizedBox(height: 24),
          
          // About
          _buildSectionHeader(context, 'About'),
          _buildActionTile(
            title: 'About HOPE',
            subtitle: 'Version 1.0.0',
            icon: Icons.info,
            onTap: () => _showAboutDialog(context),
          ),
          _buildActionTile(
            title: 'Terms of Service',
            subtitle: 'Legal information',
            icon: Icons.description,
            onTap: () {},
          ),
          _buildActionTile(
            title: 'Send Feedback',
            subtitle: 'Help us improve',
            icon: Icons.feedback,
            onTap: () {},
          ),
          
          const SizedBox(height: 32),
          
          // Disclaimer
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              'HOPE is a support tool, not a replacement for professional mental health care. '
              'If you are in crisis, please contact emergency services or a mental health professional.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileCard(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
          ),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 30,
            backgroundColor: AppTheme.panicAccent,
            child: const Icon(Icons.person, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Welcome',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  'Anonymous User',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit),
            onPressed: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
          fontWeight: FontWeight.w600,
          color: AppTheme.panicAccent,
        ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required IconData icon,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: SwitchListTile(
        secondary: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
        value: value,
        onChanged: onChanged,
      ),
    );
  }

  Widget _buildDropdownTile({
    required String title,
    required String subtitle,
    required IconData icon,
    required String value,
    required List<String> options,
    required ValueChanged<String?> onChanged,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: DropdownButton<String>(
          value: value,
          underline: const SizedBox(),
          items: options.map((o) => DropdownMenuItem(value: o, child: Text(o))).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }

  Widget _buildActionTile({
    required String title,
    required String subtitle,
    required IconData icon,
    required VoidCallback onTap,
    bool isDestructive = false,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: isDestructive ? Colors.red : null),
        title: Text(title, style: TextStyle(color: isDestructive ? Colors.red : null)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }

  void _showClearDataDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Clear All Data?'),
        content: const Text('This will permanently delete all your session history. This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Data cleared')),
              );
            },
            child: const Text('Clear', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showAboutDialog(
      context: context,
      applicationName: 'HOPE',
      applicationVersion: '1.0.0',
      applicationIcon: CircleAvatar(
        backgroundColor: AppTheme.panicAccent,
        child: const Icon(Icons.favorite, color: Colors.white),
      ),
      children: [
        const Text(
          'HOPE - Healing-Oriented Panic Engine\n\n'
          'A panic intervention support app providing real-time AI-powered assistance during acute distress episodes.',
        ),
      ],
    );
  }
}
