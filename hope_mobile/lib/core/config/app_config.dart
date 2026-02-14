/// HOPE App Configuration
///
/// Centralized configuration for backend API URLs and environment settings.
/// Uses --dart-define for build-time configuration:
///
/// ```bash
/// # Development (local backend)
/// flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
///
/// # Production
/// flutter run --release --dart-define=API_BASE_URL=https://hope-api-b3bxa3htdsd3guhc.swedencentral-01.azurewebsites.net
/// ```
library;

class AppConfig {
  AppConfig._();

  /// Backend API base URL (no trailing slash)
  /// Configurable via --dart-define=API_BASE_URL=...
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://hope-api-b3bxa3htdsd3guhc.swedencentral-01.azurewebsites.net',
  );

  /// Full API v1 URL
  static const String apiV1Url = '$apiBaseUrl/api/v1';

  /// Health check URL
  static const String healthUrl = '$apiBaseUrl/health';

  /// Whether we're running in release mode
  static const bool isRelease = bool.fromEnvironment('dart.vm.product');
}
