#!/bin/bash

# Clean up any existing DMG
rm -f DexcomNavBarIcon.dmg

# Create a temporary directory for DMG contents
mkdir -p dmg_temp

# Copy the app to the temporary directory
cp -R "dist/DexcomNavBarIcon.app" dmg_temp/

# Create a symbolic link to Applications
ln -s /Applications dmg_temp/Applications

# Create the DMG
hdiutil create -volname "DexcomNavBarIcon" -srcfolder dmg_temp -ov -format UDZO DexcomNavBarIcon.dmg

# Clean up
rm -rf dmg_temp

echo "DMG created successfully: DexcomNavBarIcon.dmg"
