import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
import socket

# Secure storage for credentials
class SecureStorage:
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        key_file = ".secret_key"
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Data caching
class DexcomCache:
    def __init__(self, cache_file="cache.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {"last_update": None, "data": None}
    
    def save(self, data):
        self.cache = {
            "last_update": datetime.now().isoformat(),
            "data": data
        }
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def get(self):
        if not self.cache["last_update"]:
            return None
        last_update = datetime.fromisoformat(self.cache["last_update"])
        if datetime.now() - last_update > datetime.timedelta(minutes=5):
            return None
        return self.cache["data"]

# Network utilities
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Data validation
def validate_reading(reading):
    if not reading:
        return False
    
    try:
        value = float(reading.value)
        if not (40 <= value <= 400):  # Reasonable glucose range
            return False
        return True
    except (ValueError, AttributeError):
        return False
