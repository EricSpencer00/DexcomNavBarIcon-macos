# app.py
import rumps
import threading
import logging
import os
import json
import time
import subprocess

import numpy as np
import matplotlib.pyplot as plt

from Cocoa import (
    NSApplication, NSApplicationActivationPolicyAccessory, NSOperationQueue,
    NSColor, NSAttributedString, NSFont
)
from pydexcom import Dexcom
from pydexcom.errors import AccountError

from dialogs import get_credentials, get_style_settings, get_preferences
from settings import load_settings, save_settings, DEFAULT_SETTINGS, get_settings_dir

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
        self.menu.add("Show Graph")
        self.menu["Show Graph"].set_callback(self.show_history_graph)

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
        self.persist_settings()

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
            # Authentication succeeded; persist settings.
            self.persist_settings()
        except AccountError as e:
            rumps.alert("Authentication Error", str(e))
            self.username = ""
            self.password = ""
            self.dexcom = None
            self.persist_settings()
            self.open_account_settings(None)
        except Exception as e:
            logging.error("Unexpected error during authentication: %s", e)
            self.dexcom = None

    def manual_update(self, _):
        self.update_data()

    def update_data(self, _=None):
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
                # Update persistent history
                self.update_history(reading)
                # Use the full trend arrow provided by pydexcom.
                arrow_override = reading.trend_arrow
                try:
                    value = float(self.current_value)
                except Exception:
                    value = 0
                # Determine display value based on unit preference.
                if self.preferences["units"].lower() == "mgdl":
                    display_value = self.current_value
                else:  # assume "mmol"
                    display_value = self.current_value * 0.0555  # approximate conversion factor

                # Choose number format based on thresholds.
                if value < self.preferences["low_threshold"]:
                    number_format = self.style_settings["number_low"]
                elif value > self.preferences["high_threshold"]:
                    number_format = self.style_settings["number_high"]
                else:
                    number_format = self.style_settings["number_normal"]

                number_text = number_format % display_value
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

    # ----------------- New Methods for History, Prediction and Graphing -----------------

    def update_history(self, reading):
        """Append the current reading to a persistent history file."""
        history_file = os.path.join(get_settings_dir(), "glucose_history.json")
        timestamp = time.time()
        new_entry = {"timestamp": timestamp, "value": reading.value}
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as f:
                    history = json.load(f)
            except Exception:
                history = []
        else:
            history = []
        history.append(new_entry)
        # Optionally keep only the latest 100 entries.
        history = history[-100:]
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)

    def predict_future_readings(self, count=3):
        """Predict the next 'count' glucose readings using a simple linear regression."""
        history_file = os.path.join(get_settings_dir(), "glucose_history.json")
        if not os.path.exists(history_file):
            return []
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception:
            return []
        if len(history) < 2:
            if history:
                return [history[-1]["value"]] * count
            else:
                return []
        history.sort(key=lambda x: x["timestamp"])
        times = np.array([entry["timestamp"] for entry in history])
        values = np.array([entry["value"] for entry in history])
        m, b = np.polyfit(times, values, 1)
        last_time = times[-1]
        avg_delta = np.mean(np.diff(times))
        predictions = []
        for i in range(1, count + 1):
            future_time = last_time + i * avg_delta
            pred_value = m * future_time + b
            predictions.append(round(pred_value, 1))
        return predictions

    def generate_graph(self):
        """Generate and save a graph of past glucose readings and predicted future values."""
        history_file = os.path.join(get_settings_dir(), "glucose_history.json")
        if not os.path.exists(history_file):
            return None
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception:
            return None
        if len(history) == 0:
            return None
        history.sort(key=lambda x: x["timestamp"])
        times = np.array([entry["timestamp"] for entry in history])
        values = np.array([entry["value"] for entry in history])
        predictions = self.predict_future_readings(count=3)
        last_time = times[-1]
        avg_delta = np.mean(np.diff(times)) if len(times) > 1 else 300
        future_times = np.array([last_time + (i + 1) * avg_delta for i in range(3)])
        plt.figure(figsize=(8, 4))
        plt.plot(times, values, marker="o", label="Past Readings")
        if predictions:
            plt.plot(future_times, predictions, marker="x", linestyle="--", label="Predictions")
        plt.xlabel("Timestamp")
        plt.ylabel("Glucose (mg/dL)")
        plt.title("Glucose History and Future Predictions")
        plt.legend()
        plt.tight_layout()
        graph_path = os.path.join(get_settings_dir(), "glucose_graph.png")
        plt.savefig(graph_path)
        plt.close()
        return graph_path

    def show_history_graph(self, _):
        """Open the generated glucose graph in the default image viewer."""
        graph_path = self.generate_graph()
        if graph_path and os.path.exists(graph_path):
            subprocess.Popen(["open", graph_path])
        else:
            rumps.alert("Graph Error", "No graph available.")

if __name__ == "__main__":
    from Cocoa import NSApplication, NSApplicationActivationPolicyAccessory
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    DexcomMenuApp().run()
