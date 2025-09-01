#!/usr/bin/env python3
"""
CABAS Automation System - Main Application
Spare Parts Automation Project for European Sustainability

This application automates CABAS desktop application interactions
for spare parts sourcing across multiple workshop locations.
"""

import sys
import os
import time
import logging
from typing import Optional

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cabas_automation_desktop import DesktopCABASAutomation
from config_manager import ConfigManager

class CABASAutomationSystem:
    """
    Main CABAS Automation System
    Coordinates all automation components
    """
    
    def __init__(self):
        """
        Initialize the automation system
        """
        self.config_manager = ConfigManager()
        self.cabas_automation = None
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        if not self.config_manager.validate_config():
            raise ValueError("Invalid configuration. Please check config.json")
        
        # Create necessary directories
        self.config_manager.create_directories()
        
        # Initialize CABAS automation
        self.initialize_cabas_automation()
    
    def initialize_cabas_automation(self) -> None:
        """
        Initialize CABAS automation with configuration
        """
        try:
            cabas_config = self.config_manager.get_cabas_config()
            
            self.cabas_automation = DesktopCABASAutomation(
                cabas_exe_path=cabas_config['exe_path'],
                username=cabas_config['username'],
                password=cabas_config['password']
            )
            
            self.logger.info("CABAS automation initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize CABAS automation: {e}")
            raise
    
    def test_cabas_connection(self) -> bool:
        """
        Test CABAS application launch and login
        
        Returns:
            bool: True if test successful, False otherwise
        """
        try:
            self.logger.info("Starting CABAS connection test...")
            
            # Launch CABAS
            if not self.cabas_automation.launch_cabas():
                self.logger.error("Failed to launch CABAS application")
                return False
            
            self.logger.info("CABAS application launched successfully")
            
            # Attempt login
            if not self.cabas_automation.login_to_cabas():
                self.logger.error("Failed to login to CABAS")
                return False
            
            self.logger.info("CABAS login successful")
            
            # Take screenshot for verification
            screenshot_path = self.cabas_automation.take_screenshot("test_login_success.png")
            self.logger.info(f"Screenshot saved: {screenshot_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error during CABAS connection test: {e}")
            return False
    
    def run_interactive_test(self) -> None:
        """
        Run interactive test mode for manual verification
        """
        print("\n" + "="*60)
        print("CABAS Automation System - Interactive Test Mode")
        print("="*60)
        
        try:
            # Display configuration summary
            self.display_config_summary()
            
            # Ask user if they want to proceed
            response = input("\nDo you want to test CABAS connection? (y/n): ").lower().strip()
            
            if response == 'y':
                print("\nStarting CABAS connection test...")
                
                if self.test_cabas_connection():
                    print("\n✅ CABAS connection test SUCCESSFUL!")
                    print("\nThe application should now be logged in to CABAS.")
                    print("Please verify the interface manually.")
                    
                    input("\nPress Enter when you're done testing...")
                else:
                    print("\n❌ CABAS connection test FAILED!")
                    print("Please check the logs for more details.")
            else:
                print("\nTest cancelled by user.")
        
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user.")
        
        except Exception as e:
            print(f"\n❌ Error during interactive test: {e}")
        
        finally:
            # Clean up
            self.cleanup()
    
    def display_config_summary(self) -> None:
        """
        Display configuration summary
        """
        print("\nConfiguration Summary:")
        print("-" * 30)
        
        cabas_config = self.config_manager.get_cabas_config()
        print(f"CABAS Executable: {cabas_config.get('exe_path')}")
        print(f"Username: {cabas_config.get('username')}")
        print(f"Password: {'*' * len(cabas_config.get('password', ''))}")
        
        workshops = self.config_manager.get_all_workshops()
        print(f"\nConfigured Workshops: {len(workshops)}")
        for workshop_id, workshop_config in workshops.items():
            print(f"  - {workshop_config.get('name', workshop_id)}")
    
    def cleanup(self) -> None:
        """
        Clean up resources
        """
        try:
            if self.cabas_automation:
                self.cabas_automation.close_cabas()
                self.logger.info("CABAS automation cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def run_automation_cycle(self) -> None:
        """
        Run a single automation cycle (for future implementation)
        This will be expanded to include Excel monitoring and supplier automation
        """
        # TODO: Implement full automation cycle
        # 1. Monitor Excel spreadsheet for changes
        # 2. Process new orders
        # 3. Execute supplier search automation
        # 4. Update PM system
        # 5. Send Teams notifications
        pass

def main():
    """
    Main entry point
    """
    try:
        # Initialize automation system
        automation_system = CABASAutomationSystem()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == 'test':
                # Run connection test only
                success = automation_system.test_cabas_connection()
                automation_system.cleanup()
                sys.exit(0 if success else 1)
            
            elif command == 'interactive':
                # Run interactive test mode
                automation_system.run_interactive_test()
            
            elif command == 'run':
                # Run full automation (future implementation)
                print("Full automation mode not yet implemented")
                automation_system.cleanup()
            
            else:
                print(f"Unknown command: {command}")
                print("Available commands: test, interactive, run")
                sys.exit(1)
        else:
            # Default to interactive mode
            automation_system.run_interactive_test()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logging.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()