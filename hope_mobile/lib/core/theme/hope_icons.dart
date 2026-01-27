/// HOPE Icon System
/// 
/// Centralized icon components for the HOPE mental health app.
/// Uses custom-painted butterfly icon as the primary branding element.
/// 
/// The butterfly symbolizes:
/// - Transformation and growth
/// - Hope and new beginnings
/// - Lightness and calm
/// - Gentle resilience

import 'package:flutter/material.dart';
import 'app_theme.dart';

/// Custom icon set for HOPE app
class HopeIcons {
  HopeIcons._();
  
  /// Primary butterfly icon - the heart of HOPE branding
  /// 
  /// Use this instead of heart icons throughout the app.
  /// Represents hope, transformation, and gentle support.
  static Widget butterfly({
    double size = 24.0,
    Color? color,
  }) {
    return _ButterflyIcon(size: size, color: color);
  }
  
  /// Animated butterfly with gentle floating motion
  /// 
  /// Use for empty states, loading, or celebratory moments.
  static Widget butterflyAnimated({
    double size = 24.0,
    Color? color,
    Duration duration = const Duration(seconds: 3),
  }) {
    return _AnimatedButterflyIcon(
      size: size,
      color: color,
      duration: duration,
    );
  }
}

/// Static butterfly icon widget
class _ButterflyIcon extends StatelessWidget {
  final double size;
  final Color? color;
  
  const _ButterflyIcon({
    required this.size,
    this.color,
  });
  
  @override
  Widget build(BuildContext context) {
    final iconColor = color ?? Theme.of(context).colorScheme.primary;
    
    return SizedBox(
      width: size,
      height: size,
      child: CustomPaint(
        size: Size(size, size),
        painter: _ButterflyPainter(color: iconColor),
      ),
    );
  }
}

/// Animated butterfly with gentle floating motion
class _AnimatedButterflyIcon extends StatefulWidget {
  final double size;
  final Color? color;
  final Duration duration;
  
  const _AnimatedButterflyIcon({
    required this.size,
    this.color,
    required this.duration,
  });
  
  @override
  State<_AnimatedButterflyIcon> createState() => _AnimatedButterflyIconState();
}

class _AnimatedButterflyIconState extends State<_AnimatedButterflyIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: widget.duration,
      vsync: this,
    )..repeat(reverse: true);
    
    _scaleAnimation = Tween<double>(
      begin: 0.95,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeInOutSine,
    ));
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: _ButterflyIcon(
            size: widget.size,
            color: widget.color,
          ),
        );
      },
    );
  }
}

/// Custom painter for butterfly icon
/// 
/// Draws a minimal, elegant butterfly silhouette
/// with smooth curves and balanced proportions.
class _ButterflyPainter extends CustomPainter {
  final Color color;
  
  _ButterflyPainter({required this.color});
  
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;
    
    final w = size.width;
    final h = size.height;
    final cx = w / 2;
    final cy = h / 2;
    
    // Scale factor for proportions
    final scale = w / 24.0;
    
    // Left upper wing
    final leftUpperWing = Path();
    leftUpperWing.moveTo(cx, cy - 1 * scale);
    leftUpperWing.cubicTo(
      cx - 4 * scale, cy - 6 * scale,
      cx - 10 * scale, cy - 8 * scale,
      cx - 9 * scale, cy - 2 * scale,
    );
    leftUpperWing.cubicTo(
      cx - 10 * scale, cy + 1 * scale,
      cx - 6 * scale, cy + 2 * scale,
      cx, cy,
    );
    leftUpperWing.close();
    
    // Left lower wing
    final leftLowerWing = Path();
    leftLowerWing.moveTo(cx, cy);
    leftLowerWing.cubicTo(
      cx - 5 * scale, cy + 2 * scale,
      cx - 8 * scale, cy + 4 * scale,
      cx - 7 * scale, cy + 7 * scale,
    );
    leftLowerWing.cubicTo(
      cx - 5 * scale, cy + 9 * scale,
      cx - 2 * scale, cy + 6 * scale,
      cx, cy + 2 * scale,
    );
    leftLowerWing.close();
    
    // Right upper wing (mirrored)
    final rightUpperWing = Path();
    rightUpperWing.moveTo(cx, cy - 1 * scale);
    rightUpperWing.cubicTo(
      cx + 4 * scale, cy - 6 * scale,
      cx + 10 * scale, cy - 8 * scale,
      cx + 9 * scale, cy - 2 * scale,
    );
    rightUpperWing.cubicTo(
      cx + 10 * scale, cy + 1 * scale,
      cx + 6 * scale, cy + 2 * scale,
      cx, cy,
    );
    rightUpperWing.close();
    
    // Right lower wing (mirrored)
    final rightLowerWing = Path();
    rightLowerWing.moveTo(cx, cy);
    rightLowerWing.cubicTo(
      cx + 5 * scale, cy + 2 * scale,
      cx + 8 * scale, cy + 4 * scale,
      cx + 7 * scale, cy + 7 * scale,
    );
    rightLowerWing.cubicTo(
      cx + 5 * scale, cy + 9 * scale,
      cx + 2 * scale, cy + 6 * scale,
      cx, cy + 2 * scale,
    );
    rightLowerWing.close();
    
    // Body
    final body = Path();
    body.addOval(Rect.fromCenter(
      center: Offset(cx, cy),
      width: 2 * scale,
      height: 8 * scale,
    ));
    
    // Draw all parts
    canvas.drawPath(leftUpperWing, paint);
    canvas.drawPath(leftLowerWing, paint);
    canvas.drawPath(rightUpperWing, paint);
    canvas.drawPath(rightLowerWing, paint);
    canvas.drawPath(body, paint);
    
    // Antennae
    final antennaPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.2 * scale
      ..strokeCap = StrokeCap.round;
    
    // Left antenna
    canvas.drawLine(
      Offset(cx - 0.5 * scale, cy - 4 * scale),
      Offset(cx - 2 * scale, cy - 7 * scale),
      antennaPaint,
    );
    
    // Right antenna
    canvas.drawLine(
      Offset(cx + 0.5 * scale, cy - 4 * scale),
      Offset(cx + 2 * scale, cy - 7 * scale),
      antennaPaint,
    );
  }
  
  @override
  bool shouldRepaint(covariant _ButterflyPainter oldDelegate) {
    return oldDelegate.color != color;
  }
}
