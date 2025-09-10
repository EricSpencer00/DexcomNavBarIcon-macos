#!/usr/bin/env bash
set -euo pipefail

APP_PATH="${1:-dist/DexcomNavBarIcon.app}"
if [[ ! -d "$APP_PATH" ]]; then
  echo "App not found at $APP_PATH" >&2
  exit 1
fi

echo "Verifying universal2 architectures in: $APP_PATH"

BIN="$APP_PATH/Contents/MacOS/DexcomNavBarIcon"
if [[ -f "$BIN" ]]; then
  echo "Main binary architectures:"
  lipo -info "$BIN" || true
  file "$BIN" || true
else
  echo "Warning: Main binary not found at $BIN"
fi

PYFRAME="$APP_PATH/Contents/Frameworks/Python.framework/Versions/3.9/Python"
if [[ -f "$PYFRAME" ]]; then
  echo "Embedded Python architectures:"
  lipo -info "$PYFRAME" || true
  file "$PYFRAME" || true
else
  echo "Note: Embedded Python not found (py2app may use site Python)."
fi

echo "Inspecting .so/.dylib files for arch coverage (first 10):"
find "$APP_PATH" -type f \( -name "*.so" -o -name "*.dylib" -o -name "*.framework" \) | head -n 10 | while read -r f; do
  echo "-- $f"
  file "$f" || true
done

if command -v /usr/libexec/PlistBuddy >/dev/null 2>&1; then
  echo "Info.plist version info:"
  PLIST="$APP_PATH/Contents/Info.plist"
  /usr/libexec/PlistBuddy -c "Print :CFBundleShortVersionString" "$PLIST" || true
  /usr/libexec/PlistBuddy -c "Print :CFBundleVersion" "$PLIST" || true
fi

echo "Verification finished. Manually ensure 'universal' appears for critical binaries."
