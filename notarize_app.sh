#!/bin/bash

# Script to notarize the app with Apple

# Configuration - replace with your information
APPLE_ID="your.email@example.com"
TEAM_ID="XXXXXXXXXX"  # Your Apple Developer Team ID
APP_ID="com.ericspencer.dexcomnavbaricon"
PASSWORD="@keychain:AC_PASSWORD"  # App-specific password stored in keychain

# Create a zip of the app for notarization
echo "Creating zip archive for notarization..."
ditto -c -k --keepParent dist/DexcomNavBarIcon.app DexcomNavBarIcon.zip

# Submit to Apple for notarization
echo "Submitting app for notarization..."
xcrun notarytool submit DexcomNavBarIcon.zip \
  --apple-id "$APPLE_ID" \
  --team-id "$TEAM_ID" \
  --password "$PASSWORD" \
  --wait

# Staple the notarization ticket to the app
echo "Stapling notarization ticket to app..."
xcrun stapler staple dist/DexcomNavBarIcon.app

# Create a new DMG with the notarized app
echo "Creating new DMG with notarized app..."
./create_dmg.sh

# Check the notarization status
echo "Checking notarization status..."
spctl -a -v dist/DexcomNavBarIcon.app

echo "Notarization complete!"
