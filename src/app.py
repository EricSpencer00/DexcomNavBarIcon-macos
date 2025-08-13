# app.py
import rumps
import threading
from tenacity import retry, stop_after_attempt, wait_exponential

from Cocoa import (
    NSApplication, NSApplicationActivationPolicyAccessory, NSOperationQueue,
    NSColor, NSAttributedString, NSFont
)
from pydexcom import Dexcom
from pydexcom.errors import AccountError

from src.dialogs import get_credentials, get_units_preference
from src.settings import load_settings, save_settings, DEFAULT_SETTINGS
from src.utils import DexcomCache, check_internet, validate_reading
from src.account_page import AccountPage

class DexcomMenuApp(rumps.App):
    def __init__(self):
        print("Initializing DexcomMenuApp")
        
        # Hide Dock icon
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        super(DexcomMenuApp, self).__init__("Dexcom")

        # Initialize cache
        self.cache = DexcomCache()
        print("Cache initialized")

        # Load settings
        self.settings = load_settings()
        self.username = self.settings.get("username", "")
        self.password = self.settings.get("password", "")
        self.region = self.settings.get("region", "us")
        self.style_settings = self.settings.get("style_settings", DEFAULT_SETTINGS["style_settings"])
        self.preferences = self.settings.get("preferences", DEFAULT_SETTINGS["preferences"])
        self.dexcom = None
        print("Settings loaded")

        # Data display
        self.current_value = None
        self.current_trend_arrow = None

        # Build menu items
        self.menu.clear()
        self.menu.add("Update Now")
        self.menu["Update Now"].set_callback(self.manual_update)
        self.menu.add("Account")
        self.menu["Account"].set_callback(self.open_account_page)
        self.menu.add("Units")
        self.menu["Units"].set_callback(self.open_units_settings)
        print("Menu items created")

        # If no account info, prompt for it
        if not self.username or not self.password:
            print("No credentials found, prompting user")
            self.open_account_settings(None)
        else:
            print("Found existing credentials, attempting authentication")
            self.authenticate()

        # Fetch data immediately and set up a timer to update every 5 minutes
        print("Starting initial data fetch")
        self.update_data()
        timer = rumps.Timer(self.update_data, self.preferences.get("update_frequency", 5) * 60)
        timer.start()
        print("Update timer started")

    def open_account_page(self, _):
        if not self.username:
            self.open_account_settings(None)
            return
            
        account_page = AccountPage(
            username=self.username,
            region=self.region,
            on_sign_out=self.sign_out
        )
        account_page.show()

    def sign_out(self):
        print("Signing out user")
        self.username = ""
        self.password = ""
        self.dexcom = None
        self.persist_settings()
        self.open_account_settings(None)

    def open_account_settings(self, _):
        creds = get_credentials()
        if not creds[0] or creds[1] == "":
            rumps.alert("Setup Cancelled", "Credentials are required.")
            return
        self.username, self.password, self.region = creds
        self.authenticate()

    def open_units_settings(self, _):
        units = get_units_preference()
        if units:
            self.preferences["units"] = units
            rumps.alert("Units Updated", f"Units set to {units}")
            self.refresh_display()
            self.persist_settings()

    def authenticate(self):
        try:
            # Attempt Dexcom authentication
            if self.region == "us":
                self.dexcom = Dexcom(username=self.username, password=self.password)
            else:
                self.dexcom = Dexcom(username=self.username, password=self.password, ous=True)
            # If we get here, authentication succeeded. Persist the (good) credentials now.
            self.persist_settings()
            print("Successfully authenticated with Dexcom")
        except AccountError as e:
            # If credentials are invalid, alert the user
            print(f"Authentication failed: {str(e)}")
            rumps.alert("Authentication Error", str(e))
            
            # Clear out the stored credentials
            self.username = ""
            self.password = ""
            self.dexcom = None
            
            # Persist the empty credentials
            self.persist_settings()
            
            # Prompt user to re-enter credentials
            self.open_account_settings(None)
        except Exception as e:
            # Log any other unexpected error
            print(f"Unexpected error during authentication: {e}")
            self.dexcom = None

    def manual_update(self, _):
        print("Manual update triggered")
        self.update_data()

    def update_data(self, _=None):
        print("update_data called")
        if not check_internet():
            print("No internet connection available")
            self.refresh_display_with_text("[Offline]")
            return
        
        # Start a new daemon thread to fetch data
        print("Starting fetch_data thread")
        thread = threading.Thread(target=self.fetch_data)
        thread.daemon = True
        thread.start()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_data(self):
        print("fetch_data started")
        if not self.dexcom:
            print("No Dexcom instance, attempting authentication")
            self.authenticate()
            if not self.dexcom:
                print("Authentication failed")
                raise Exception("Authentication failed")
        
        try:
            print("Attempting to get current glucose reading")
            reading = self.dexcom.get_current_glucose_reading()
            print(f"Received reading: {reading}")
            
            if not validate_reading(reading):
                print("Invalid reading received")
                raise Exception("Invalid reading received")
            
            self.current_value = reading.value
            self.current_trend_arrow = reading.trend_arrow
            print(f"Current value: {self.current_value}, Trend: {self.current_trend_arrow}")
            
            # Cache the successful reading
            self.cache.save({
                "value": reading.value,
                "trend_arrow": reading.trend_arrow
            })
            print("Reading cached")
            
            # Convert to mmol/L if needed
            display_value = self.current_value
            if self.preferences["units"] == "mmol/L":
                try:
                    display_value = round(float(self.current_value) / 18.0, 1)
                except:
                    pass
                
            number_format = self.style_settings["number_format"]
            arrow_symbol = self.get_arrow_symbol(self.current_trend_arrow)
                
            number_text = number_format % display_value
            if self.style_settings.get("show_brackets", True):
                display_text = f"[{number_text}][{arrow_symbol}]"
            else:
                display_text = f"{number_text} {arrow_symbol}"
            
            print(f"Prepared display text: {display_text}")
            NSOperationQueue.mainQueue().addOperationWithBlock_(
                lambda: self.refresh_display_with_text(display_text)
            )
            
        except Exception as e:
            print(f"Error in fetch_data: {str(e)}")
            # Try to use cached data if available
            cached_data = self.cache.get()
            if cached_data:
                print("Using cached data due to fetch error")
                self.current_value = cached_data["value"]
                self.current_trend_arrow = cached_data["trend_arrow"]
                
                # Convert to mmol/L if needed
                display_value = self.current_value
                if self.preferences["units"] == "mmol/L":
                    try:
                        display_value = round(float(self.current_value) / 18.0, 1)
                    except:
                        pass
                
                arrow_symbol = self.get_arrow_symbol(self.current_trend_arrow)
                display_text = f"[{display_value}][{arrow_symbol}]"
                
                NSOperationQueue.mainQueue().addOperationWithBlock_(
                    lambda: self.refresh_display_with_text(display_text)
                )
            else:
                print("No cached data available")
                NSOperationQueue.mainQueue().addOperationWithBlock_(
                    lambda: self.refresh_display_with_text("[Err][?]")
                )

    def get_arrow_symbol(self, trend_arrow):
        arrow_map = {
            "FLAT": self.style_settings["arrow_steady"],
            "DOUBLE_UP": self.style_settings["arrow_rising"],
            "SINGLE_UP": self.style_settings["arrow_rising"],
            "FORTY_FIVE_UP": self.style_settings["arrow_rising"],
            "DOUBLE_DOWN": self.style_settings["arrow_falling"],
            "SINGLE_DOWN": self.style_settings["arrow_falling"],
            "FORTY_FIVE_DOWN": self.style_settings["arrow_falling"],
        }
        return arrow_map.get(trend_arrow, "?")

    def refresh_display_with_text(self, text):
        print(f"Refreshing display with text: {text}")
        self.title = text

    def persist_settings(self):
        settings = {
            "username": self.username,
            "password": self.password,
            "region": self.region,
            "style_settings": self.style_settings,
            "preferences": self.preferences
        }
        if save_settings(settings):
            print("Settings saved successfully")
        else:
            print("Failed to save settings")
