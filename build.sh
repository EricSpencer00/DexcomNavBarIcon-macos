#!/bin/bash

# Ensure the script exits if any command fails
set -e

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

APP_NAME="DexcomNavBarIcon"
APP_BUNDLE_ID="com.ericspencer.dexcomnavbaricon"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}.dmg"
PKG_NAME="${APP_NAME}.pkg"
ENTITLEMENTS="entitlements.plist"

# Certificate placeholders (replace before running for MAS builds)
APP_CERT="Developer ID Application: Eric Spencer (QAWD9U9CF6)"
INSTALLER_CERT="Developer ID Installer: Eric Spencer (QAWD9U9CF6)"

# Step 1: Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist "$DMG_NAME" "$PKG_NAME" venv_universal

# Step 2: Set up virtual environment ONCE (prefer PYTHON_BIN if provided)
PY_BIN="${PYTHON_BIN:-python3.9}"
echo "Using Python: ${PY_BIN}"
"${PY_BIN}" -m venv venv_universal
source venv_universal/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Step 2: Check for required tools and files
echo "Checking for required tools and files..."
if ! command -v "${PY_BIN}" >/dev/null 2>&1; then
  echo "Error: ${PY_BIN} not found. Please install the official universal2 Python 3.9+ from python.org." >&2
  exit 1
fi
if ! "${PY_BIN}" -c "import platform; print(platform.machine())" 2>/dev/null | grep -Eq 'x86_64|arm64'; then
  echo "Warning: Your python3.9 may not be the official universal2 build. Universal2 is required for both Intel and Apple Silicon support." >&2
fi
if ! python -m pip show py2app >/dev/null 2>&1; then
  echo "Error: py2app is not installed in the venv. Run: python -m pip install py2app" >&2
  exit 1
fi
if [ ! -f requirements.txt ]; then
  echo "Error: requirements.txt not found in project root." >&2
  exit 1
fi

# Step 3: Build the universal2 app
echo "Building universal2 (Intel + Apple Silicon) version..."
# If APP_VERSION is provided, it will be embedded via setup.py plist
python setup.py py2app

# Step 3: Verify the built application exists
if [ ! -d "$APP_PATH" ]; then
  echo "Error: $APP_PATH not found" >&2
  exit 1
fi


# Sign all .so and .dylib files in Resources and Frameworks (no entitlements)
echo "Signing all .so and .dylib files in Resources and Frameworks..."
SIGNED=0
if security find-identity -v -p codesigning | grep -q "$APP_CERT"; then
  find "$APP_PATH/Contents/Resources" -name "*.so" -or -name "*.dylib" | while read -r f; do
    codesign --force --options runtime --sign "$APP_CERT" "$f"
  done
  if [ -d "$APP_PATH/Contents/Frameworks" ]; then
    find "$APP_PATH/Contents/Frameworks" -name "*.so" -or -name "*.dylib" | while read -r f; do
      codesign --force --options runtime --sign "$APP_CERT" "$f"
    done
  fi
  # Now sign the main app bundle
  echo "Code signing app bundle (Developer ID)..."
  codesign --force --deep --options runtime \
    --entitlements "$ENTITLEMENTS" \
    --sign "$APP_CERT" "$APP_PATH"
  SIGNED=1
else
  echo "Warning: Developer ID Application certificate not found. Skipping signing."
fi

# Verify signature (if signed)
if codesign --verify --deep --strict --verbose=2 "$APP_PATH"; then
  echo "Codesign verification passed."
else
  echo "Warning: codesign verification failed or app not signed."
fi


# Step 5: Create the DMG using hdiutil
echo "Creating DMG for universal2 app..."
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_NAME"


# Optionally create a signed installer package for App Store upload
# Note: App Store typically requires submission via Xcode or Transporter with a signed app archive.
# The following can help validate entitlements in a pkg, but use at your discretion.
if [ "$CREATE_PKG" = "1" ]; then
  echo "Looking for installer signing identity: $INSTALLER_CERT"
  security find-identity -v -p codesigning
  if security find-identity -v -p codesigning | grep -Fxq "$INSTALLER_CERT"; then
    echo "Building signed installer package..."
    productbuild --component "$APP_PATH" \
      "/Applications" \
      --sign "$INSTALLER_CERT" \
      "$PKG_NAME" || echo "productbuild failed; ensure correct certificate and product definition."
  else
    echo "Note: Installer signing certificate not found. Skipping pkg creation."
  fi
else
  echo "Skipping .pkg creation (set CREATE_PKG=1 to enable)."
fi

# Step 6: Notarize the DMG (optional; only if signed and creds present)
if [ "$SIGNED" = "1" ] && [ -n "$NOTARIZE_APPLE_ID" ] && [ -n "$NOTARIZE_TEAM_ID" ] && [ -n "$NOTARIZE_APP_SPECIFIC_PASSWORD" ]; then
  echo "Submitting DMG for notarization..."
  xcrun notarytool submit "$DMG_NAME" \
    --apple-id "$NOTARIZE_APPLE_ID" \
    --team-id "$NOTARIZE_TEAM_ID" \
    --password "$NOTARIZE_APP_SPECIFIC_PASSWORD" \
    --wait
  echo "Stapling notarization ticket to DMG..."
  xcrun stapler staple "$DMG_NAME"
  echo "Notarization complete."
else
  echo "Notarization skipped. Ensure app is signed and notarization credentials are set."
fi

echo "Build and packaging complete."
echo "DMG created: ${DMG_NAME} (universal2: Intel + Apple Silicon)"

# Step 7: Clean up virtual environment
rm -rf venv_universal
