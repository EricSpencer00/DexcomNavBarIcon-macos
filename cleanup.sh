#!/bin/bash

# Create necessary directories
mkdir -p scripts
mkdir -p resources
mkdir -p src

# Move scripts to scripts directory
mv build.sh scripts/
mv create_dmg.sh scripts/

# Move resources to resources directory
mv icon.png resources/
mv icon.icns resources/

# Move source files to src directory
mv app.py src/
mv account_page.py src/
mv data_manager.py src/
mv dialogs.py src/
mv settings.py src/
mv statistics_view.py src/
mv utils.py src/

# Clean up build artifacts
rm -rf build/
rm -rf dist/
rm -rf dmg_temp/
rm -f DexcomNavBarIcon.dmg
rm -rf .eggs/
rm -rf __pycache__/
rm -f .DS_Store

# Move main.py to root (it's the entry point)
# Keep requirements.txt, setup.py, and README.md in root

echo "Cleanup complete! Files have been organized into appropriate directories." 