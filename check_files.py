"""Project Structure Verification Tool.

This module verifies that all required files for the Salesforce Org Analyzer
are present in the correct directory structure. It provides helpful error
messages and setup commands if any files are missing.
"""

from pathlib import Path
import sys
from typing import List, Tuple

def check_files() -> bool:
    """Verify the existence of all required project files.
    
    Checks for the presence of all necessary Python modules, package files,
    and configuration files in the expected directory structure. The function
    maintains a comprehensive list of required files and their expected locations.
    
    Returns:
        bool: True if all required files are present, False otherwise.
    """
    # Define all required files for the project
    # Files are listed in logical groups for better maintenance
    required_files = [
        # Core package files
        'src/__init__.py',
        'src/cli.py',
        
        # Apex analysis modules
        'src/apex/__init__.py',
        'src/apex/parser.py',
        'src/apex/analyzer.py',
        
        # Data models
        'src/models/__init__.py',
        'src/models/apex_models.py',
        'src/models/analysis_models.py',
        
        # Automation analysis modules
        'src/automations/__init__.py',
        
        # Execution path analysis and visualization
        'src/execution/__init__.py',
        'src/execution/path_analyzer.py',
        'src/execution/visualizer.py',
        
        # LLM integration
        'src/llm/__init__.py',
        'src/llm/documenter.py',
        
        # Utility modules
        'src/utils/__init__.py',
        'src/utils/sfdx_helper.py',
        
        # Configuration
        'config/default_config.yaml'
    ]

    # Track missing files
    missing = []
    
    # Check each required file
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    # Report results
    if missing:
        print("\n❌ Missing files:")
        for file in missing:
            print(f"  - {file}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

def generate_setup_commands(indent: int = 0) -> List[str]:
    """
        Generate shell commands to create missing project structure.
        Creates a list of shell commands that will set up the complete
        project directory structure and create all necessary files.
        
        Args:
            indent: Number of spaces to indent the commands (default: 0)
        
        Returns:
            List[str]: Shell commands to create project structure
    """
    # Define directory structure and file creation commands
    commands = [
        # Create directory structure
        "mkdir -p src/apex src/models src/automations src/execution src/llm src/utils config",
        # Create core package files
        "touch src/__init__.py src/cli.py",
        # Create Apex analysis files
        "touch src/apex/__init__.py src/apex/parser.py src/apex/analyzer.py",
        # Create model files
        "touch src/models/__init__.py src/models/apex_models.py src/models/analysis_models.py",
        # Create automation files
        "touch src/automations/__init__.py",
        # Create execution analysis files
        "touch src/execution/__init__.py src/execution/path_analyzer.py src/execution/visualizer.py",
        # Create LLM integration files
        "touch src/llm/__init__.py src/llm/documenter.py",
        # Create utility files
        "touch src/utils/__init__.py src/utils/sfdx_helper.py",
        # Create configuration file
        "touch config/default_config.yaml"
    ]
    
    # Apply indentation if requested
    if indent > 0:
        return [" " * indent + cmd for cmd in commands]
    return commands

if __name__ == "__main__":
    # When run as a script, check files and provide setup instructions if needed
    if not check_files():
        print("\nRun these commands to create missing files:")
        
        # Print each setup command on a new line
        for command in generate_setup_commands():
            print(command)
        
        # Exit with error status to indicate missing files
        sys.exit(1)