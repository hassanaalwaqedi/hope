/// Intensity Slider - User panic intensity reporting
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class IntensitySlider extends StatelessWidget {
  final double value;
  final ValueChanged<double> onChanged;

  const IntensitySlider({
    super.key,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getColorForIntensity(value);
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'How intense is it right now?',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${value.round()}/10',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: color,
              inactiveTrackColor: color.withOpacity(0.2),
              thumbColor: color,
              overlayColor: color.withOpacity(0.2),
              trackHeight: 8,
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 12),
            ),
            child: Slider(
              value: value,
              min: 1,
              max: 10,
              divisions: 9,
              onChanged: (newValue) {
                HapticFeedback.selectionClick();
                onChanged(newValue);
              },
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Manageable',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFF059669),
                ),
              ),
              Text(
                'Overwhelming',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: const Color(0xFFDC2626),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _getColorForIntensity(double value) {
    if (value <= 3) {
      return const Color(0xFF059669); // Green
    } else if (value <= 5) {
      return const Color(0xFFD97706); // Amber
    } else if (value <= 7) {
      return const Color(0xFFEA580C); // Orange
    } else {
      return const Color(0xFFDC2626); // Red
    }
  }
}
