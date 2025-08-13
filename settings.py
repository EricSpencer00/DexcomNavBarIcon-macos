import os
import json
import logging

try:
    from Foundation import NSSearchPathForDirectoriesInDomains, NSApplicationSupportDirectory, NSUserDomainMask
except Exception:
    NSSearchPathForDirectoriesInDomains = None
    NSApplicationSupportDirectory = None
    NSUserDomainMask = None


def get_settings_dir():
    # Prefer Cocoa API to ensure sandbox-safe Application Support path
    if NSSearchPathForDirectoriesInDomains is not None:
        try:
            paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, True)
            if paths and len(paths) > 0:
                base = paths[0]
                app_dir = os.path.join(base, "DexcomNavBarIcon")
                os.makedirs(app_dir, exist_ok=True)
                return app_dir
        except Exception:
            pass
    # Fallback (non-sandboxed or during development)
    base = os.path.expanduser("~/Library/Application Support")
    app_dir = os.path.join(base, "DexcomNavBarIcon")
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

SETTINGS_FILE = os.path.join(get_settings_dir(), "settings.json")

DEFAULT_SETTINGS = {
    "username": "",
    # password intentionally excluded from settings.json; use Keychain
    "region": "us",
    "style_settings": {
        "number_low": "Low: %s",
        "number_normal": "Normal: %s",
        "number_high": "High: %s",
        "arrow_steady": "\u2192",
        "arrow_rising": "\u2191",
        "arrow_falling": "\u2193",
        "show_brackets": True
    },
    "preferences": {
        "low_threshold": 70.0,
        "high_threshold": 180.0,
        "notifications": True,
        "units": "mg/dL"
    }
}


def _deepcopy_defaults():
    import copy
    return copy.deepcopy(DEFAULT_SETTINGS)


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # merge with defaults to ensure new keys are present
                base = _deepcopy_defaults()
                base.update({k: v for k, v in data.items() if k in base})
                # merge nested dicts
                if isinstance(data.get("style_settings"), dict):
                    base["style_settings"].update(data["style_settings"])
                if isinstance(data.get("preferences"), dict):
                    base["preferences"].update(data["preferences"])
                return base
        except Exception as e:
            logging.error("Error loading settings: %s", e)
    return _deepcopy_defaults()


def save_settings(settings):
    try:
        # never store password
        to_save = {
            "username": settings.get("username", ""),
            "region": settings.get("region", "us"),
            "style_settings": settings.get("style_settings", DEFAULT_SETTINGS["style_settings"]),
            "preferences": settings.get("preferences", DEFAULT_SETTINGS["preferences"]),
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(to_save, f, indent=4)
    except Exception as e:
        logging.error("Error saving settings: %s", e)
