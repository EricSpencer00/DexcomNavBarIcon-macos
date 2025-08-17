import sys
try:
    import keyring
    from keyring.backends import macOS
    keyring.set_keyring(macOS.Keyring())
except Exception as e:
    print(f"Warning: Could not set macOS keyring backend: {e}", file=sys.stderr)
# main.py
from Cocoa import NSApplication, NSApplicationActivationPolicyAccessory
from app import DexcomMenuApp

if __name__ == "__main__":
    # Ensure the application doesn’t show in the Dock.
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    DexcomMenuApp().run()
