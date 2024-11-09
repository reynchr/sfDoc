"""
    Utilities for working with Salesforce DX projects.

    This module provides helper classes and functions for interacting with Salesforce DX
    projects, managing configuration, and handling logging. It includes functionality for
    metadata retrieval, package.xml generation, and project validation.
"""

import subprocess
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Union
import yaml

logger = logging.getLogger(__name__)

class SFDXHelper:
    """
        Helper class for interacting with Salesforce DX projects.
        
        Provides functionality for:
        - Project validation
        - Metadata retrieval
        - Source code retrieval
        - Package.xml generation
        
        Args:
            project_path: Path to the root of the SFDX project
            
        Raises:
            ValueError: If project_path does not contain a valid SFDX project
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self._validate_sfdx_project()
        
    def _validate_sfdx_project(self):
        """
            Validate that the path contains a valid SFDX project.
            
            Raises:
                ValueError: If sfdx-project.json is not found
        """
        sfdx_project_path = self.project_path / 'sfdx-project.json'
        if not sfdx_project_path.exists():
            raise ValueError(f"No sfdx-project.json found in {self.project_path}")
            
    def get_metadata(self, metadata_type: str) -> List[Dict]:
        """
            Retrieve metadata of specified type from the project.
            
            Args:
                metadata_type: Salesforce metadata type (e.g., 'ApexClass', 'CustomObject')
                
            Returns:
                List[Dict]: List of metadata components, empty if retrieval fails
                
            Example:
                >>> helper.get_metadata('ApexClass')
                [{'fullName': 'MyClass', 'id': '01p...', 'type': 'ApexClass'}]
        """
        try:
            result = subprocess.run(
                ['sfdx', 'force:mdapi:listmetadata', 
                 '-m', metadata_type, 
                 '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)['result']
        except subprocess.CalledProcessError as e:
            logger.error(f"Error retrieving metadata: {str(e)}")
            return []
            
    def retrieve_source(self, package_xml_path: Path, target_path: Optional[Path] = None) -> bool:
        """
            Retrieve source files using a package.xml.
            
            Args:
                package_xml_path: Path to package.xml file defining components to retrieve
                target_path: Optional target directory for retrieved files
                            Defaults to force-app directory in project
            
            Returns:
                bool: True if retrieval successful, False otherwise
                
            Example:
                >>> helper.retrieve_source(Path('manifest/package.xml'))
                True
        """
        target_path = target_path or self.project_path / 'force-app'
        try:
            subprocess.run(
                ['sfdx', 'force:source:retrieve',
                 '-x', str(package_xml_path),
                 '-r', str(target_path)],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Error retrieving source: {str(e)}")
            return False

    def create_package_xml(self, metadata_types: List[str], api_version: str = '58.0') -> Path:
        """
            Create a package.xml file for metadata retrieval.
            
            Args:
                metadata_types: List of Salesforce metadata types to include
                api_version: Salesforce API version to use
                
            Returns:
                Path: Path to generated package.xml file
                
            Example:
                >>> helper.create_package_xml(['ApexClass', 'CustomObject'])
                PosixPath('manifest/package.xml')
        """
        package_xml = self.project_path / 'manifest' / 'package.xml'
        package_xml.parent.mkdir(exist_ok=True)
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    {self._generate_package_xml_types(metadata_types)}
    <version>{api_version}</version>
</Package>"""
        
        with open(package_xml, 'w') as f:
            f.write(xml_content)
            
        return package_xml
    
    def _generate_package_xml_types(self, metadata_types: List[str]) -> str:
        """
            Generate the types sections for package.xml.
            
            Args:
                metadata_types: List of metadata types to include
                
            Returns:
                str: XML string containing type elements
        """
        types_xml = []
        for metadata_type in metadata_types:
            types_xml.append(f"""    <types>
        <members>*</members>
        <name>{metadata_type}</name>
    </types>""")
        return '\n'.join(types_xml)
    
    def get_org_metadata_info(self) -> Dict:
        """
            Get information about all metadata types in the org.
            
            Returns:
                Dict: Metadata type information, empty if retrieval fails
                
            Example:
                >>> helper.get_org_metadata_info()
                {'metadataObjects': [...], 'organizationNamespace': ''}
        """
        try:
            result = subprocess.run(
                ['sfdx', 'force:mdapi:describemetadata', '--json'],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)['result']
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting metadata info: {str(e)}")
            return {}

class ConfigManager:
    """
        Manages configuration loading and validation for the analyzer.
        
        Handles loading, validating, updating, and saving configuration settings
        from YAML files. Ensures all required configuration sections are present
        and properly formatted.
        
        Args:
            config_path: Optional path to configuration file
                        Defaults to 'config/default_config.yaml'
        
        Raises:
            FileNotFoundError: If configuration file not found
            ValueError: If required configuration sections are missing
        
        Example:
            >>> config_manager = ConfigManager()
            >>> analysis_config = config_manager.get_section('analysis')
            >>> config_manager.update_config({'analysis': {'new_setting': True}})
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path('config/default_config.yaml')
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """
            Load and validate configuration from YAML file.
            
            Returns:
                Dict: Validated configuration dictionary
                
            Raises:
                FileNotFoundError: If configuration file doesn't exist
                yaml.YAMLError: If YAML parsing fails
                ValueError: If configuration validation fails
                
            Example:
                >>> config = config_manager.load_config()
                >>> print(config['analysis']['parser'])
                {'include_inner_classes': True, ...}
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self._validate_config(config)
        return config
    
    def _validate_config(self, config: Dict):
        """
            Validate the configuration structure.
            
            Checks for required sections and their expected structure.
            
            Args:
                config: Configuration dictionary to validate
                
            Raises:
                ValueError: If required sections are missing
        """
        required_sections = ['analysis', 'execution', 'visualization', 'llm']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
    
    def update_config(self, updates: Dict):
        """
            Update configuration with new values.
            
            Performs deep update of configuration, preserving existing values
            not specified in the update.
            
            Args:
                updates: Dictionary containing configuration updates
                
            Example:
                >>> config_manager.update_config({
                ...     'analysis': {'parser': {'include_comments': True}}
                ... })
        """
        def deep_update(d: Dict, u: Dict) -> Dict:
            """Recursively update dictionary values."""
            for k, v in u.items():
                if isinstance(v, dict) and k in d:
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d
            
        self.config = deep_update(self.config, updates)
        self._save_config()
    
    def _save_config(self):
        """
            Save the current configuration to file.
            Writes configuration in YAML format with human-readable formatting.
        """
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)
    
    def get_section(self, section: str) -> Dict:
        """
            Get a specific section of the configuration.
            
            Args:
                section: Name of configuration section to retrieve
                
            Returns:
                Dict: Configuration section contents
                
            Raises:
                KeyError: If requested section doesn't exist
                
            Example:
                >>> llm_config = config_manager.get_section('llm')
                >>> print(llm_config['model'])
                'codellama/CodeLlama-7b-hf'
        """
        if section not in self.config:
            raise KeyError(f"Configuration section not found: {section}")
        return self.config[section]

class LogManager:
    """
        Manages logging configuration and setup.
        
        Configures logging based on configuration settings, including:
            - Log levels
            - Output formats
            - File and console handlers
        
        Args:
            config: Configuration dictionary containing logging settings
        
        Configuration Example:
            logging:
            level: INFO
            file: logs/analyzer.log
            format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    """
    
    def __init__(self, config: Dict):
        """
            Initialize logging manager with configuration.
            
            Args:
                config: Configuration dictionary containing logging settings
        """
        self.config = config.get('logging', {})
        self._setup_logging()
        
    def _setup_logging(self):
        """
            Configure logging based on configuration.
            
            Sets up:
                1. Log level from configuration or defaults to INFO
                2. Log format with timestamps and levels
                3. File output with automatic directory creation
                4. Console output for immediate feedback
            
            Example Configuration Result:
                2024-01-01 12:00:00 - analyzer - INFO - Starting analysis...
        """
        # Get log level from string name
        log_level = getattr(logging, self.config.get('level', 'INFO'))
        # Get format string with default
        log_format = self.config.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # Ensure log directory exists
        log_file = self.config.get('file', 'logs/analyzer.log')
        Path(log_file).parent.mkdir(exist_ok=True)
        # Configure logging with both file and console output
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

def get_salesforce_api_version() -> str:
    """
        Get the current Salesforce API version from the authenticated org.
        
        Attempts to retrieve the API version from the currently authenticated org.
        Falls back to a recent default version if retrieval fails.
        
        Returns:
            str: Salesforce API version (e.g., '58.0')
        
        Example:
            >>> version = get_salesforce_api_version()
            >>> print(version)
            '58.0'
    """
    try:
        # Attempt to get version from org
        result = subprocess.run(
            ['sfdx', 'force:org:display', '--json'],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data['result'].get('apiVersion', '58.0')
    except Exception:
        # Fall back to default version
        return '58.0'  # Default to a recent API version if unable to determine