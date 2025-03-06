# app.py
import rumps
import threading
import logging

from Cocoa import (
    NSApplication, NSApplicationActivationPolicyAccessory, NSOperationQueue,
    NSColor, NSAttributedString, NSFont
)
from pydexcom import Dexcom
from pydexcom.errors import AccountError

from dialogs import get_credentials, get_style_settings, get_preferences
from settings import load_settings, save_settings, DEFAULT_SETTINGS

class DexcomMenuApp(rumps.App):
    def __init__(self):
        # Hide Dock icon.
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        super(DexcomMenuApp, self).__init__("Dexcom")

        # Load settings.
        self.settings = load_settings()
        self.username = self.settings.get("username", "")
        self.password = self.settings.get("password", "")
        self.region = self.settings.get("region", "us")
        self.style_settings = self.settings.get("style_settings", DEFAULT_SETTINGS["style_settings"])
        self.preferences = self.settings.get("preferences", DEFAULT_SETTINGS["preferences"])
        self.dexcom = None

        # Data display
        self.current_value = None
        self.current_trend_arrow = None

        # Build menu items.
        self.menu.clear()
        self.menu.add("Update Now")
        self.menu["Update Now"].set_callback(self.manual_update)
        self.menu.add("Account")
        self.menu["Account"].set_callback(self.open_account_settings)
        self.menu.add("Style")
        self.menu["Style"].set_callback(self.open_style_settings)
        self.menu.add("Preferences")
        self.menu["Preferences"].set_callback(self.open_preferences)

        # If no account info, prompt for it.
        if not self.username or not self.password:
            self.open_account_settings(None)
        else:
            self.authenticate()

        # Fetch data immediately and set up a timer to update every 5 minutes.
        self.update_data()
        timer = rumps.Timer(self.update_data, 300)
        timer.start()

    def open_account_settings(self, _):
        creds = get_credentials()
        if not creds[0] or creds[1] == "":
            rumps.alert("Setup Cancelled", "Credentials are required.")
            return
        self.username, self.password, self.region = creds
        self.authenticate()
        # self.persist_settings()

    def open_style_settings(self, _):
        new_style = get_style_settings(self.style_settings)
        if new_style:
            self.style_settings = new_style
            rumps.alert("Style Updated", "New style settings have been applied.")
            self.refresh_display()
            self.persist_settings()

    def open_preferences(self, _):
        new_prefs = get_preferences(self.preferences)
        if new_prefs:
            self.preferences = new_prefs
            rumps.alert("Preferences Updated", "New preferences have been applied.")
            self.refresh_display()
            self.persist_settings()

    def authenticate(self):
        try:
            # Attempt Dexcom authentication
            self.dexcom = Dexcom(username=self.username, password=self.password, region=self.region)
            # If we get here, authentication succeeded. Persist the (good) credentials now.
            self.persist_settings()
        except AccountError as e:
            # If credentials are invalid, alert the user
            rumps.alert("Authentication Error", str(e))
            
            # Clear out the stored credentials so we don't keep reloading them
            self.username = ""
            self.password = ""
            self.dexcom = None
            
            # Persist the empty credentials so settings.json is no longer storing them
            self.persist_settings()
            
            # Prompt user to re-enter credentials
            self.open_account_settings(None)
        except Exception as e:
            # Log any other unexpected error
            logging.error("Unexpected error during authentication: %s", e)
            self.dexcom = None


    def manual_update(self, _):
        self.update_data()

    def update_data(self, _=None):
        # Start a new daemon thread to fetch data.
        thread = threading.Thread(target=self.fetch_data)
        thread.daemon = True
        thread.start()

    def fetch_data(self):
        if not self.dexcom:
            self.authenticate()
            if not self.dexcom:
                return
        try:
            reading = self.dexcom.get_current_glucose_reading()
            if reading is not None:
                self.current_value = reading.value
                self.current_trend_arrow = reading.trend_arrow
                try:
                    value = float(self.current_value)
                except Exception:
                    value = 0
                if value < self.preferences["low_threshold"]:
                    number_format = self.style_settings["number_low"]
                    arrow_override = self.style_settings["arrow_falling"]
                elif value > self.preferences["high_threshold"]:
                    number_format = self.style_settings["number_high"]
                    arrow_override = self.style_settings["arrow_rising"]
                else:
                    number_format = self.style_settings["number_normal"]
                    arrow_override = self.style_settings["arrow_steady"]
                number_text = number_format % self.current_value
                if self.style_settings.get("show_brackets", True):
                    display_text = f"[{number_text}][{arrow_override}]"
                else:
                    display_text = f"{number_text} {arrow_override}"
            else:
                display_text = "[N/A][?]"
        except Exception as e:
            logging.error("Error fetching Dexcom data: %s", e)
            display_text = "[Err][?]"

        NSOperationQueue.mainQueue().addOperationWithBlock_(lambda: self.refresh_display_with_text(display_text))

    def refresh_display_with_text(self, text):
        try:
            value = float(self.current_value)
        except Exception:
            value = 0
        color = NSColor.redColor() if (value > self.preferences["high_threshold"] or value < self.preferences["low_threshold"]) else NSColor.blackColor()
        attributes = {"NSForegroundColorAttributeName": color, "NSFont": NSFont.systemFontOfSize_(12)}
        attributed_title = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
        if hasattr(self, '_status_item') and self._status_item.button:
            self._status_item.button.setAttributedTitle_(attributed_title)
        else:
            self.title = text

    def persist_settings(self):
        settings = {
            "username": self.username,
            "password": self.password,
            "region": self.region,
            "style_settings": self.style_settings,
            "preferences": self.preferences
        }
        save_settings(settings)
