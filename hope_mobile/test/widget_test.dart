// HOPE Mobile Widget Tests

import 'package:flutter_test/flutter_test.dart';
import 'package:hope_mobile/main.dart';

void main() {
  testWidgets('Home screen displays panic button', (WidgetTester tester) async {
    await tester.pumpWidget(const HopeApp());
    
    // Verify app loads with HOPE title
    expect(find.text('HOPE'), findsOneWidget);
    
    // Verify panic button exists
    expect(find.text('I need\nhelp'), findsOneWidget);
  });
}

