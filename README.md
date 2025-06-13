# DexcomNavBarIcon

A macOS menu bar application that displays your current Dexcom glucose reading and trend in the menu bar.

## Features

- Real-time glucose readings in the menu bar
- Trend indicators
- Account management
- Statistics and data analysis
- Customizable alerts
- Data export capabilities

## Installation

1. Download the latest release from the [Releases](https://github.com/ericspencer/DexcomNavBarIcon/releases) page
2. Open the DMG file
3. Drag the app to your Applications folder
4. Launch the app from your Applications folder

## Development

### Prerequisites

- Python 3.11 or later
- macOS 10.15 or later

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ericspencer/DexcomNavBarIcon.git
   cd DexcomNavBarIcon
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Project Structure

```
DexcomNavBarIcon/
├── src/                    # Source code
│   ├── app.py             # Main application
│   ├── account_page.py    # Account management
│   ├── data_manager.py    # Data handling
│   ├── dialogs.py         # UI dialogs
│   ├── settings.py        # Settings management
│   ├── statistics_view.py # Statistics display
│   └── utils.py           # Utility functions
├── resources/             # Application resources
│   ├── icon.png          # Application icon (PNG)
│   └── icon.icns         # Application icon (ICNS)
├── scripts/              # Build and utility scripts
│   ├── build.sh         # Build script
│   └── create_dmg.sh    # DMG creation script
├── main.py              # Application entry point
├── setup.py             # Py2App configuration
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Building

The application is automatically built and packaged when changes are pushed to the main branch. The DMG file is available as an artifact in the GitHub Actions workflow.

To build locally:
```bash
python setup.py py2app
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [pydexcom](https://github.com/gagebenne/pydexcom) for the Dexcom API wrapper
- [rumps](https://github.com/jaredks/rumps) for the macOS menu bar integration

![Build macOS DMG](https://github.com/EricSpencer00/DexcomNavBarIcon-macos/actions/workflows/main.yml/badge.svg)

![Icon](icon.png)

Dexcom Navigation Bar Icon on MacOS

Using the pydexcom python package, view your Dexcom numbers in the top of your navigation bar on Mac.

Installation: 
- Download the [.dmg file](https://github.com/EricSpencer00/DexcomNavBarIcon-macos/actions/runs/15541999840)
- Click on app via the window that pops up
- Open System Preferences
- Navigate to Security & Privacy
- Allow the App to Run

For more information on how to allow apps from unidentified developers, visit [this link](https://easymacos.com/cannot-be-opened-because-it-is-from-an-unidentified-developer.html).

- Then, sign in with your Dexcom username and password along with your region

![Screenshot 2025-03-05 at 12 59 37 PM](https://github.com/user-attachments/assets/f547bb49-6a3d-4d2d-a4f2-07099d0cc680) 
