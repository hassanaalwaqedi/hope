#!/bin/bash

echo "Installing Flutter..."
git clone https://github.com/flutter/flutter.git -b stable --depth 1 _flutter
export PATH="$PATH:`pwd`/_flutter/bin"

echo "Flutter installed:"
flutter --version

echo "Building Web App..."
cd hope_mobile
flutter config --no-analytics
flutter build web --release --no-tree-shake-icons --dart-define=API_BASE_URL=https://hope-api.azurewebsites.net

echo "Build complete."
