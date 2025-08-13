"""
Simple wrapper around macOS Keychain using the `keyring` package.
This stores only the Dexcom password; the username remains in settings.
"""
from typing import Optional

import keyring

SERVICE_NAME = "DexcomNavBarIcon"


def set_password(username: str, password: str) -> None:
    if not username:
        return
    keyring.set_password(SERVICE_NAME, username, password or "")


def get_password(username: str) -> Optional[str]:
    if not username:
        return None
    try:
        return keyring.get_password(SERVICE_NAME, username)
    except Exception:
        return None


def delete_password(username: str) -> None:
    if not username:
        return
    try:
        keyring.delete_password(SERVICE_NAME, username)
    except Exception:
        # Ignore if it doesn't exist
        pass
