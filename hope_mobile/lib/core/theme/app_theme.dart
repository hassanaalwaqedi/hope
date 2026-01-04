/// App Theme - Calming, minimal theme for panic situations
import 'package:flutter/material.dart';

class AppTheme {
  AppTheme._();

  static const Color primaryLight = Color(0xFF6B7FD7);
  static const Color primaryDark = Color(0xFF8B9FE8);
  static const Color backgroundLight = Color(0xFFF8F9FC);
  static const Color backgroundDark = Color(0xFF1A1A2E);
  static const Color surfaceLight = Color(0xFFFFFFFF);
  static const Color surfaceDark = Color(0xFF252542);
  static const Color textPrimaryLight = Color(0xFF2D3142);
  static const Color textPrimaryDark = Color(0xFFE8E8EE);
  static const Color panicAccent = Color(0xFF7C9A92);
  static const Color crisisColor = Color(0xFFD97706);
  static const Color calmColor = Color(0xFF059669);

  static const String fontFamily = 'Inter';

  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    primaryColor: primaryLight,
    scaffoldBackgroundColor: backgroundLight,
    fontFamily: fontFamily,
    colorScheme: const ColorScheme.light(
      primary: primaryLight,
      secondary: panicAccent,
      surface: surfaceLight,
      error: crisisColor,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryLight,
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 56),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    ),
  );

  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    primaryColor: primaryDark,
    scaffoldBackgroundColor: backgroundDark,
    fontFamily: fontFamily,
    colorScheme: const ColorScheme.dark(
      primary: primaryDark,
      secondary: panicAccent,
      surface: surfaceDark,
      error: crisisColor,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryDark,
        foregroundColor: backgroundDark,
        minimumSize: const Size(double.infinity, 56),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
    ),
  );
}

class PanicUiConstants {
  PanicUiConstants._();
  static const double minTouchTarget = 48.0;
  static const double panicButtonSize = 180.0;
  static const double paddingSmall = 8.0;
  static const double paddingMedium = 16.0;
  static const double paddingLarge = 24.0;
  static const Duration fadeIn = Duration(milliseconds: 400);
  static const Duration fadeOut = Duration(milliseconds: 300);
}
