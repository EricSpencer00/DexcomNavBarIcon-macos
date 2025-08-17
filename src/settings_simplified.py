import os
import json
from src.utils_simplified import SecureStorage

SETTINGS_FILE = "settings.json"
secure_storage = SecureStorage()

DEFAULT_SETTINGS = {
    "username": "",
    "password": "",
    "region": "us",
    "style_settings": {
        "number_format": "%s",
        "arrow_steady": "→",
        "arrow_rising": "↑",
        "arrow_falling": "↓",
        "show_brackets": True
    },
    "preferences": {
        # Glucose Ranges
        "low_threshold": 70.0,
        "high_threshold": 180.0,
        # Update Settings
        "update_frequency": 5,  # minutes
        # Units
        "units": "mg/dL"  # or "mmol/L"
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
            print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save settings to SETTINGS_FILE."""
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
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
