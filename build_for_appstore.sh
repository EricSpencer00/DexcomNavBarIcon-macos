#!/bin/bash

# Build script for App Store submission

echo "Cleaning up previous builds..."
rm -rf build dist

echo "Installing required dependencies..."
pip install -r requirements_simplified.txt

echo "Building app with py2app in production mode..."
python setup_simplified.py py2app

echo "Checking code signature requirements..."
codesign --verify --verbose dist/DexcomNavBarIcon.app

echo "Packaging app for App Store..."
# Create a directory for the package
mkdir -p DexcomNavBarIcon_AppStore

# Copy the app to the package directory
cp -R dist/DexcomNavBarIcon.app DexcomNavBarIcon_AppStore/

# Copy the icon for App Store
cp resources/icon.png DexcomNavBarIcon_AppStore/AppIcon.png

echo "Build complete! App is ready for App Store submission."
echo "Please submit the DexcomNavBarIcon_AppStore directory to App Store Connect."
