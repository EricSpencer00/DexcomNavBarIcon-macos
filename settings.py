import os
import json
import logging

def get_settings_dir():
    # User’s Application Support folder
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
        "units": "mg/dL"   # New key for units, defaults to mg/dL
    }
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logging.error("Error loading settings: %s", e)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        logging.error("Error saving settings: %s", e)
