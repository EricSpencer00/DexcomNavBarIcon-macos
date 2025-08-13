"""
setup.py
Usage: python setup.py py2app
"""
from setuptools import setup

APP = ['main.py']
DATA_FILES = ['icon.icns']
OPTIONS = {
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleIdentifier': 'com.ericspencer.dexcomnavbaricon',
        'CFBundleName': 'DexcomNavBarIcon',
        'LSUIElement': True,  # Agent app, hides from Dock
        'NSHumanReadableCopyright': '© 2025 Eric Spencer',
        'LSApplicationCategoryType': 'public.app-category.healthcare-fitness',
    },
    'excludes': ['tkinter', 'pytest', 'tests'],
    'includes': [
        'keyring',
        'keyring.backends',
        'keyring.backends.OS_X',
        'keyring.backends.macOS',  # Ensure macOS Keychain backend is bundled
        'charset_normalizer'
    ],
    'packages': ['requests', 'pydexcom', 'matplotlib', 'numpy'],
}

setup(
    name='DexcomNavBarIcon',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
