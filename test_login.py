#!/usr/bin/env python3
"""
Simple test script for CABAS login automation
"""

import pyautogui
import time
import logging
from config_manager import ConfigManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cabas_login():
    """Test the CABAS login process"""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config_loaded = config_manager.load_config()
        
        if not config_loaded:
            logger.error("Failed to load configuration")
            return False
            
        config = config_manager.config
        username = config['cabas']['username']
        password = config['cabas']['password']
        
        logger.info("Starting CABAS login test")
        
        # Get screen dimensions
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        logger.info(f"Screen size: {screen_width}x{screen_height}")
        logger.info(f"Center position: {center_x}, {center_y}")
        
        # Wait for user to position CABAS login window
        print("\nPlease open the CABAS login window and position it on screen.")
        print("Press Enter when ready to start the login test...")
        input()
        
        # Try different username field positions based on CABAS window layout
        username_positions = [
            (center_x, center_y - 80),  # Higher up for username field
            (center_x, center_y - 60),  # Alternative higher position
            (center_x, center_y - 100), # Even higher for small window
            (center_x, center_y - 40),  # Medium height
            (center_x, center_y - 20),  # Slightly above center
            (center_x, center_y),       # Exact center
        ]
        
        for i, pos in enumerate(username_positions):
            try:
                logger.info(f"Trying username position {i+1}: {pos}")
                
                # Click username field
                pyautogui.click(pos[0], pos[1])
                time.sleep(1)
                
                # Clear and type username
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.5)
                pyautogui.typewrite(username, interval=0.1)
                time.sleep(1)
                
                # Press Tab to move to password field
                pyautogui.press('tab')
                time.sleep(1)
                
                # Type password
                pyautogui.typewrite(password, interval=0.1)
                time.sleep(1)
                
                # Try to submit
                logger.info("Attempting to submit login...")
                
                # Try clicking Continue button positions based on CABAS layout
                continue_positions = [
                    (center_x, center_y + 40),  # Blue Continue button position
                    (center_x, center_y + 60),  # Alternative button position
                    (center_x, center_y + 20),  # Higher button position
                    (center_x, center_y + 80),  # Lower button position
                    (center_x, center_y + 100), # Even lower position
                ]
                
                button_found = False
                for btn_pos in continue_positions:
                    try:
                        pyautogui.click(btn_pos[0], btn_pos[1])
                        logger.info(f"Clicked Continue button at {btn_pos}")
                        button_found = True
                        break
                    except:
                        continue
                
                if not button_found:
                    # Fallback to Enter key
                    pyautogui.press('enter')
                    logger.info("Used Enter key as fallback")
                
                time.sleep(3)
                logger.info(f"Login attempt {i+1} completed")
                
                # Ask user if login was successful
                result = input("\nDid the login succeed? (y/n): ").lower().strip()
                if result == 'y':
                    logger.info("Login test successful!")
                    return True
                elif result == 'n':
                    logger.info("Login failed, trying next position...")
                    continue
                else:
                    logger.info("Invalid input, trying next position...")
                    continue
                    
            except Exception as e:
                logger.error(f"Error in position {i+1}: {e}")
                continue
        
        logger.error("All login attempts failed")
        return False
        
    except Exception as e:
        logger.error(f"Error in login test: {e}")
        return False

if __name__ == "__main__":
    test_cabas_login()