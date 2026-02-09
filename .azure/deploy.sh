#!/bin/bash
# Azure Oryx Pre-Build Script
# This runs before the app starts to install the hope package

echo "Installing hope package in editable mode..."
pip install -e .

echo "Package installation complete!"
