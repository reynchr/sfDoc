"""
    Project Structure Verification Tool.

    This module verifies that all required files and directories for the Salesforce
    Analyzer project are present in the expected locations. It checks for core
    Python modules, package initialization files, and configuration files.

    Usage:
        python check_structure.py
"""

from pathlib import Path
from typing import List, Tuple, Dict
import sys

def check_structure() -> Tuple[bool, List[str]]:
    """
        Verify the existence of all required project files and directories.

        Checks for the presence of:
            1. Core package files (__init__.py, cli.py)
            2. Module-specific initialization files
            3. Key implementation files (parser.py, analyzer.py)
            4. Configuration files (default_config.yaml)

        Returns:
            Tuple[bool, List[str]]: 
                - Boolean indicating if all files are present
                - List of missing file paths

        Example:
            success, missing = check_structure()
            if not success:
                print("Missing files:", missing)
    """
    # Define required project files and directories
    # Grouped by module for better organization
    required_paths = [
        # Core package files
        'src/__init__.py',
        'src/cli.py',
        # Apex analysis module
        'src/apex/__init__.py',
        'src/apex/parser.py',
        'src/apex/analyzer.py',
        # Data models
        'src/models/__init__.py',
        # Automation analysis modules
        'src/automations/__init__.py',
        # Execution path analysis
        'src/execution/__init__.py',
        # LLM integration
        'src/llm/__init__.py',
        # Utility modules
        'src/utils/__init__.py',
        # Configuration
        'config/default_config.yaml'
    ]
    # Track missing files
    missing: List[str] = []
    # Check each required path
    for path in required_paths:
        if not Path(path).exists():
            missing.append(path)
    # Report results
    if missing:
        print("\n❌ Missing files/directories:")
        for path in missing:
            print(f"  - {path}")
        return False, missing
    else:
        print("\n✅ All required files present!")
        return True, []

def generate_creation_commands(missing_paths: List[str]) -> List[str]:
    """
        Generate shell commands to create missing files and directories.
        Args:
            missing_paths: List of paths that need to be created
            
        Returns:
            List[str]: Shell commands to create the missing files
            
        Example:
            commands = generate_creation_commands(missing)
            for cmd in commands:
                print(cmd)
    """
    # Group paths by directory for efficient creation
    directories = set(str(Path(path).parent) for path in missing_paths)
    commands = []
    # Create mkdir commands for missing directories
    if directories:
        dir_list = ' '.join(directories)
        commands.append(f"mkdir -p {dir_list}")
    # Create touch commands for missing files
    if missing_paths:
        file_list = ' '.join(missing_paths)
        commands.append(f"touch {file_list}")
    return commands

def check_file_contents() -> Dict[str, bool]:
    """
        Verify that key files contain required content.
        Returns:
            Dict[str, bool]: Mapping of file paths to content validation results
    """
    content_checks = {}
    # Add specific content checks as needed
    return content_checks

if __name__ == "__main__":
    # Run structure check
    success, missing_files = check_structure()
    if not success:
        print("\nTo create missing files, run these commands:")
        commands = generate_creation_commands(missing_files)
        for cmd in commands:
            print(f"\n{cmd}")
        # Exit with error status for CI/CD integration
        sys.exit(1)
    # Exit with success status
    sys.exit(0)