# app.py
import rumps
import threading
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

from Cocoa import (
    NSApplication, NSApplicationActivationPolicyAccessory, NSOperationQueue,
    NSColor, NSAttributedString, NSFont
)
from pydexcom import Dexcom
from pydexcom.errors import AccountError

from dialogs import get_credentials, get_style_settings, get_preferences
from settings import load_settings, save_settings, DEFAULT_SETTINGS
from utils import setup_logging, DexcomCache, check_internet, validate_reading
from account_page import AccountPage
from data_manager import GlucoseDataManager
from statistics_view import StatisticsView

class DexcomMenuApp(rumps.App):
    def __init__(self):
        # Setup logging
        setup_logging()
        logging.info("Initializing DexcomMenuApp")
        
        # Hide Dock icon
        NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        super(DexcomMenuApp, self).__init__("Dexcom")

        # Initialize cache and data manager
        self.cache = DexcomCache()
        self.data_manager = GlucoseDataManager()
        logging.info("Cache and data manager initialized")

        # Load settings
        self.settings = load_settings()
        self.username = self.settings.get("username", "")
        self.password = self.settings.get("password", "")
        self.region = self.settings.get("region", "us")
        self.style_settings = self.settings.get("style_settings", DEFAULT_SETTINGS["style_settings"])
        self.preferences = self.settings.get("preferences", DEFAULT_SETTINGS["preferences"])
        self.dexcom = None
        logging.info("Settings loaded")

        # Data display
        self.current_value = None
        self.current_trend_arrow = None

        # Build menu items
        self.menu.clear()
        self.menu.add("Update Now")
        self.menu["Update Now"].set_callback(self.manual_update)
        self.menu.add("Account")
        self.menu["Account"].set_callback(self.open_account_page)
        self.menu.add("Statistics")
        self.menu["Statistics"].set_callback(self.open_statistics)
        self.menu.add("Style")
        self.menu["Style"].set_callback(self.open_style_settings)
        self.menu.add("Preferences")
        self.menu["Preferences"].set_callback(self.open_preferences)
        logging.info("Menu items created")

        # If no account info, prompt for it
        if not self.username or not self.password:
            logging.info("No credentials found, prompting user")
            self.open_account_settings(None)
        else:
            logging.info("Found existing credentials, attempting authentication")
            self.authenticate()

        # Fetch data immediately and set up a timer to update every 5 minutes
        logging.info("Starting initial data fetch")
        self.update_data()
        timer = rumps.Timer(self.update_data, self.preferences.get("update_frequency", 5) * 60)
        timer.start()
        logging.info("Update timer started")

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
        logging.info("Signing out user")
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

    def open_statistics(self, _):
        """Open the statistics view."""
        stats_view = StatisticsView(self.data_manager)
        stats_view.show()

    def authenticate(self):
        try:
            # Attempt Dexcom authentication
            if self.region == "us":
                self.dexcom = Dexcom(username=self.username, password=self.password)
            else:
                self.dexcom = Dexcom(username=self.username, password=self.password, ous=True)
            # If we get here, authentication succeeded. Persist the (good) credentials now.
            self.persist_settings()
            logging.info("Successfully authenticated with Dexcom")
        except AccountError as e:
            # If credentials are invalid, alert the user
            logging.error("Authentication failed: %s", str(e))
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
            logging.error("Unexpected error during authentication: %s", e)
            self.dexcom = None

    def manual_update(self, _):
        logging.info("Manual update triggered")
        self.update_data()

    def update_data(self, _=None):
        logging.info("update_data called")
        if not check_internet():
            logging.warning("No internet connection available")
            self.refresh_display_with_text("[Offline]")
            return
        
        # Start a new daemon thread to fetch data
        logging.info("Starting fetch_data thread")
        thread = threading.Thread(target=self.fetch_data)
        thread.daemon = True
        thread.start()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def fetch_data(self):
        logging.info("fetch_data started")
        if not self.dexcom:
            logging.info("No Dexcom instance, attempting authentication")
            self.authenticate()
            if not self.dexcom:
                logging.error("Authentication failed")
                raise Exception("Authentication failed")
        
        try:
            logging.info("Attempting to get current glucose reading")
            reading = self.dexcom.get_current_glucose_reading()
            logging.info(f"Received reading: {reading}")
            
            if not validate_reading(reading):
                logging.error("Invalid reading received")
                raise Exception("Invalid reading received")
            
            self.current_value = reading.value
            self.current_trend_arrow = reading.trend_arrow
            logging.info(f"Current value: {self.current_value}, Trend: {self.current_trend_arrow}")
            
            # Save reading to data manager
            self.data_manager.save_reading(float(self.current_value), self.current_trend_arrow)
            
            # Cache the successful reading
            self.cache.save({
                "value": reading.value,
                "trend_arrow": reading.trend_arrow
            })
            logging.info("Reading cached and saved")
            
            try:
                value = float(self.current_value)
            except Exception as e:
                logging.error(f"Error converting value to float: {e}")
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
            
            logging.info(f"Prepared display text: {display_text}")
            NSOperationQueue.mainQueue().addOperationWithBlock_(
                lambda: self.refresh_display_with_text(display_text)
            )
            
            # Check if we need to send notifications
            if self.preferences.get("notifications", False):
                self._check_notifications(value)
            
        except Exception as e:
            logging.error(f"Error in fetch_data: {str(e)}")
            # Try to use cached data if available
            cached_data = self.cache.get()
            if cached_data:
                logging.info("Using cached data due to fetch error")
                self.current_value = cached_data["value"]
                self.current_trend_arrow = cached_data["trend_arrow"]
                display_text = f"[{self.current_value}][{self.current_trend_arrow}]"
                NSOperationQueue.mainQueue().addOperationWithBlock_(
                    lambda: self.refresh_display_with_text(display_text)
                )
            else:
                logging.error("No cached data available")
                NSOperationQueue.mainQueue().addOperationWithBlock_(
                    lambda: self.refresh_display_with_text("[Err][?]")
                )

    def _check_notifications(self, value):
        """Check if notifications should be sent based on glucose value."""
        if value < self.preferences.get("low_threshold", 70) and self.preferences.get("alert_on_low", True):
            self._send_notification("Low Glucose Alert", f"Your glucose is low: {value}")
        elif value > self.preferences.get("high_threshold", 180) and self.preferences.get("alert_on_high", True):
            self._send_notification("High Glucose Alert", f"Your glucose is high: {value}")

    def _send_notification(self, title, message):
        """Send a notification with the specified title and message."""
        try:
            notification = rumps.Notification(
                title=title,
                message=message,
                sound=self.preferences.get("sound_enabled", True)
            )
            notification.send()
        except Exception as e:
            logging.error(f"Error sending notification: {e}")

    def refresh_display_with_text(self, text):
        logging.info(f"Refreshing display with text: {text}")
        try:
            value = float(self.current_value) if self.current_value else 0
        except Exception as e:
            logging.error(f"Error converting value in refresh_display: {e}")
            value = 0
            
        # Add status indicator
        status_indicators = {
            "normal": "●",
            "high": "▲",
            "low": "▼"
        }
        
        if value > self.preferences["high_threshold"]:
            status = "high"
            color = NSColor.redColor()
        elif value < self.preferences["low_threshold"]:
            status = "low"
            color = NSColor.redColor()
        else:
            status = "normal"
            color = NSColor.blackColor()
            
        text = f"{status_indicators[status]} {text}"
        logging.info(f"Final display text: {text}")
        
        attributes = {
            "NSForegroundColorAttributeName": color,
            "NSFont": NSFont.systemFontOfSize_(12)
        }
        attributed_title = NSAttributedString.alloc().initWithString_attributes_(text, attributes)
        
        if hasattr(self, '_status_item') and self._status_item.button:
            self._status_item.button.setAttributedTitle_(attributed_title)
            logging.info("Display updated via status item")
        else:
            self.title = text
            logging.info("Display updated via title")

    def persist_settings(self):
        settings = {
            "username": self.username,
            "password": self.password,
            "region": self.region,
            "style_settings": self.style_settings,
            "preferences": self.preferences
        }
        if save_settings(settings):
            logging.info("Settings saved successfully")
        else:
            logging.error("Failed to save settings")

    def cleanup(self):
        """Clean up old data based on retention settings."""
        try:
            retention_days = self.preferences.get("data_retention_days", 30)
            self.data_manager.cleanup_old_data(retention_days)
            logging.info(f"Cleaned up data older than {retention_days} days")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
