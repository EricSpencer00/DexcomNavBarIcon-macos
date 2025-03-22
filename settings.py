import json
import os
import logging

# Determine a persistent settings directory.
def get_settings_dir():
    # Expand to the user's Application Support directory.
    base = os.path.expanduser("~/Library/Application Support")
    app_dir = os.path.join(base, "DexcomNavBarIcon")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

SETTINGS_FILE = os.path.join(get_settings_dir(), "settings.json")

DEFAULT_SETTINGS = {
    "username": "",
    "password": "",
    "region": "us",
    "style_settings": {
        "number_low": "Low: %s",
        "number_normal": "Normal: %s",
        "number_high": "High: %s",
        "arrow_steady": "→",
        "arrow_rising": "↑",
        "arrow_falling": "↓",
        "show_brackets": True
    },
    "preferences": {
        "low_threshold": 70.0,
        "high_threshold": 180.0,
        "notifications": True,
        "units": "mg/dL"
    }
}

def load_settings():
    """Load settings from SETTINGS_FILE, or return defaults if file not found or error occurs."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error("Error loading settings: %s", e)
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to SETTINGS_FILE."""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logging.error("Error saving settings: %s", e)
