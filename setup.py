"""
This is a setup.py script for the App Store-compliant Dexcom NavBar Icon app

Usage:
    python setup.py py2app
"""
from setuptools import setup, find_packages

APP = ['main.py']
DATA_FILES = [
    ('resources', ['resources/icon.icns']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': find_packages() + ['cffi'],
    'includes': ['cmath', 'chardet', 'cffi'],
    'iconfile': 'resources/icon.icns',
    'plist': {
        'CFBundleName': 'DexcomNavBarIcon',
        'CFBundleDisplayName': 'DexcomNavBarIcon',
        'CFBundleGetInfoString': "DexcomNavBarIcon for Mac Menu Bar",
        'CFBundleIdentifier': "com.ericspencer.dexcomnavbaricon",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': u"Copyright © 2025, Eric Spencer, All Rights Reserved",
        'NSHighResolutionCapable': True,
        'LSApplicationCategoryType': 'public.app-category.healthcare-fitness',
        'LSUIElement': True,  # Makes app run as a background app without a dock icon
        'NSAppTransportSecurity': {
            'NSAllowsArbitraryLoads': True
        },
        'NSAppleEventsUsageDescription': 'This app needs to control other applications to function properly.',
        'NSCalendarsUsageDescription': 'This app needs access to your calendar to function properly.',
        'NSCameraUsageDescription': 'This app needs access to your camera to function properly.',
        'NSContactsUsageDescription': 'This app needs access to your contacts to function properly.',
        'NSLocationAlwaysUsageDescription': 'This app needs access to your location to function properly.',
        'NSLocationWhenInUseUsageDescription': 'This app needs access to your location to function properly.',
        'NSMicrophoneUsageDescription': 'This app needs access to your microphone to function properly.',
        'NSPhotoLibraryUsageDescription': 'This app needs access to your photo library to function properly.',
    }
}

setup(
    name='DexcomNavBarIcon',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'pydexcom>=0.4.0',
        'pyobjc_framework_Cocoa>=11.0',
        'rumps>=0.4.0',
        'setuptools>=58.0.4',
        'cryptography',
        'tenacity',
        'cffi',
    ],
    package_dir={'': '.'},
)
