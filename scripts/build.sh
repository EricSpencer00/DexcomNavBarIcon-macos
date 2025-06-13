#!/bin/bash

# Ensure the script exits if any command fails
set -e

# Step 1: Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist DexcomNavBarIcon.dmg

# Step 2: Build the application with py2app
echo "Building the application..."
python setup.py py2app

# Step 3: Define variables
APP_NAME="DexcomNavBarIcon"
APP_PATH="dist/${APP_NAME}.app"
DMG_NAME="${APP_NAME}.dmg"

# Step 4: Verify the built application exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: Application build failed or ${APP_PATH} does not exist."
    exit 1
fi

# Step 5: Create the DMG using hdiutil
echo "Creating DMG..."
hdiutil create -volname "$APP_NAME" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_NAME"

# Step 6: Open (mount) the DMG
echo "Opening DMG..."
hdiutil attach "$DMG_NAME"

echo "Build and packaging complete. DMG located at ${DMG_NAME}"
