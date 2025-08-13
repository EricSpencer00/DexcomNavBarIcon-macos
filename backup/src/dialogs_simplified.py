# dialogs.py
from Cocoa import (
    NSAlert,
    NSTextField,
    NSSecureTextField,
    NSPopUpButton,
    NSView,
    NSMakeRect,
    NSAlertFirstButtonReturn,
    NSApplication,
    NSColor,
    NSFont
)

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
        print(f"Error in get_credentials dialog: {e}")
        return None, None, None

def get_units_preference():
    """
    Display a dialog for selecting glucose units.
    Returns the selected units (mg/dL or mmol/L) if OK is pressed; else returns None.
    """
    try:
        NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Units Settings")
        alert.setInformativeText_("Select your preferred glucose units")
        alert.addButtonWithTitle_("OK")
        alert.addButtonWithTitle_("Cancel")

        width, height = 300, 50
        accessory = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, width, height))

        # Units popup
        units_label = NSTextField.alloc().initWithFrame_(NSMakeRect(0, 15, 80, 22))
        units_label.setStringValue_("Units:")
        units_label.setEditable_(False)
        units_label.setBezeled_(False)
        units_label.setDrawsBackground_(False)

        units_popup = NSPopUpButton.alloc().initWithFrame_(NSMakeRect(90, 15, 200, 22))
        units_popup.addItemsWithTitles_(["mg/dL", "mmol/L"])
        units_popup.selectItemAtIndex_(0)

        accessory.addSubview_(units_label)
        accessory.addSubview_(units_popup)
        alert.setAccessoryView_(accessory)

        response = alert.runModal()
        if response == NSAlertFirstButtonReturn:
            units = str(units_popup.titleOfSelectedItem())
            return units
        else:
            return None
    except Exception as e:
        print(f"Error in get_units_preference dialog: {e}")
        return None
