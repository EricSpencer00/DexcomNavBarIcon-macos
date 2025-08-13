# main.py
from Cocoa import NSApplication, NSApplicationActivationPolicyAccessory
from src.app_simplified import DexcomMenuApp

if __name__ == "__main__":
    # Ensure the application doesn't show in the Dock.
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    DexcomMenuApp().run()
