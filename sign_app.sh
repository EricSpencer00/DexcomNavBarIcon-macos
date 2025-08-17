#!/bin/bash

# Script to build and sign the app with your Developer ID

# Configuration - replace with your information
DEVELOPER_ID="Developer ID Application: Your Name (XXXXXXXXXX)"
TEAM_ID="XXXXXXXXXX"  # Your Apple Developer Team ID
APP_ID="com.ericspencer.dexcomnavbaricon"

# Clean up previous builds
echo "Cleaning up previous builds..."
rm -rf build dist

# Build the app
echo "Building app with py2app..."
python setup.py py2app

# Sign the app and its contents
echo "Signing the app with Developer ID..."
codesign --force --options runtime --deep --sign "$DEVELOPER_ID" dist/DexcomNavBarIcon.app

# Verify the signature
echo "Verifying signature..."
codesign --verify --verbose dist/DexcomNavBarIcon.app

# Create the DMG
echo "Creating DMG..."
./create_dmg.sh

# Sign the DMG
echo "Signing the DMG..."
codesign --force --sign "$DEVELOPER_ID" DexcomNavBarIcon.dmg

echo "App and DMG signed successfully!"
echo "To notarize the app, run: ./notarize_app.sh"
