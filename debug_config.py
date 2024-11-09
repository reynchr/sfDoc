"""
    Configuration Validation and Debug Tool.

    This module provides debugging utilities for the Salesforce Analyzer configuration,
    verifying file existence, content readability, YAML parsing, and required sections.
    It helps diagnose configuration issues with detailed error reporting.
"""

from pathlib import Path
import yaml
import sys
from typing import Dict, List, Tuple, Optional

def debug_config() -> Optional[Dict]:
    """
        Debug and validate the analyzer configuration file.
        
        Performs a series of checks on the configuration file:
            1. Verifies file existence and accessibility
            2. Checks file content readability
            3. Validates YAML syntax
            4. Confirms presence of required configuration sections
        
        Returns:
            Optional[Dict]: Parsed configuration if successful, None if validation fails
        
        Raises:
            yaml.YAMLError: If YAML syntax is invalid
            IOError: If file cannot be read
            
        Example Output:
            === Checking Configuration ===
            
            1. Checking if config file exists at: /path/to/config.yaml
            ✅ Config file found
            File size: 1234 bytes
            
            2. Reading config file content:
            Raw content length: 1234
            First 500 characters of content:
            --------------------------------------------------
            [Configuration content preview]
            --------------------------------------------------
            
            3. Attempting to parse YAML:
            ✅ All required sections found
            Found sections: ['analysis', 'execution', 'visualization', 'llm']
    """
    # Define path to configuration file
    config_path = Path('config/default_config.yaml')
    
    print("\n=== Checking Configuration ===\n")
    
    # Step 1: Verify file existence and basic properties
    print(f"1. Checking if config file exists at: {config_path.absolute()}")
    if not config_path.exists():
        print(f"❌ Config file not found!")
        return None
    else:
        print(f"✅ Config file found")
        # Report file size to help identify empty or truncated files
        print(f"File size: {config_path.stat().st_size} bytes")
    
    # Step 2: Verify file readability and content
    print("\n2. Reading config file content:")
    try:
        with open(config_path, 'r') as f:
            raw_content = f.read()
            # Report content length for validation
            print("Raw content length:", len(raw_content))
            # Show preview of content for quick verification
            print("\nFirst 500 characters of content:")
            print("-" * 50)
            print(raw_content[:500])
            print("-" * 50)
    except Exception as e:
        print(f"❌ Error reading file: {str(e)}")
        return None
        
    # Step 3: Validate YAML structure and required sections
    print("\n3. Attempting to parse YAML:")
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        # Verify all required configuration sections are present
        required_sections = ['analysis', 'execution', 'visualization', 'llm']
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            print("❌ Missing required sections:", missing_sections)
            return None
        else:
            print("✅ All required sections found")
            
        # Report all found configuration sections
        print("\nFound sections:", list(config.keys()))
        
        return config
        
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Other error: {str(e)}")
        return None

def verify_section_contents(config: Dict) -> List[str]:
    """
        Verify the contents of each configuration section.
        
        Args:
            config: Parsed configuration dictionary
            
        Returns:
            List[str]: List of validation errors, empty if all valid
    """
    errors = []
    
    # Add section content validation as needed
    return errors

if __name__ == "__main__":
    # Run configuration debug when script is executed directly
    if debug_config() is None:
        # Exit with error status if configuration validation fails
        sys.exit(1)