#!/bin/bash
# Azure App Service Startup Script
# This ensures the hope package is installed before starting the app

echo "=== HOPE Backend Startup ==="

# Install the hope package in editable mode
echo "Installing hope package..."
cd /home/site/wwwroot
pip install -e . --no-cache-dir

# Set PYTHONPATH to include the src directory
export PYTHONPATH=/home/site/wwwroot/src:$PYTHONPATH

# Start the application
echo "Starting Uvicorn..."
exec python -m uvicorn hope.main:app --host 0.0.0.0 --port 8000
