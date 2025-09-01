import json
import os
import logging
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Configuration Manager for CABAS Automation System
    Handles loading and managing configuration settings
    """
    
    def __init__(self, config_file_path: str = "config.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file_path: Path to configuration JSON file
        """
        self.config_file_path = config_file_path
        self.config = {}
        self.load_config()
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> bool:
        """
        Load configuration from JSON file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if not os.path.exists(self.config_file_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_file_path}")
            
            with open(self.config_file_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Save current configuration to JSON file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error saving configuration: {e}")
            else:
                print(f"Error saving configuration: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to configuration value (e.g., 'cabas.username')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        try:
            keys = key_path.split('.')
            value = self.config
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return default
            
            return value
            
        except Exception:
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value using dot notation
        
        Args:
            key_path: Dot-separated path to configuration value
            value: Value to set
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        try:
            keys = key_path.split('.')
            config_ref = self.config
            
            # Navigate to the parent of the target key
            for key in keys[:-1]:
                if key not in config_ref:
                    config_ref[key] = {}
                config_ref = config_ref[key]
            
            # Set the final value
            config_ref[keys[-1]] = value
            return True
            
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error setting configuration value: {e}")
            return False
    
    def get_cabas_config(self) -> Dict[str, Any]:
        """
        Get CABAS-specific configuration
        
        Returns:
            Dict containing CABAS configuration
        """
        return self.get('cabas', {})
    
    def get_workshop_config(self, workshop_id: str) -> Dict[str, Any]:
        """
        Get configuration for specific workshop
        
        Args:
            workshop_id: Workshop identifier
            
        Returns:
            Dict containing workshop configuration
        """
        return self.get(f'workshops.{workshop_id}', {})
    
    def get_all_workshops(self) -> Dict[str, Dict[str, Any]]:
        """
        Get configuration for all workshops
        
        Returns:
            Dict containing all workshop configurations
        """
        return self.get('workshops', {})
    
    def get_pm_config(self) -> Dict[str, Any]:
        """
        Get PM system configuration
        
        Returns:
            Dict containing PM system configuration
        """
        return self.get('pm_system', {})
    
    def get_excel_config(self) -> Dict[str, Any]:
        """
        Get Excel monitoring configuration
        
        Returns:
            Dict containing Excel monitoring configuration
        """
        return self.get('excel_monitoring', {})
    
    def get_supplier_config(self) -> Dict[str, Any]:
        """
        Get supplier automation configuration
        
        Returns:
            Dict containing supplier automation configuration
        """
        return self.get('supplier_automation', {})
    
    def get_teams_config(self) -> Dict[str, Any]:
        """
        Get Teams integration configuration
        
        Returns:
            Dict containing Teams integration configuration
        """
        return self.get('teams_integration', {})
    
    def setup_logging(self) -> None:
        """
        Setup logging configuration based on config file
        """
        try:
            log_config = self.get('logging', {})
            log_level = log_config.get('level', 'INFO')
            log_file = log_config.get('file_path', 'logs/automation.log')
            
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Configure logging
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_file, encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
    
    def validate_config(self) -> bool:
        """
        Validate configuration completeness
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_sections = ['cabas', 'workshops', 'pm_system', 'excel_monitoring']
        
        for section in required_sections:
            if not self.get(section):
                if hasattr(self, 'logger'):
                    self.logger.error(f"Missing required configuration section: {section}")
                return False
        
        # Validate CABAS configuration
        cabas_config = self.get_cabas_config()
        required_cabas_fields = ['exe_path', 'username', 'password']
        
        for field in required_cabas_fields:
            if not cabas_config.get(field):
                if hasattr(self, 'logger'):
                    self.logger.error(f"Missing required CABAS configuration: {field}")
                return False
        
        return True
    
    def create_directories(self) -> None:
        """
        Create necessary directories based on configuration
        """
        try:
            # Create screenshot directory
            screenshot_path = self.get('cabas.screenshot_path', 'screenshots')
            if not os.path.exists(screenshot_path):
                os.makedirs(screenshot_path)
            
            # Create logs directory
            log_file = self.get('logging.file_path', 'logs/automation.log')
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            if hasattr(self, 'logger'):
                self.logger.info("Required directories created")
                
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error creating directories: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Validate configuration
    if config_manager.validate_config():
        print("Configuration is valid")
        
        # Create necessary directories
        config_manager.create_directories()
        
        # Example: Get CABAS configuration
        cabas_config = config_manager.get_cabas_config()
        print(f"CABAS executable path: {cabas_config.get('exe_path')}")
        
        # Example: Get workshop configuration
        workshop_config = config_manager.get_workshop_config('bil_goteborg')
        print(f"Workshop name: {workshop_config.get('name')}")
        
        # Example: Update configuration
        config_manager.set('cabas.timeout_seconds', 45)
        config_manager.save_config()
        
    else:
        print("Configuration validation failed")