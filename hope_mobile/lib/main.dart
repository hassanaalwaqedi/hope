/// Main App with Bottom Navigation, Localization, and Settings
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'core/theme/app_theme.dart';
import 'core/di/service_locator.dart';
import 'core/settings/settings_service.dart';
import 'core/settings/settings_bloc.dart';
import 'core/settings/user_data_service.dart';
import 'presentation/screens/home_screen.dart';
import 'presentation/screens/chat_screen.dart';
import 'presentation/screens/history_screen.dart';
import 'presentation/screens/resources_screen.dart';
import 'presentation/screens/settings_screen.dart';
import 'panic/bloc/panic_bloc.dart';
import 'l10n/generated/app_localizations.dart';

// Global settings service instance
late final SettingsService settingsService;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize settings service first
  settingsService = SettingsService();
  await settingsService.initialize();

  await setupServiceLocator();

  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);

  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
    ),
  );

  runApp(const HopeApp());
}

class HopeApp extends StatefulWidget {
  const HopeApp({super.key});

  @override
  State<HopeApp> createState() => _HopeAppState();
  
  /// Allows changing locale from anywhere in the app
  static void setLocale(BuildContext context, Locale newLocale) {
    final state = context.findAncestorStateOfType<_HopeAppState>();
    state?.setLocale(newLocale);
  }
  
  /// Allows changing theme mode from anywhere in the app
  static void setThemeMode(BuildContext context, ThemeMode mode) {
    final state = context.findAncestorStateOfType<_HopeAppState>();
    state?.setThemeMode(mode);
  }
}

class _HopeAppState extends State<HopeApp> {
  Locale? _locale;
  ThemeMode _themeMode = ThemeMode.system;
  
  @override
  void initState() {
    super.initState();
    // Load initial settings
    _themeMode = _getThemeModeFromSettings();
    _locale = _getLocaleFromSettings();
    
    // Listen for settings changes
    settingsService.addListener((settings) {
      if (mounted) {
        setState(() {
          _themeMode = _getThemeModeFromSettings();
          final newLocale = _getLocaleFromSettings();
          if (newLocale != _locale) {
            _locale = newLocale;
          }
        });
      }
    });
  }
  
  ThemeMode _getThemeModeFromSettings() {
    switch (settingsService.settings.themePreference) {
      case ThemePreference.light:
        return ThemeMode.light;
      case ThemePreference.dark:
        return ThemeMode.dark;
      case ThemePreference.system:
        return ThemeMode.system;
    }
  }

  Locale? _getLocaleFromSettings() {
    final code = settingsService.settings.languageCode;
    if (code != null) {
      return Locale(code);
    }
    return null; // System default
  }
  
  void setLocale(Locale locale) {
    setState(() {
      _locale = locale;
    });
    // Also save to settings
    settingsService.setLanguageCode(locale.languageCode);
  }
  
  void setThemeMode(ThemeMode mode) {
    setState(() {
      _themeMode = mode;
    });
    // Save is handled by SettingsBloc/Service elsewhere but we could do it here too if needed
  }

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<PanicBloc>(
          create: (_) => getIt<PanicBloc>(),
        ),
        BlocProvider<SettingsBloc>(
          create: (_) => SettingsBloc(
            settingsService: settingsService,
            userDataService: UserDataService(),
          )..add(const SettingsLoaded()),
        ),
      ],
      child: MaterialApp(
        title: 'HOPE',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: _themeMode,
        
        // Localization configuration
        locale: _locale,
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        supportedLocales: const [
          Locale('en'), // English
          Locale('fr'), // French
          Locale('ar'), // Arabic (RTL)
          Locale('de'), // German
          Locale('es'), // Spanish
          Locale('it'), // Italian
          Locale('ko'), // Korean
        ],
        
        home: const MainNavigation(),
      ),
    );
  }
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    HomeScreen(),
    ChatScreen(),
    HistoryScreen(),
    ResourcesScreen(),
    SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    
    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: _screens,
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          HapticFeedback.selectionClick();
          setState(() => _currentIndex = index);
        },
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.home_outlined),
            selectedIcon: const Icon(Icons.home),
            label: l10n.navHome,
          ),
          NavigationDestination(
            icon: const Icon(Icons.chat_outlined),
            selectedIcon: const Icon(Icons.chat),
            label: l10n.navChat,
          ),
          NavigationDestination(
            icon: const Icon(Icons.history_outlined),
            selectedIcon: const Icon(Icons.history),
            label: l10n.navHistory,
          ),
          NavigationDestination(
            icon: const Icon(Icons.support_outlined),
            selectedIcon: const Icon(Icons.support),
            label: l10n.navResources,
          ),
          NavigationDestination(
            icon: const Icon(Icons.settings_outlined),
            selectedIcon: const Icon(Icons.settings),
            label: l10n.navSettings,
          ),
        ],
      ),
    );
  }
}
