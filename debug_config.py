# debug_config.py
from pathlib import Path
import yaml
import sys

def debug_config():
    config_path = Path('config/default_config.yaml')

    print("\n=== Checking Configuration ===\n")

    # Check if config file exists
    print(f"1. Checking if config file exists at: {config_path.absolute()}")
    if not config_path.exists():
        print(f"❌ Config file not found!")
        return
    else:
        print(f"✅ Config file found")
        print(f"File size: {config_path.stat().st_size} bytes")

    # Try to read the file
    print("\n2. Reading config file content:")
    try:
        with open(config_path, 'r') as f:
            raw_content = f.read()
            print("Raw content length:", len(raw_content))
            print("\nFirst 500 characters of content:")
            print("-" * 50)
            print(raw_content[:500])
            print("-" * 50)
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return

    # Try to parse YAML
    print("\n3. Attempting to parse YAML:")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Check required sections
        required_sections = ['analysis', 'execution', 'visualization', 'llm']
        missing_sections = [section for section in required_sections if section not in config]

        if missing_sections:
            print("❌ Missing required sections:", missing_sections)
        else:
            print("✅ All required sections found")

        print("\nFound sections:", list(config.keys()))

    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {str(e)}")
    except Exception as e:
        print(f"❌ Other error: {str(e)}")

if __name__ == "__main__":
    debug_config()