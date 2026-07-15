![Build macOS DMG](https://github.com/EricSpencer00/DexcomNavBarIcon-macos/actions/workflows/main.yml/badge.svg)

![Icon](icon.png)

Dexcom Navigation Bar Icon on MacOS

Using the pydexcom python package, view your Dexcom numbers in the top of your navigation bar on Mac.

Installation:
- Download the latest release DMG from GitHub Releases.
- Open the app from the DMG or drag it to Applications.
- On first launch, macOS may warn about an unidentified developer. Open System Settings → Privacy & Security and allow the app.

Notes for Mac App Store:
- This project is being adapted for Mac App Store distribution. Passwords are stored in Keychain, no analytics are used, and the app uses HTTPS to reach Dexcom APIs via pydexcom.
- See the Privacy Policy (PRIVACY.md).

Usage:
- Sign in with your Dexcom username and password and select your region.
- The current glucose and trend appear in the menu bar. Open the menu to update, adjust style, and preferences.

Screenshots

<img width="551" height="38" alt="Screenshot 2026-07-15 at 10 57 23 AM" src="https://github.com/user-attachments/assets/0a5a92e8-5b64-4a8b-b194-c0100470703b" />
