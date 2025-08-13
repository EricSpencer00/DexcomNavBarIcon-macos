#!/bin/bash

# Migration script to convert to App Store version

echo "Starting migration to App Store version..."

# Create backup of original files
echo "Creating backup of original files..."
mkdir -p backup
cp main.py setup.py requirements.txt create_dmg.sh README.md backup/
cp -r src backup/

# Rename simplified files to replace originals
echo "Replacing files with simplified versions..."
mv main_simplified.py main.py
mv setup_simplified.py setup.py
mv requirements_simplified.txt requirements.txt
mv create_dmg_simplified.sh create_dmg.sh
mv README_simplified.md README.md

# Replace src folder files
echo "Updating source files..."
cd src
mv app_simplified.py app.py
mv utils_simplified.py utils.py
mv settings_simplified.py settings.py
mv account_page_simplified.py account_page.py
mv dialogs_simplified.py dialogs.py

# Clean up
echo "Removing unnecessary files..."
rm -f statistics_view.py
rm -f data_manager.py
cd ..

# Remove unnecessary folders
echo "Removing unnecessary folders..."
rm -rf data
rm -rf logs

# Make scripts executable
echo "Making scripts executable..."
chmod +x build_for_appstore.sh
chmod +x create_dmg.sh

echo "Migration complete! The app is now ready for App Store preparation."
echo "To build the app for App Store, run: ./build_for_appstore.sh"
