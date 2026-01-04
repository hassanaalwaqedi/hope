/// Grounding Exercise - 5-4-3-2-1 Technique
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../core/theme/app_theme.dart';

class GroundingExercise extends StatefulWidget {
  const GroundingExercise({super.key});

  @override
  State<GroundingExercise> createState() => _GroundingExerciseState();
}

class _GroundingExerciseState extends State<GroundingExercise> {
  int _currentStep = 0;
  final List<bool> _completed = [false, false, false, false, false];
  
  static const List<_GroundingStep> _steps = [
    _GroundingStep(
      count: 5,
      sense: 'SEE',
      icon: Icons.visibility,
      instruction: 'Name 5 things you can see right now',
      examples: ['A lamp', 'Your phone', 'A window', 'Your hands', 'A wall'],
      color: Color(0xFF6B7FD7),
    ),
    _GroundingStep(
      count: 4,
      sense: 'TOUCH',
      icon: Icons.touch_app,
      instruction: 'Name 4 things you can touch',
      examples: ['Your clothes', 'The floor', 'A chair', 'Your hair'],
      color: Color(0xFF7C9A92),
    ),
    _GroundingStep(
      count: 3,
      sense: 'HEAR',
      icon: Icons.hearing,
      instruction: 'Name 3 things you can hear',
      examples: ['Birds', 'Traffic', 'Your breathing'],
      color: Color(0xFFD4A373),
    ),
    _GroundingStep(
      count: 2,
      sense: 'SMELL',
      icon: Icons.air,
      instruction: 'Name 2 things you can smell',
      examples: ['Fresh air', 'Coffee'],
      color: Color(0xFFE9C46A),
    ),
    _GroundingStep(
      count: 1,
      sense: 'TASTE',
      icon: Icons.restaurant,
      instruction: 'Name 1 thing you can taste',
      examples: ['Your mouth'],
      color: Color(0xFFE76F51),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    final step = _steps[_currentStep];
    
    return SingleChildScrollView(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
        // Progress dots
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(5, (index) {
            return Container(
              margin: const EdgeInsets.symmetric(horizontal: 6),
              width: _completed[index] ? 12 : 10,
              height: _completed[index] ? 12 : 10,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: _completed[index]
                    ? AppTheme.calmColor
                    : index == _currentStep
                        ? step.color
                        : Colors.grey.withOpacity(0.3),
                border: index == _currentStep
                    ? Border.all(color: step.color, width: 2)
                    : null,
              ),
            );
          }),
        ),
        
        const SizedBox(height: 32),
        
        // Count circle
        AnimatedContainer(
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeOutBack,
          width: 120,
          height: 120,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: step.color.withOpacity(0.2),
            border: Border.all(color: step.color, width: 3),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                '${step.count}',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: step.color,
                ),
              ),
              Text(
                step.sense,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: step.color,
                  letterSpacing: 2,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Instruction
        Text(
          step.instruction,
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
        
        const SizedBox(height: 16),
        
        // Examples
        Wrap(
          alignment: WrapAlignment.center,
          spacing: 8,
          runSpacing: 8,
          children: step.examples.map((example) {
            return Chip(
              label: Text(example),
              backgroundColor: step.color.withOpacity(0.1),
              side: BorderSide.none,
            );
          }).toList(),
        ),
        
        const SizedBox(height: 32),
        
        // Navigation
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            if (_currentStep > 0)
              IconButton.outlined(
                onPressed: _previousStep,
                icon: const Icon(Icons.arrow_back),
              ),
            const SizedBox(width: 24),
            ElevatedButton.icon(
              onPressed: _nextStep,
              icon: Icon(_currentStep < 4 ? Icons.check : Icons.done_all),
              label: Text(_currentStep < 4 ? 'Done, next' : 'Complete'),
              style: ElevatedButton.styleFrom(
                backgroundColor: step.color,
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              ),
            ),
          ],
        ),
      ],
      ),
    );
  }

  void _previousStep() {
    if (_currentStep > 0) {
      HapticFeedback.selectionClick();
      setState(() => _currentStep--);
    }
  }

  void _nextStep() {
    HapticFeedback.mediumImpact();
    setState(() {
      _completed[_currentStep] = true;
      if (_currentStep < 4) {
        _currentStep++;
      } else {
        // All done - reset
        _currentStep = 0;
        for (int i = 0; i < 5; i++) {
          _completed[i] = false;
        }
      }
    });
  }
}

class _GroundingStep {
  final int count;
  final String sense;
  final IconData icon;
  final String instruction;
  final List<String> examples;
  final Color color;

  const _GroundingStep({
    required this.count,
    required this.sense,
    required this.icon,
    required this.instruction,
    required this.examples,
    required this.color,
  });
}
