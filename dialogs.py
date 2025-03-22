# dialogs.py
from Cocoa import (
    NSAlert,          # Dialog boxes with messages, buttons and accessory views
    NSTextField,      # Text fields for labels and input
    NSSecureTextField,# Secure text fields for password input
    NSPopUpButton,    # Pop‐up menus for selecting from a list of items
    NSView,           # Container for other views
    NSMakeRect,       # Create a rectangle with origin and size
    NSAlertFirstButtonReturn, # Return value for the first button in an alert
    NSApplication,    # Access to the shared NSApplication instance
    NSSlider
)
import logging

def get_credentials():
    """
    Display a sign‐in dialog with fields for username, password, and region.
    Returns (username, password, region) if OK is pressed; otherwise, returns (None, None, None).
    """
    try:
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Account Settings")
        alert.setInformativeText_("Please enter your Dexcom username, password, and select your region.")
        alert.addButtonWithTitle_("OK")
        alert.addButtonWithTitle_("Cancel")

        width, height = 300, 120
        accessory = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))

        # Coordinates for layout
        username_y, password_y, region_y = 80, 50, 20

        # Username field
        username_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, username_y, 80, 22))
        username_label.setStringValue_("Username:")
        username_label.setEditable_(False)
        username_label.setBezeled_(False)
        username_label.setDrawsBackground_(False)

        username_field = NSTextField.alloc().initWithFrame_(NSMakeRect(90, username_y, 200, 22))
        username_field.setEditable_(True)
        username_field.setStringValue_("")
        username_field.becomeFirstResponder()

        # Password field
        password_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, password_y, 80, 22))
        password_label.setStringValue_("Password:")
        password_label.setEditable_(False)
        password_label.setBezeled_(False)
        password_label.setDrawsBackground_(False)

        password_field = NSSecureTextField.alloc().initWithFrame_(NSMakeRect(90, password_y, 200, 22))
        password_field.setEditable_(True)
        password_field.setStringValue_("")

        # Region popup
        region_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, region_y, 80, 22))
        region_label.setStringValue_("Region:")
        region_label.setEditable_(False)
        region_label.setBezeled_(False)
        region_label.setDrawsBackground_(False)

        region_popup = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(90, region_y, 200, 22))
        region_popup.addItemsWithTitles_(["us", "ous", "jp"])
        region_popup.selectItemAtIndex_(0)

        # Add all views to accessory view
        accessory.addSubview_(username_label)
        accessory.addSubview_(username_field)
        accessory.addSubview_(password_label)
        accessory.addSubview_(password_field)
        accessory.addSubview_(region_label)
        accessory.addSubview_(region_popup)
        alert.setAccessoryView_(accessory)

        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            username = str(username_field.stringValue())
            password = str(password_field.stringValue())
            region = str(region_popup.titleOfSelectedItem())
            return username, password, region
        else:
            return None, None, None
    except Exception as e:
        logging.error("Error in get_credentials dialog: %s", e)
        return None, None, None

def get_style_settings(current_style):
    """
    Display a dialog for style settings.
    Returns a dictionary of new style settings if OK is pressed; else returns None.
    """
    try:
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Style Settings")
        alert.setInformativeText_("Configure the display style. Use %s as a placeholder for the number.")
        alert.addButtonWithTitle_("OK")
        alert.addButtonWithTitle_("Cancel")

        width, height = 350, 200
        accessory = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))

        labels = ["Low Number Style:", "Normal Number Style:", "High Number Style:",
                  "Steady Arrow:", "Rising Arrow:", "Falling Arrow:", "Show Brackets (true/false):"]
        keys = ["number_low", "number_normal", "number_high",
                "arrow_steady", "arrow_rising", "arrow_falling", "show_brackets"]
        fields = {}

        y_start, delta = 160, 25
        for i, label_text in enumerate(labels):
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, y_start - i * delta, 150, 22))
            label.setStringValue_(label_text)
            label.setEditable_(False)
            label.setBezeled_(False)
            label.setDrawsBackground_(False)
            field = NSTextField.alloc().initWithFrame_(NSMakeRect(160, y_start - i * delta, 180, 22))
            default_value = current_style.get(keys[i], "") if current_style else ""
            field.setStringValue_(default_value)
            accessory.addSubview_(label)
            accessory.addSubview_(field)
            fields[keys[i]] = field

        alert.setAccessoryView_(accessory)
        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            new_style = {}
            for key, field in fields.items():
                val = str(field.stringValue())
                new_style[key] = (val.lower() == "true") if key == "show_brackets" else val
            return new_style
        else:
            return None
    except Exception as e:
        logging.error("Error in get_style_settings dialog: %s", e)
        return None

def get_preferences(current_prefs):
    """
    Display a dialog for user preferences.
    Returns a dictionary of preferences if OK is pressed; else returns None.
    Now includes an extra field for Units (mgdl or mmol).
    """
    try:
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Preferences")
        alert.setInformativeText_("Set acceptable ranges, notifications and units (mgdl or mmol).")
        alert.addButtonWithTitle_("OK")
        alert.addButtonWithTitle_("Cancel")

        width, height = 350, 150
        accessory = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))

        # Define labels and keys (adding a new field for units)
        labels = ["Low Threshold:", "High Threshold:", "Notifications (true/false):", "Units (mgdl/mmol):"]
        keys = ["low_threshold", "high_threshold", "notifications", "units"]
        fields = {}

        y_start, delta = 120, 30
        for i, label_text in enumerate(labels):
            label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, y_start - i * delta, 150, 22))
            label.setStringValue_(label_text)
            label.setEditable_(False)
            label.setBezeled_(False)
            label.setDrawsBackground_(False)
            field = NSTextField.alloc().initWithFrame_(NSMakeRect(160, y_start - i * delta, 180, 22))
            default_value = str(current_prefs.get(keys[i], "")) if current_prefs else ""
            # Provide default for units if not set.
            if keys[i] == "units" and default_value == "":
                default_value = "mgdl"
            field.setStringValue_(default_value)
            accessory.addSubview_(label)
            accessory.addSubview_(field)
            fields[keys[i]] = field

        alert.setAccessoryView_(accessory)
        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            new_prefs = {}
            try:
                new_prefs["low_threshold"] = float(str(fields["low_threshold"].stringValue()))
            except Exception:
                new_prefs["low_threshold"] = 70.0
            try:
                new_prefs["high_threshold"] = float(str(fields["high_threshold"].stringValue()))
            except Exception:
                new_prefs["high_threshold"] = 180.0
            new_prefs["notifications"] = (str(fields["notifications"].stringValue()).lower() == "true")
            new_prefs["units"] = str(fields["units"].stringValue()).lower()  # expects "mgdl" or "mmol"
            return new_prefs
        else:
            return None
    except Exception as e:
        logging.error("Error in get_preferences dialog: %s", e)
        return None
