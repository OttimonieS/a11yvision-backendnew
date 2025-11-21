#!/bin/bash

# Render build script for A11y Vision Backend

echo "Starting build process..."

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Install Playwright browsers (only chromium to save space)
echo "Installing Playwright browsers..."
playwright install --with-deps chromium

echo "Build completed successfully!"
