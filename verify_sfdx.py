"""
    SFDX Project Structure and Authentication Validator.

    This module verifies the essential components of a Salesforce DX project:
        1. Project configuration file (sfdx-project.json)
        2. Required directory structure
        3. Salesforce org authentication status

    Used for ensuring a project is properly configured before running analysis tools.
"""

from pathlib import Path
import json
import subprocess
from typing import Dict, Optional, List

def verify_sfdx_project() -> bool:
    """
        Verify SFDX project structure and authentication status.
        
        Performs comprehensive validation of SFDX project setup:
            1. Checks for sfdx-project.json and validates its contents
            2. Verifies existence of required directories
            3. Confirms Salesforce org authentication
        
        Returns:
            bool: True if all validations pass, False otherwise
        
        Raises:
            JSONDecodeError: If sfdx-project.json is invalid
            subprocess.CalledProcessError: If SFDX CLI commands fail
            
        Example Output:
            === Verifying SFDX Project ===
            
            1. Checking sfdx-project.json:
            ✅ sfdx-project.json found
            Contents: {
                "packageDirectories": [
                {"path": "force-app", "default": true}
                ],
                "namespace": "",
                "sourceApiVersion": "58.0"
            }
            
            2. Checking manifest directory:
            ✅ manifest directory found
            
            3. Checking force-app directory:
            ✅ force-app directory found
            
            4. Checking SFDX authentication:
            ✅ Found authenticated orgs:
            - DevHub (user@example.com)
    """
    # Define project root path - consider making this configurable
    project_path = Path('/Users/reynchr/VSC Projects/docsTest')
    
    print("\n=== Verifying SFDX Project ===\n")
    
    # Step 1: Verify and validate sfdx-project.json
    validation_success = True
    sfdx_project = project_path / 'sfdx-project.json'
    print(f"1. Checking sfdx-project.json:")
    if sfdx_project.exists():
        print("✅ sfdx-project.json found")
        try:
            with open(sfdx_project, 'r') as f:
                config = json.load(f)
                print("  Contents:", json.dumps(config, indent=2))
                # Consider adding validation of required config elements
        except Exception as e:
            print(f"❌ Error reading sfdx-project.json: {str(e)}")
            validation_success = False
    else:
        print("❌ sfdx-project.json not found")
        validation_success = False
    
    # Step 2: Check for manifest directory (package.xml location)
    manifest_dir = project_path / 'manifest'
    print("\n2. Checking manifest directory:")
    if manifest_dir.exists():
        print("✅ manifest directory found")
    else:
        print("❌ manifest directory not found")
        validation_success = False
    
    # Step 3: Verify force-app directory (main source directory)
    force_app = project_path / 'force-app'
    print("\n3. Checking force-app directory:")
    if force_app.exists():
        print("✅ force-app directory found")
    else:
        print("❌ force-app directory not found")
        validation_success = False
    
    # Step 4: Verify SFDX authentication status
    print("\n4. Checking SFDX authentication:")
    try:
        result = subprocess.run(
            ['sfdx', 'force:org:list', '--json'],
            capture_output=True,
            text=True,
            check=True  # Raises CalledProcessError if command fails
        )
        orgs = json.loads(result.stdout)
        if orgs.get('result'):
            print("✅ Found authenticated orgs:")
            for org in orgs['result']:
                if 'alias' in org:
                    print(f"  - {org.get('alias')} ({org.get('username')})")
        else:
            print("❌ No authenticated orgs found")
            validation_success = False
    except subprocess.CalledProcessError:
        print("❌ Error checking org authentication")
        validation_success = False
    except Exception as e:
        print(f"❌ Error running sfdx command: {str(e)}")
        validation_success = False
    
    return validation_success

def validate_sfdx_config(config: Dict) -> List[str]:
    """
        Validate the contents of sfdx-project.json.
        
        Args:
            config: Parsed JSON content of sfdx-project.json
        
        Returns:
            List[str]: List of validation errors, empty if valid
        
        Example:
            errors = validate_sfdx_config(config)
            if errors:
                print("Configuration errors found:", errors)
    """
    errors = []
    required_fields = ['packageDirectories', 'sourceApiVersion']
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    return errors

if __name__ == "__main__":
    # Exit with appropriate status code based on validation result
    import sys
    sys.exit(0 if verify_sfdx_project() else 1)