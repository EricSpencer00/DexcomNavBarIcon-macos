import os
import json
import logging
from utils import SecureStorage

<<<<<<< HEAD
def get_settings_dir():
    # User’s Application Support folder
    base = os.path.expanduser("~/Library/Application Support")
    app_dir = os.path.join(base, "DexcomNavBarIcon")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

SETTINGS_FILE = os.path.join(get_settings_dir(), "settings.json")
=======
SETTINGS_FILE = "settings.json"
secure_storage = SecureStorage()
>>>>>>> 7dbff11 (better storage)

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
                settings = json.load(f)
                # Decrypt credentials if they exist
                if settings.get("username"):
                    settings["username"] = secure_storage.decrypt(settings["username"])
                if settings.get("password"):
                    settings["password"] = secure_storage.decrypt(settings["password"])
                return settings
        except Exception as e:
            logging.error("Error loading settings: %s", e)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        # Create a copy of settings to encrypt
        settings_to_save = settings.copy()
        
        # Encrypt credentials
        if settings_to_save.get("username"):
            settings_to_save["username"] = secure_storage.encrypt(settings_to_save["username"])
        if settings_to_save.get("password"):
            settings_to_save["password"] = secure_storage.encrypt(settings_to_save["password"])
        
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings_to_save, f, indent=4)
    except Exception as e:
        logging.error("Error saving settings: %s", e)
