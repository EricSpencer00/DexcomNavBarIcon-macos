#!/bin/bash

# Build script for App Store submission

# Configuration - replace with your information
DEVELOPER_ID="3rd Party Mac Developer Application: Your Name (XXXXXXXXXX)"
INSTALLER_ID="3rd Party Mac Developer Installer: Your Name (XXXXXXXXXX)"
TEAM_ID="XXXXXXXXXX"  # Your Apple Developer Team ID
APP_ID="com.ericspencer.dexcomnavbaricon"

echo "Cleaning up previous builds..."
rm -rf build dist DexcomNavBarIcon_AppStore DexcomNavBarIcon.pkg

echo "Installing required dependencies..."
pip install -r requirements_simplified.txt

echo "Building app with py2app in production mode..."
python setup_simplified.py py2app

echo "Signing application with App Store certificate..."
codesign --force --options runtime --deep --sign "$DEVELOPER_ID" --entitlements "entitlements.plist" dist/DexcomNavBarIcon.app

echo "Verifying code signature..."
codesign --verify --verbose dist/DexcomNavBarIcon.app

echo "Packaging app for App Store..."
# Create a directory for the package
mkdir -p DexcomNavBarIcon_AppStore

# Copy the app to the package directory
cp -R dist/DexcomNavBarIcon.app DexcomNavBarIcon_AppStore/

# Copy the icon for App Store
cp resources/icon.png DexcomNavBarIcon_AppStore/AppIcon.png

# Create a pkg installer for App Store submission
productbuild --component dist/DexcomNavBarIcon.app /Applications \
  --sign "$INSTALLER_ID" \
  DexcomNavBarIcon.pkg

echo "Build complete! App is ready for App Store submission."
echo "Please submit the DexcomNavBarIcon.pkg file to App Store Connect."
