/// History Screen - Session History
/// 
/// PRODUCTION: No mock data. Shows real sessions or empty state.
/// Data will come from local storage or backend when available.
import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

/// Session data model for history display.
class SessionRecord {
  final String id;
  final DateTime startedAt;
  final Duration duration;
  final int peakIntensity;
  final String outcome;
  
  const SessionRecord({
    required this.id,
    required this.startedAt,
    required this.duration,
    required this.peakIntensity,
    required this.outcome,
  });
}

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<SessionRecord>? _sessions;
  bool _loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadSessions();
  }
  
  Future<void> _loadSessions() async {
    // TODO: Load from local storage or backend
    // For now, show empty state until real data is available
    await Future.delayed(const Duration(milliseconds: 500));
    
    if (mounted) {
      setState(() {
        _sessions = []; // Empty - no mock data
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Historique'),
        centerTitle: true,
      ),
      body: _loading 
          ? const Center(child: CircularProgressIndicator())
          : _sessions!.isEmpty 
              ? _buildEmptyState(context)
              : _buildSessionList(context),
    );
  }
  
  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.history,
              size: 64,
              color: Colors.grey.withOpacity(0.5),
            ),
            const SizedBox(height: 24),
            Text(
              'Pas encore de sessions',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 12),
            Text(
              'Vos sessions de gestion de panique apparaîtront ici.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: Colors.grey[500],
              ),
            ),
            const SizedBox(height: 32),
            OutlinedButton.icon(
              onPressed: () {
                // Navigate to home or start panic session
                Navigator.of(context).pop();
              },
              icon: const Icon(Icons.home),
              label: const Text('Retour à l\'accueil'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionList(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Stats card - calculated from real data
        if (_sessions!.isNotEmpty) ...[
          _buildStatsCard(context),
          const SizedBox(height: 24),
        ],
        
        // Recent sessions
        Text(
          'Sessions récentes',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 12),
        
        // Session list from real data
        ..._sessions!.map((session) => _buildSessionCard(context, session)),
      ],
    );
  }

  Widget _buildStatsCard(BuildContext context) {
    // Calculate real stats from sessions
    final sessionCount = _sessions!.length;
    final totalDuration = _sessions!.fold<Duration>(
      Duration.zero,
      (sum, s) => sum + s.duration,
    );
    final avgIntensity = _sessions!.isEmpty 
        ? 0.0 
        : _sessions!.map((s) => s.peakIntensity).reduce((a, b) => a + b) / sessionCount;
    
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.panicAccent,
            AppTheme.panicAccent.withOpacity(0.7),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          Text(
            'Cette semaine',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: Colors.white.withOpacity(0.9),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStat(context, '$sessionCount', 'Sessions'),
              _buildStat(context, '${totalDuration.inMinutes} min', 'Total'),
              _buildStat(context, avgIntensity.toStringAsFixed(1), 'Intensité'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStat(BuildContext context, String value, String label) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: Colors.white.withOpacity(0.8),
          ),
        ),
      ],
    );
  }

  Widget _buildSessionCard(BuildContext context, SessionRecord session) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: _getIntensityColor(session.peakIntensity).withOpacity(0.2),
          child: Text(
            '${session.peakIntensity}',
            style: TextStyle(
              color: _getIntensityColor(session.peakIntensity),
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        title: Text(_formatDate(session.startedAt)),
        subtitle: Text('${session.duration.inMinutes} min • ${session.outcome}'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          // Show session details
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);
    final yesterday = today.subtract(const Duration(days: 1));
    final sessionDate = DateTime(date.year, date.month, date.day);
    
    if (sessionDate == today) {
      return "Aujourd'hui, ${date.hour}:${date.minute.toString().padLeft(2, '0')}";
    } else if (sessionDate == yesterday) {
      return "Hier, ${date.hour}:${date.minute.toString().padLeft(2, '0')}";
    } else {
      return "${date.day}/${date.month}/${date.year}";
    }
  }

  Color _getIntensityColor(int value) {
    if (value <= 3) return const Color(0xFF059669);
    if (value <= 5) return const Color(0xFFD97706);
    if (value <= 7) return const Color(0xFFEA580C);
    return const Color(0xFFDC2626);
  }
}
