# Migration Guide: DexcomNavBarIcon for App Store

This document outlines the changes made to prepare the DexcomNavBarIcon app for App Store submission, and provides steps to migrate from the original version to the App Store compliant version.

## Changes Made

1. **Removed Data Collection & Storage Features**
   - Removed glucose data storage functionality
   - Removed statistics view and data analysis features
   - Removed data export functionality

2. **Simplified User Interface**
   - Removed advanced style settings
   - Removed complex preferences
   - Kept only essential menu items (Update Now, Account, Units)

3. **Privacy Enhancements**
   - Removed all analytics and tracking code
   - Credentials are only stored locally in secure storage

4. **Optimized Code Base**
   - Reduced dependencies (removed pandas, matplotlib, numpy)
   - Simplified logging to basic console output
   - Removed unused features

5. **App Store Compliance**
   - Updated Info.plist with required App Store properties
   - Added proper usage descriptions for system permissions
   - Added App Store packaging script

## Migration Steps

To migrate from the original version to the App Store version:

1. **Rename the simplified files:**
   ```bash
   mv main_simplified.py main.py
   mv setup_simplified.py setup.py
   mv requirements_simplified.txt requirements.txt
   mv create_dmg_simplified.sh create_dmg.sh
   mv README_simplified.md README.md
   ```

2. **Replace the src folder files:**
   ```bash
   cd src
   mv app_simplified.py app.py
   mv utils_simplified.py utils.py
   mv settings_simplified.py settings.py
   mv account_page_simplified.py account_page.py
   mv dialogs_simplified.py dialogs.py
   rm statistics_view.py
   rm data_manager.py
   ```

3. **Remove unnecessary files and folders:**
   ```bash
   rm -rf data
   rm -rf logs
   ```

4. **Build the App Store version:**
   ```bash
   chmod +x build_for_appstore.sh
   ./build_for_appstore.sh
   ```

## App Store Submission Checklist

Before submitting to the App Store:

1. **App Metadata**
   - Prepare app description (1-2 paragraphs)
   - Create keywords list
   - Create support URL and privacy policy URL

2. **App Assets**
   - Create App Icon in all required sizes
   - Take screenshots in required dimensions
   - Create promotional text

3. **Developer Account**
   - Ensure your Apple Developer account is active
   - Set up your App ID in App Store Connect
   - Configure app capabilities

4. **Testing**
   - Test on multiple macOS versions
   - Verify sandboxing is working correctly
   - Ensure the app works without admin privileges

5. **Code Signing**
   - Sign the app with your Developer ID
   - Use the App Store provisioning profile

## Important Notes

- The simplified app maintains the core functionality of displaying Dexcom readings in the menu bar
- Users can still switch between mg/dL and mmol/L units
- Dexcom login functionality remains the same
- The menu bar display format is simplified
