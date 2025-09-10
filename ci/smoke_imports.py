import platform

def main():
    print("Python:", platform.python_version(), platform.platform(), platform.machine())
    mods = ["rumps", "Cocoa", "keyring", "pydexcom"]
    for m in mods:
        try:
            __import__(m)
            print(f"OK import: {m}")
        except Exception as e:
            print(f"FAIL import: {m}: {e}")

if __name__ == "__main__":
    main()
