![Build macOS DMG](https://github.com/EricSpencer00/DexcomNavBarIcon-macos/actions/workflows/main.yml/badge.svg)

<img width="444" height="464" alt="Screenshot 2026-07-15 at 10 58 55 AM" src="https://github.com/user-attachments/assets/4a8a1a06-9d40-4a76-b5ab-7c2cb2f82b49" />

Dexcom Navigation Bar Icon on MacOS

Using the pydexcom python package, view your Dexcom numbers in the top of your navigation bar on Mac.

Installation:
- Download the latest release DMG from GitHub Releases.
- Open the app from the DMG or drag it to Applications.
- There shouldn't be any warnings about untrusted developer since I notarized it.

Notes for Mac App Store:
- This project is being adapted for Mac App Store distribution. Passwords are stored in Keychain, no analytics are used, and the app uses HTTPS to reach Dexcom APIs via pydexcom.
- See the Privacy Policy (PRIVACY.md).

Usage:
- Sign in with your Dexcom username and password and select your region.
- The current glucose and trend appear in the menu bar. Open the menu to update, adjust style, and preferences.

Screenshots

<img width="551" height="38" alt="Screenshot 2026-07-15 at 10 57 23 AM" src="https://github.com/user-attachments/assets/0a5a92e8-5b64-4a8b-b194-c0100470703b" />

![Icon](icon.png)
