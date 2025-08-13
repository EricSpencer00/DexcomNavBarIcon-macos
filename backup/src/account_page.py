import rumps
from Cocoa import (
    NSAlert, NSInformationalAlertStyle, NSApp, NSButton,
    NSView, NSTextField, NSFont, NSColor, NSMakeRect
)

class AccountPage:
    def __init__(self, username, region, on_sign_out):
        self.username = username
        self.region = region
        self.on_sign_out = on_sign_out
        
    def show(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_("Account Information")
        alert.setInformativeText_("Your Dexcom account details")
        alert.setAlertStyle_(NSInformationalAlertStyle)
        
        # Create custom view for account info
        view = NSView.alloc().initWithFrame_(NSMakeRect(0, 0, 300, 100))
        
        # Username field
        username_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 70, 260, 20))
        username_label.setStringValue_(f"Username: {self.username}")
        username_label.setEditable_(False)
        username_label.setBordered_(False)
        username_label.setBackgroundColor_(NSColor.clearColor())
        view.addSubview_(username_label)
        
        # Region field
        region_label = NSTextField.alloc().initWithFrame_(NSMakeRect(20, 40, 260, 20))
        region_label.setStringValue_(f"Region: {self.region.upper()}")
        region_label.setEditable_(False)
        region_label.setBordered_(False)
        region_label.setBackgroundColor_(NSColor.clearColor())
        view.addSubview_(region_label)
        
        alert.setAccessoryView_(view)
        
        # Add buttons
        alert.addButtonWithTitle_("Sign Out")
        alert.addButtonWithTitle_("Close")
        
        response = alert.runModal()
        
        if response == 1000:  # Sign Out button
            self.on_sign_out() 