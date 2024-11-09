"""Utilities for working with Salesforce DX projects."""

import subprocess
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Union
import yaml

logger = logging.getLogger(__name__)

class SFDXHelper:
    """Helper class for interacting with Salesforce DX projects."""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self._validate_sfdx_project()
        
    def _validate_sfdx_project(self):
        """Validate that the path contains a valid SFDX project."""
        sfdx_project_path = self.project_path / 'sfdx-project.json'
        if not sfdx_project_path.exists():
            raise ValueError(f"No sfdx-project.json found in {self.project_path}")
            
    def get_metadata(self, metadata_type: str) -> List[Dict]:
        """Retrieve metadata of specified type from the project."""
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
        """Retrieve source files using a package.xml."""
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
        """Create a package.xml file for metadata retrieval."""
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
        """Generate the types sections for package.xml."""
        types_xml = []
        for metadata_type in metadata_types:
            types_xml.append(f"""    <types>
        <members>*</members>
        <name>{metadata_type}</name>
    </types>""")
        return '\n'.join(types_xml)
    
    def get_org_metadata_info(self) -> Dict:
        """Get information about all metadata types in the org."""
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
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path('config/default_config.yaml')
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load and validate configuration."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        self._validate_config(config)
        return config
    
    def _validate_config(self, config: Dict):
        """Validate the configuration structure."""
        required_sections = ['analysis', 'execution', 'visualization', 'llm']
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required config section: {section}")
    
    def update_config(self, updates: Dict):
        """Update configuration with new values."""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d:
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d
            
        self.config = deep_update(self.config, updates)
        self._save_config()
    
    def _save_config(self):
        """Save the current configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False)
    
    def get_section(self, section: str) -> Dict:
        """Get a specific section of the configuration."""
        if section not in self.config:
            raise KeyError(f"Configuration section not found: {section}")
        return self.config[section]

class LogManager:
    """Manages logging configuration and setup."""
    
    def __init__(self, config: Dict):
        self.config = config.get('logging', {})
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging based on configuration."""
        log_level = getattr(logging, self.config.get('level', 'INFO'))
        log_format = self.config.get('format', 
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Create logs directory if it doesn't exist
        log_file = self.config.get('file', 'logs/analyzer.log')
        Path(log_file).parent.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

def get_salesforce_api_version() -> str:
    """Get the current Salesforce API version."""
    try:
        result = subprocess.run(
            ['sfdx', 'force:org:display', '--json'],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data['result'].get('apiVersion', '58.0')
    except Exception:
        return '58.0'  # Default to a recent API version if unable to determine