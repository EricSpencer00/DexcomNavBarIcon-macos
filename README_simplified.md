# DexcomNavBarIcon for macOS Menu Bar

A lightweight macOS menu bar app that displays your current Dexcom glucose reading.

## Features

- Display Dexcom glucose readings in your macOS menu bar
- Switch between mg/dL and mmol/L units
- Securely store your Dexcom credentials
- Simple, minimal interface with essential functionality

## App Store Version

This version of the app has been streamlined for App Store submission with:

1. Minimal code focused on core functionality
2. Removal of data tracking/storage features
3. Compliance with App Store guidelines
4. Privacy-focused design (no user data is stored remotely)

## Building the App

### Prerequisites

- macOS 10.15 or later
- Python 3.9 or later
- Xcode Command Line Tools

### Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements_simplified.txt
   ```

3. Build the app:
   ```bash
   python setup_simplified.py py2app
   ```

4. The built app will be in the `dist` folder

### App Store Submission

To prepare the app for App Store submission:

1. Run the build script:
   ```bash
   chmod +x build_for_appstore.sh
   ./build_for_appstore.sh
   ```

2. Sign the app with your Apple Developer ID using Xcode
3. Create App Store assets (screenshots, description, etc.)
4. Submit through App Store Connect

## Usage

1. Click the app icon in your menu bar to see your current glucose reading
2. Use the "Update Now" menu item to force a refresh
3. Use the "Units" menu item to switch between mg/dL and mmol/L
4. Use the "Account" menu item to sign out or view account details

## Privacy Policy

This app:
- Does not track or store your data remotely
- Only uses your Dexcom credentials to access your glucose readings
- All data is stored locally and securely on your device
- No data is shared with third parties

## License

See the LICENSE file for details.
