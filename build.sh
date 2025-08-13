#!/bin/bash

# Ensure the script exits if any command fails
set -e

APP_NAME="DexcomNavBarIcon"
APP_BUNDLE_ID="com.ericspencer.dexcomnavbaricon"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}.dmg"
PKG_NAME="${APP_NAME}.pkg"
ENTITLEMENTS="entitlements.plist"

# Certificate placeholders (replace before running for MAS builds)
APP_CERT="3rd Party Mac Developer Application: Your Name (TEAMID)"
INSTALLER_CERT="3rd Party Mac Developer Installer: Your Name (TEAMID)"

# Step 1: Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "$DMG_NAME" "$PKG_NAME"

# Step 2: Build the application with py2app
echo "Building the application with py2app..."
python3 setup.py py2app

# Step 3: Verify the built application exists
if [ ! -d "$APP_PATH" ]; then
  echo "Error: $APP_PATH not found" >&2
  exit 1
fi

# Sign for Mac App Store (comment out if only testing locally)
echo "Code signing app bundle (MAS)..."
if security find-identity -v -p codesigning | grep -q "$APP_CERT"; then
  codesign --force --deep --options runtime \
    --entitlements "$ENTITLEMENTS" \
    --sign "$APP_CERT" "$APP_PATH"
else
  echo "Warning: App Store signing certificate not found. Skipping signing."
fi

# Verify signature (if signed)
if codesign --verify --deep --strict --verbose=2 "$APP_PATH"; then
  echo "Codesign verification passed."
else
  echo "Warning: codesign verification failed or app not signed."
fi

# Step 4: Create the DMG using hdiutil
echo "Creating DMG..."
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_NAME"

# Optionally create a signed installer package for App Store upload
# Note: App Store typically requires submission via Xcode or Transporter with a signed app archive.
# The following can help validate entitlements in a pkg, but use at your discretion.
if security find-identity -v -p codesigning | grep -q "$INSTALLER_CERT"; then
  echo "Building signed installer package..."
  productbuild --component "$APP_PATH" \
    "/Applications" \
    --sign "$INSTALLER_CERT" \
    --product "" \
    "$PKG_NAME" || echo "productbuild failed; ensure correct certificate and product definition."
else
  echo "Note: Installer signing certificate not found. Skipping pkg creation."
fi

echo "Build and packaging complete. DMG located at ${DMG_NAME}"
