/// Connectivity Service
/// 
/// Real-time network connectivity monitoring with automatic recovery.
/// Provides stream-based updates for UI reactivity.
/// 
/// SAFETY-CRITICAL: Ensures users can always access panic features
/// even when connectivity is degraded.

import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// Network status levels
enum NetworkStatus {
  /// Full connectivity - internet and backend available
  online,
  /// Internet available but backend unreachable
  backendUnavailable,
  /// No internet connection
  offline,
  /// Status unknown or checking
  unknown,
}

/// Result of connectivity check
class ConnectivityStatus {
  final NetworkStatus status;
  final bool hasInternet;
  final bool backendReachable;
  final DateTime checkedAt;
  final String? errorMessage;
  
  const ConnectivityStatus({
    required this.status,
    required this.hasInternet,
    required this.backendReachable,
    required this.checkedAt,
    this.errorMessage,
  });
  
  factory ConnectivityStatus.online() => ConnectivityStatus(
    status: NetworkStatus.online,
    hasInternet: true,
    backendReachable: true,
    checkedAt: DateTime.now(),
  );
  
  factory ConnectivityStatus.offline() => ConnectivityStatus(
    status: NetworkStatus.offline,
    hasInternet: false,
    backendReachable: false,
    checkedAt: DateTime.now(),
  );
  
  factory ConnectivityStatus.backendDown([String? error]) => ConnectivityStatus(
    status: NetworkStatus.backendUnavailable,
    hasInternet: true,
    backendReachable: false,
    checkedAt: DateTime.now(),
    errorMessage: error,
  );
  
  /// Whether online chat should be used
  bool get canUseOnlineChat => status == NetworkStatus.online;
  
  /// Whether any network is available
  bool get hasAnyNetwork => hasInternet;
  
  @override
  String toString() => 'ConnectivityStatus($status)';
}

/// Connectivity Service
/// 
/// Monitors network connectivity in real-time and provides
/// stream-based updates for reactive UI.
class ConnectivityService {
  static final ConnectivityService _instance = ConnectivityService._();
  factory ConnectivityService() => _instance;
  ConnectivityService._();
  
  final Connectivity _connectivity = Connectivity();
  
  // Stream controller for status updates
  final _statusController = StreamController<ConnectivityStatus>.broadcast();
  
  // Current status
  ConnectivityStatus _currentStatus = ConnectivityStatus(
    status: NetworkStatus.unknown,
    hasInternet: true, // Assume online until proven otherwise
    backendReachable: true,
    checkedAt: DateTime.now(),
  );
  
  // Subscription for platform connectivity changes
  StreamSubscription<ConnectivityResult>? _subscription;
  
  // Backend health check timer
  Timer? _healthCheckTimer;
  
  // Backend URL to check - Production Azure backend
  static const String _backendHealthUrl = 'https://hope-api-b3bxa3htdkd3guhc.swedencentral-01.azurewebsites.net/health';
  
  // For local development, uncomment this:
  // static const String _backendHealthUrl = 'http://localhost:8000/health';
  
  static const Duration _healthCheckInterval = Duration(seconds: 30);
  static const Duration _healthCheckTimeout = Duration(seconds: 5);
  
  // Retry configuration
  int _consecutiveFailures = 0;
  static const int _maxFailuresBeforeOffline = 2;
  
  /// Stream of connectivity status updates
  Stream<ConnectivityStatus> get statusStream => _statusController.stream;
  
  /// Current connectivity status
  ConnectivityStatus get currentStatus => _currentStatus;
  
  /// Whether online chat is available
  bool get isOnline => _currentStatus.canUseOnlineChat;
  
  /// Initialize connectivity monitoring
  /// 
  /// Call this once at app startup.
  Future<void> initialize() async {
    // Check initial status
    await checkConnectivity();
    
    // Listen for platform connectivity changes
    _subscription = _connectivity.onConnectivityChanged.listen((result) {
      _handleConnectivityChange(result);
    });
    
    // Start periodic health checks
    _startHealthCheckTimer();
    
    debugPrint('ConnectivityService: Initialized');
  }
  
  /// Force check connectivity now
  /// 
  /// Call this when you want to verify status immediately.
  Future<ConnectivityStatus> checkConnectivity() async {
    // First check platform connectivity
    final result = await _connectivity.checkConnectivity();
    final hasNetwork = result != ConnectivityResult.none;
    
    if (!hasNetwork) {
      _updateStatus(ConnectivityStatus.offline());
      return _currentStatus;
    }
    
    // Have network, check if backend is reachable
    final backendReachable = await _checkBackendHealth();
    
    if (backendReachable) {
      _consecutiveFailures = 0;
      _updateStatus(ConnectivityStatus.online());
    } else {
      _consecutiveFailures++;
      
      if (_consecutiveFailures >= _maxFailuresBeforeOffline) {
        _updateStatus(ConnectivityStatus.backendDown());
      }
    }
    
    return _currentStatus;
  }
  
  /// Handle platform connectivity changes
  void _handleConnectivityChange(ConnectivityResult result) {
    final hasNetwork = result != ConnectivityResult.none;
    
    debugPrint('ConnectivityService: Platform connectivity changed, hasNetwork=$hasNetwork');
    
    if (!hasNetwork) {
      // Immediately go offline
      _updateStatus(ConnectivityStatus.offline());
    } else if (_currentStatus.status == NetworkStatus.offline) {
      // Came back online - verify backend
      checkConnectivity();
    }
  }
  
  /// Check if backend is reachable
  /// 
  /// Uses http package which works on both mobile and web platforms.
  Future<bool> _checkBackendHealth() async {
    try {
      final response = await http.get(
        Uri.parse(_backendHealthUrl),
      ).timeout(_healthCheckTimeout);
      
      return response.statusCode == 200;
    } on TimeoutException {
      debugPrint('ConnectivityService: Backend health check timeout');
      return false;
    } catch (e) {
      debugPrint('ConnectivityService: Backend health check failed: $e');
      return false;
    }
  }
  
  /// Start periodic health check timer
  void _startHealthCheckTimer() {
    _healthCheckTimer?.cancel();
    _healthCheckTimer = Timer.periodic(_healthCheckInterval, (_) {
      // Only check if we think we're online
      if (_currentStatus.hasInternet) {
        checkConnectivity();
      }
    });
  }
  
  /// Update status and notify listeners
  void _updateStatus(ConnectivityStatus newStatus) {
    if (_currentStatus.status != newStatus.status) {
      debugPrint('ConnectivityService: Status changed ${_currentStatus.status} -> ${newStatus.status}');
    }
    
    _currentStatus = newStatus;
    _statusController.add(newStatus);
  }
  
  /// Notify that an API call succeeded
  /// 
  /// Call this after successful API calls to confirm online status.
  void notifyApiSuccess() {
    _consecutiveFailures = 0;
    
    if (_currentStatus.status != NetworkStatus.online) {
      _updateStatus(ConnectivityStatus.online());
    }
  }
  
  /// Notify that an API call failed
  /// 
  /// Call this after failed API calls to trigger connectivity check.
  void notifyApiFailure() {
    _consecutiveFailures++;
    
    if (_consecutiveFailures >= _maxFailuresBeforeOffline) {
      // Trigger immediate connectivity check
      checkConnectivity();
    }
  }
  
  /// Dispose resources
  void dispose() {
    _subscription?.cancel();
    _healthCheckTimer?.cancel();
    _statusController.close();
  }
}

/// Global connectivity service instance
final connectivityService = ConnectivityService();
