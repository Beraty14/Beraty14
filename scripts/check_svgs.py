import glob
import xml.etree.ElementTree as ET

def main():
    files = glob.glob("assets/*.svg")
    print(f"Checking {len(files)} compiled SVGs...")
    for f in files:
        try:
            ET.parse(f)
            print(f"  [OK] {f} is valid XML")
        except Exception as e:
            print(f"  [ERROR] {f} is INVALID: {e}")

if __name__ == "__main__":
    main()
