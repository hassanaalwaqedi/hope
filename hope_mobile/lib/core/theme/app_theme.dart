/// HOPE Design System
/// 
/// Therapeutic, calm, professional design system for mental health.
/// Designed for someone at their lowest point - every element must feel safe.
/// 
/// Design Principles:
/// - Safe: Warm colors, rounded shapes, gentle animations
/// - Calm: Muted palette, slow transitions, reduced visual noise
/// - Clinical: Consistent system, accessibility compliance
/// - Human: Friendly typography, supportive iconography

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// ============================================================================
// COLOR TOKENS - Therapeutic Palette
// ============================================================================

class HopeColors {
  HopeColors._();
  
  // ─────────────────────────────────────────────────────────────────────────
  // LIGHT MODE - Warm, inviting, safe
  // ─────────────────────────────────────────────────────────────────────────
  
  /// Primary sage - calming, grounded, nature-inspired
  static const Color sage = Color(0xFF7C9885);
  static const Color sageLight = Color(0xFF9BB5A3);
  static const Color sageDark = Color(0xFF5D7A66);
  
  /// Backgrounds - warm whites, never pure white
  static const Color cream = Color(0xFFFAF8F5);
  static const Color warmWhite = Color(0xFFF5F3F0);
  
  /// Surfaces - soft elevation
  static const Color surface = Color(0xFFFFFFFC);
  static const Color surfaceElevated = Color(0xFFF2EFEB);
  
  /// Text - readable, not harsh
  static const Color slate = Color(0xFF3D4852);
  static const Color slateLight = Color(0xFF6B7280);
  static const Color slateMuted = Color(0xFF9CA3AF);
  
  /// Borders - subtle separation
  static const Color mist = Color(0xFFE8E6E1);
  static const Color mistDark = Color(0xFFD4D2CD);
  
  /// Secondary - supportive teal
  static const Color teal = Color(0xFF5BA8A0);
  static const Color tealLight = Color(0xFF7DBDB6);
  
  /// Accent - warm amber
  static const Color amber = Color(0xFFD4A574);
  static const Color amberLight = Color(0xFFE5C099);
  
  /// Crisis - visible but not alarming coral
  static const Color coral = Color(0xFFC97B6B);
  static const Color coralLight = Color(0xFFDEA090);
  
  /// Success - gentle green
  static const Color success = Color(0xFF6B9B7A);
  
  // ─────────────────────────────────────────────────────────────────────────
  // DARK MODE - Warm, cozy, non-depressive
  // ─────────────────────────────────────────────────────────────────────────
  
  /// Primary in dark - brighter sage
  static const Color nightSage = Color(0xFF8BA893);
  static const Color nightSageLight = Color(0xFFA3C0AB);
  
  /// Dark backgrounds - warm, not cold black
  static const Color charcoal = Color(0xFF1E2328);
  static const Color charcoalLight = Color(0xFF252A30);
  
  /// Dark surfaces - elevated
  static const Color onyx = Color(0xFF282D33);
  static const Color onyxLight = Color(0xFF353A41);
  
  /// Dark text - moonlight glow
  static const Color moonlight = Color(0xFFE5E1DB);
  static const Color moonlightDim = Color(0xFFB8B4AE);
  static const Color moonlightMuted = Color(0xFF8A8680);
  
  /// Dark borders
  static const Color shadow = Color(0xFF3A3F46);
}

// ============================================================================
// TYPOGRAPHY SYSTEM
// ============================================================================

class HopeTypography {
  HopeTypography._();
  
  /// Primary font - rounded, friendly, readable under stress
  static const String fontFamily = 'Nunito';
  static const String fontFamilyFallback = 'Inter';
  
  /// Text styles for light mode
  static TextTheme lightTextTheme = TextTheme(
    // Headlines - clear, commanding but gentle
    displayLarge: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 32,
      fontWeight: FontWeight.w700,
      letterSpacing: -0.5,
      height: 1.2,
      color: HopeColors.slate,
    ),
    displayMedium: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 28,
      fontWeight: FontWeight.w700,
      letterSpacing: -0.5,
      height: 1.25,
      color: HopeColors.slate,
    ),
    displaySmall: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 24,
      fontWeight: FontWeight.w600,
      letterSpacing: -0.25,
      height: 1.3,
      color: HopeColors.slate,
    ),
    
    // Headlines
    headlineLarge: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 22,
      fontWeight: FontWeight.w600,
      height: 1.35,
      color: HopeColors.slate,
    ),
    headlineMedium: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 20,
      fontWeight: FontWeight.w600,
      height: 1.4,
      color: HopeColors.slate,
    ),
    headlineSmall: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 18,
      fontWeight: FontWeight.w600,
      height: 1.4,
      color: HopeColors.slate,
    ),
    
    // Titles
    titleLarge: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 18,
      fontWeight: FontWeight.w600,
      height: 1.4,
      color: HopeColors.slate,
    ),
    titleMedium: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 16,
      fontWeight: FontWeight.w600,
      letterSpacing: 0.15,
      height: 1.5,
      color: HopeColors.slate,
    ),
    titleSmall: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 14,
      fontWeight: FontWeight.w600,
      letterSpacing: 0.1,
      height: 1.5,
      color: HopeColors.slate,
    ),
    
    // Body - highly readable
    bodyLarge: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 16,
      fontWeight: FontWeight.w400,
      height: 1.6,
      color: HopeColors.slate,
    ),
    bodyMedium: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 14,
      fontWeight: FontWeight.w400,
      height: 1.6,
      color: HopeColors.slateLight,
    ),
    bodySmall: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 12,
      fontWeight: FontWeight.w400,
      height: 1.5,
      color: HopeColors.slateMuted,
    ),
    
    // Labels
    labelLarge: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 16,
      fontWeight: FontWeight.w600,
      letterSpacing: 0.5,
      height: 1.4,
      color: HopeColors.slate,
    ),
    labelMedium: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 14,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.5,
      height: 1.4,
      color: HopeColors.slateLight,
    ),
    labelSmall: const TextStyle(
      fontFamily: fontFamily,
      fontSize: 12,
      fontWeight: FontWeight.w500,
      letterSpacing: 0.5,
      height: 1.4,
      color: HopeColors.slateMuted,
    ),
  );
  
  /// Text styles for dark mode
  static TextTheme darkTextTheme = TextTheme(
    displayLarge: lightTextTheme.displayLarge!.copyWith(color: HopeColors.moonlight),
    displayMedium: lightTextTheme.displayMedium!.copyWith(color: HopeColors.moonlight),
    displaySmall: lightTextTheme.displaySmall!.copyWith(color: HopeColors.moonlight),
    headlineLarge: lightTextTheme.headlineLarge!.copyWith(color: HopeColors.moonlight),
    headlineMedium: lightTextTheme.headlineMedium!.copyWith(color: HopeColors.moonlight),
    headlineSmall: lightTextTheme.headlineSmall!.copyWith(color: HopeColors.moonlight),
    titleLarge: lightTextTheme.titleLarge!.copyWith(color: HopeColors.moonlight),
    titleMedium: lightTextTheme.titleMedium!.copyWith(color: HopeColors.moonlight),
    titleSmall: lightTextTheme.titleSmall!.copyWith(color: HopeColors.moonlight),
    bodyLarge: lightTextTheme.bodyLarge!.copyWith(color: HopeColors.moonlight),
    bodyMedium: lightTextTheme.bodyMedium!.copyWith(color: HopeColors.moonlightDim),
    bodySmall: lightTextTheme.bodySmall!.copyWith(color: HopeColors.moonlightMuted),
    labelLarge: lightTextTheme.labelLarge!.copyWith(color: HopeColors.moonlight),
    labelMedium: lightTextTheme.labelMedium!.copyWith(color: HopeColors.moonlightDim),
    labelSmall: lightTextTheme.labelSmall!.copyWith(color: HopeColors.moonlightMuted),
  );
}

// ============================================================================
// SPACING & SIZING TOKENS
// ============================================================================

class HopeSpacing {
  HopeSpacing._();
  
  static const double xs = 4.0;
  static const double sm = 8.0;
  static const double md = 16.0;
  static const double lg = 24.0;
  static const double xl = 32.0;
  static const double xxl = 48.0;
  static const double xxxl = 64.0;
  
  /// Minimum touch target (accessibility)
  static const double touchTarget = 48.0;
  
  /// Panic button size
  static const double panicButton = 200.0;
  
  /// Border radii
  static const double radiusSm = 8.0;
  static const double radiusMd = 12.0;
  static const double radiusLg = 16.0;
  static const double radiusXl = 24.0;
  static const double radiusFull = 999.0;
}

// ============================================================================
// ANIMATION DURATIONS - Slow, controlled, safe
// ============================================================================

class HopeAnimations {
  HopeAnimations._();
  
  static const Duration instant = Duration(milliseconds: 100);
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 300);
  static const Duration slow = Duration(milliseconds: 500);
  static const Duration gentle = Duration(milliseconds: 800);
  static const Duration breathe = Duration(milliseconds: 3000);
  
  /// Curves - smooth, never jarring
  static const Curve easeOut = Curves.easeOutCubic;
  static const Curve easeIn = Curves.easeInCubic;
  static const Curve easeInOut = Curves.easeInOutCubic;
  static const Curve gentleCurve = Curves.easeInOutSine;
}

// ============================================================================
// SHADOWS - Soft, subtle elevation
// ============================================================================

class HopeShadows {
  HopeShadows._();
  
  static List<BoxShadow> light = [
    BoxShadow(
      color: Colors.black.withOpacity(0.04),
      blurRadius: 8,
      offset: const Offset(0, 2),
    ),
  ];
  
  static List<BoxShadow> medium = [
    BoxShadow(
      color: Colors.black.withOpacity(0.06),
      blurRadius: 16,
      offset: const Offset(0, 4),
    ),
  ];
  
  static List<BoxShadow> heavy = [
    BoxShadow(
      color: Colors.black.withOpacity(0.08),
      blurRadius: 24,
      offset: const Offset(0, 8),
    ),
  ];
  
  static List<BoxShadow> glow(Color color) => [
    BoxShadow(
      color: color.withOpacity(0.3),
      blurRadius: 24,
      spreadRadius: 4,
    ),
  ];
}

// ============================================================================
// APP THEME - Complete theme configuration
// ============================================================================

class AppTheme {
  AppTheme._();
  
  // Legacy color references for backward compatibility
  static const Color primaryLight = HopeColors.sage;
  static const Color primaryDark = HopeColors.nightSage;
  static const Color backgroundLight = HopeColors.cream;
  static const Color backgroundDark = HopeColors.charcoal;
  static const Color surfaceLight = HopeColors.surface;
  static const Color surfaceDark = HopeColors.onyx;
  static const Color textPrimaryLight = HopeColors.slate;
  static const Color textPrimaryDark = HopeColors.moonlight;
  static const Color panicAccent = HopeColors.sage;
  static const Color crisisColor = HopeColors.coral;
  static const Color calmColor = HopeColors.success;
  
  static const String fontFamily = HopeTypography.fontFamily;
  
  // ─────────────────────────────────────────────────────────────────────────
  // LIGHT THEME - Warm, inviting, professional
  // ─────────────────────────────────────────────────────────────────────────
  
  static ThemeData lightTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,
    fontFamily: HopeTypography.fontFamily,
    
    // Colors
    primaryColor: HopeColors.sage,
    scaffoldBackgroundColor: HopeColors.cream,
    
    colorScheme: const ColorScheme.light(
      primary: HopeColors.sage,
      onPrimary: Colors.white,
      primaryContainer: HopeColors.sageLight,
      onPrimaryContainer: HopeColors.sageDark,
      secondary: HopeColors.teal,
      onSecondary: Colors.white,
      secondaryContainer: HopeColors.tealLight,
      tertiary: HopeColors.amber,
      tertiaryContainer: HopeColors.amberLight,
      surface: HopeColors.surface,
      onSurface: HopeColors.slate,
      surfaceContainerHighest: HopeColors.surfaceElevated,
      error: HopeColors.coral,
      onError: Colors.white,
      outline: HopeColors.mist,
      outlineVariant: HopeColors.mistDark,
    ),
    
    // Text
    textTheme: HopeTypography.lightTextTheme,
    
    // AppBar
    appBarTheme: const AppBarTheme(
      backgroundColor: HopeColors.cream,
      foregroundColor: HopeColors.slate,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontFamily: HopeTypography.fontFamily,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: HopeColors.slate,
      ),
      systemOverlayStyle: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.dark,
        statusBarBrightness: Brightness.light,
      ),
    ),
    
    // Buttons
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: HopeColors.sage,
        foregroundColor: Colors.white,
        minimumSize: const Size(double.infinity, 56),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        textStyle: const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 16,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
    ),
    
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: HopeColors.sage,
        minimumSize: const Size(double.infinity, 56),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        side: const BorderSide(color: HopeColors.sage, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        textStyle: const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 16,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
    ),
    
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: HopeColors.sage,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        textStyle: const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    
    // Input
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: HopeColors.surfaceElevated,
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: const BorderSide(color: HopeColors.sage, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: const BorderSide(color: HopeColors.coral, width: 1.5),
      ),
      hintStyle: const TextStyle(
        fontFamily: HopeTypography.fontFamily,
        color: HopeColors.slateMuted,
      ),
    ),
    
    // Cards
    cardTheme: CardThemeData(
      color: HopeColors.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusLg),
      ),
      margin: EdgeInsets.zero,
    ),
    
    // Bottom Navigation
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: HopeColors.surface,
      indicatorColor: HopeColors.sageLight.withOpacity(0.3),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(
            fontFamily: HopeTypography.fontFamily,
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: HopeColors.sage,
          );
        }
        return const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: HopeColors.slateMuted,
        );
      }),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: HopeColors.sage, size: 24);
        }
        return const IconThemeData(color: HopeColors.slateMuted, size: 24);
      }),
    ),
    
    // Divider
    dividerTheme: const DividerThemeData(
      color: HopeColors.mist,
      thickness: 1,
      space: 1,
    ),
    
    // Snackbar
    snackBarTheme: SnackBarThemeData(
      backgroundColor: HopeColors.slate,
      contentTextStyle: const TextStyle(
        fontFamily: HopeTypography.fontFamily,
        color: Colors.white,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
      ),
      behavior: SnackBarBehavior.floating,
    ),
    
    // Dialog
    dialogTheme: DialogThemeData(
      backgroundColor: HopeColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
      ),
      titleTextStyle: const TextStyle(
        fontFamily: HopeTypography.fontFamily,
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: HopeColors.slate,
      ),
    ),
    
    // Bottom Sheet
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: HopeColors.surface,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
    ),
    
    // Slider
    sliderTheme: SliderThemeData(
      activeTrackColor: HopeColors.sage,
      inactiveTrackColor: HopeColors.mist,
      thumbColor: HopeColors.sage,
      overlayColor: HopeColors.sage.withOpacity(0.12),
      trackHeight: 6,
      thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 10),
    ),
    
    // Switch
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return HopeColors.sage;
        }
        return HopeColors.slateMuted;
      }),
      trackColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return HopeColors.sageLight;
        }
        return HopeColors.mist;
      }),
    ),
  );
  
  // ─────────────────────────────────────────────────────────────────────────
  // DARK THEME - Warm, cozy, non-depressive
  // ─────────────────────────────────────────────────────────────────────────
  
  static ThemeData darkTheme = ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    fontFamily: HopeTypography.fontFamily,
    
    // Colors
    primaryColor: HopeColors.nightSage,
    scaffoldBackgroundColor: HopeColors.charcoal,
    
    colorScheme: const ColorScheme.dark(
      primary: HopeColors.nightSage,
      onPrimary: HopeColors.charcoal,
      primaryContainer: HopeColors.sageDark,
      secondary: HopeColors.teal,
      onSecondary: HopeColors.charcoal,
      tertiary: HopeColors.amber,
      surface: HopeColors.onyx,
      onSurface: HopeColors.moonlight,
      surfaceContainerHighest: HopeColors.onyxLight,
      error: HopeColors.coralLight,
      onError: HopeColors.charcoal,
      outline: HopeColors.shadow,
    ),
    
    // Text
    textTheme: HopeTypography.darkTextTheme,
    
    // AppBar
    appBarTheme: const AppBarTheme(
      backgroundColor: HopeColors.charcoal,
      foregroundColor: HopeColors.moonlight,
      elevation: 0,
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontFamily: HopeTypography.fontFamily,
        fontSize: 18,
        fontWeight: FontWeight.w600,
        color: HopeColors.moonlight,
      ),
      systemOverlayStyle: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        statusBarBrightness: Brightness.dark,
      ),
    ),
    
    // Buttons
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: HopeColors.nightSage,
        foregroundColor: HopeColors.charcoal,
        minimumSize: const Size(double.infinity, 56),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        textStyle: const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 16,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
    ),
    
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: HopeColors.nightSage,
        minimumSize: const Size(double.infinity, 56),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        side: const BorderSide(color: HopeColors.nightSage, width: 1.5),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
        ),
        textStyle: const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 16,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.5,
        ),
      ),
    ),
    
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(
        foregroundColor: HopeColors.nightSage,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        textStyle: const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 14,
          fontWeight: FontWeight.w600,
        ),
      ),
    ),
    
    // Input
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: HopeColors.onyxLight,
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: BorderSide.none,
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: const BorderSide(color: HopeColors.nightSage, width: 2),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
        borderSide: const BorderSide(color: HopeColors.coralLight, width: 1.5),
      ),
      hintStyle: const TextStyle(
        fontFamily: HopeTypography.fontFamily,
        color: HopeColors.moonlightMuted,
      ),
    ),
    
    // Cards
    cardTheme: CardThemeData(
      color: HopeColors.onyx,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusLg),
      ),
      margin: EdgeInsets.zero,
    ),
    
    // Bottom Navigation
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: HopeColors.onyx,
      indicatorColor: HopeColors.nightSage.withOpacity(0.2),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(
            fontFamily: HopeTypography.fontFamily,
            fontSize: 12,
            fontWeight: FontWeight.w600,
            color: HopeColors.nightSage,
          );
        }
        return const TextStyle(
          fontFamily: HopeTypography.fontFamily,
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: HopeColors.moonlightMuted,
        );
      }),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: HopeColors.nightSage, size: 24);
        }
        return const IconThemeData(color: HopeColors.moonlightMuted, size: 24);
      }),
    ),
    
    // Divider
    dividerTheme: const DividerThemeData(
      color: HopeColors.shadow,
      thickness: 1,
      space: 1,
    ),
    
    // Snackbar
    snackBarTheme: SnackBarThemeData(
      backgroundColor: HopeColors.onyxLight,
      contentTextStyle: const TextStyle(
        fontFamily: HopeTypography.fontFamily,
        color: HopeColors.moonlight,
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusMd),
      ),
      behavior: SnackBarBehavior.floating,
    ),
    
    // Dialog
    dialogTheme: DialogThemeData(
      backgroundColor: HopeColors.onyx,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(HopeSpacing.radiusXl),
      ),
      titleTextStyle: const TextStyle(
        fontFamily: HopeTypography.fontFamily,
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: HopeColors.moonlight,
      ),
    ),
    
    // Bottom Sheet
    bottomSheetTheme: const BottomSheetThemeData(
      backgroundColor: HopeColors.onyx,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
    ),
    
    // Slider
    sliderTheme: SliderThemeData(
      activeTrackColor: HopeColors.nightSage,
      inactiveTrackColor: HopeColors.shadow,
      thumbColor: HopeColors.nightSage,
      overlayColor: HopeColors.nightSage.withOpacity(0.12),
      trackHeight: 6,
      thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 10),
    ),
    
    // Switch
    switchTheme: SwitchThemeData(
      thumbColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return HopeColors.nightSage;
        }
        return HopeColors.moonlightMuted;
      }),
      trackColor: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return HopeColors.sageDark;
        }
        return HopeColors.shadow;
      }),
    ),
  );
}

// ============================================================================
// PANIC UI CONSTANTS - Accessibility & sizing
// ============================================================================

class PanicUiConstants {
  PanicUiConstants._();
  
  static const double minTouchTarget = HopeSpacing.touchTarget;
  static const double panicButtonSize = HopeSpacing.panicButton;
  static const double paddingSmall = HopeSpacing.sm;
  static const double paddingMedium = HopeSpacing.md;
  static const double paddingLarge = HopeSpacing.lg;
  static const Duration fadeIn = Duration(milliseconds: 400);
  static const Duration fadeOut = Duration(milliseconds: 300);
}
