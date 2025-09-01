import pyautogui
import pygetwindow as gw
import subprocess
import time
import os
import logging
from typing import Optional, Tuple, List, Dict, Any
import psutil
from PIL import Image, ImageGrab
import cv2
import numpy as np
import json
import threading
from datetime import datetime

class DesktopCABASAutomation:
    """
    Enhanced Desktop CABAS Application Automation Class
    Focuses on robust GUI automation with multiple detection strategies
    """
    
    def __init__(self, cabas_exe_path: str, username: str, password: str):
        """
        Initialize enhanced desktop CABAS automation
        
        Args:
            cabas_exe_path: Path to CABAS executable file
            username: CABAS login username
            password: CABAS login password
        """
        self.cabas_exe_path = cabas_exe_path
        self.username = username
        self.password = password
        self.cabas_window = None
        self.process = None
        self.login_attempts = 0
        self.max_login_attempts = 3
        
        # Enhanced timing settings
        self.default_wait = 1.0
        self.long_wait = 3.0
        self.short_wait = 0.5
        self.typing_delay = 0.03
        
        # Configure pyautogui settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.3
        
        # Setup enhanced logging
        self.setup_enhanced_logging()
        self.logger = logging.getLogger(__name__)
        
        # Create necessary directories
        self.create_directories()
        
        # Window detection settings
        self.window_titles = [
            'CAB Service Platform',
            'CAB.Client.Shell',
            'CABAS',
            'CAB',
            'CSP',
            'CabgroupCSP'
        ]
        
        self.logger.info("Enhanced CABAS automation initialized")
    
    def setup_enhanced_logging(self) -> None:
        """
        Setup comprehensive logging system
        """
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format=log_format,
            handlers=[
                logging.FileHandler(f'logs/cabas_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
    
    def create_directories(self) -> None:
        """
        Create necessary directories for screenshots and logs
        """
        directories = ['screenshots', 'logs', 'debug_images']
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def wait_for_condition(self, condition_func, timeout: float = 30.0, check_interval: float = 0.5) -> bool:
        """
        Wait for a condition to be met with timeout
        
        Args:
            condition_func: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
            
        Returns:
            bool: True if condition was met, False if timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if condition_func():
                    return True
            except Exception as e:
                self.logger.debug(f"Condition check failed: {e}")
            time.sleep(check_interval)
        return False
    
    def is_cabas_running(self) -> bool:
        """
        Check if CABAS process is running
        """
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                if proc.info['exe'] and 'CAB' in proc.info['exe']:
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Error checking if CABAS is running: {e}")
            return False
    
    def launch_cabas(self) -> bool:
        """
        Launch CABAS application with enhanced error handling
        """
        try:
            if not os.path.exists(self.cabas_exe_path):
                self.logger.error(f"CABAS executable not found: {self.cabas_exe_path}")
                return False
            
            if self.is_cabas_running():
                self.logger.info("CABAS is already running")
            else:
                self.logger.info(f"Launching CABAS from: {self.cabas_exe_path}")
                self.process = subprocess.Popen([self.cabas_exe_path])
                
                # Wait for process to start
                if not self.wait_for_condition(self.is_cabas_running, timeout=15.0):
                    self.logger.error("CABAS process failed to start")
                    return False
                
                self.logger.info("CABAS process started successfully")
            
            # Find and setup the CABAS window
            return self.find_and_setup_cabas_window()
            
        except Exception as e:
            self.logger.error(f"Error launching CABAS: {e}")
            return False
    
    def find_and_setup_cabas_window(self) -> bool:
        """
        Find CABAS window with enhanced detection and setup
        """
        try:
            self.logger.info("Searching for CABAS window...")
            
            def window_found():
                try:
                    windows = gw.getAllWindows()
                    for window in windows:
                        if window.visible and window.width > 100 and window.height > 100:
                            for title in self.window_titles:
                                if title.lower() in window.title.lower():
                                    self.cabas_window = window
                                    self.logger.info(f"Found CABAS window: '{window.title}' at {window.left},{window.top} size {window.width}x{window.height}")
                                    return True
                except Exception as e:
                    self.logger.debug(f"Error during window search: {e}")
                return False
            
            # Wait for window to appear
            if not self.wait_for_condition(window_found, timeout=30.0):
                self.logger.error("CABAS window not found")
                return False
            
            # Setup window (activate, maximize, bring to front)
            return self.setup_window()
            
        except Exception as e:
            self.logger.error(f"Error finding CABAS window: {e}")
            return False
    
    def refresh_window_reference(self) -> bool:
        """
        Refresh the window reference to handle window state changes
        """
        try:
            if not self.cabas_window:
                return False
            
            # Try to find the window again by title
            original_title = self.cabas_window.title
            windows = gw.getAllWindows()
            
            for window in windows:
                if window.visible and window.title == original_title:
                    self.cabas_window = window
                    return True
            
            # If exact title match fails, try partial match
            for window in windows:
                if window.visible and window.width > 100 and window.height > 100:
                    for title in self.window_titles:
                        if title.lower() in window.title.lower():
                            self.cabas_window = window
                            self.logger.info(f"Refreshed window reference: '{window.title}'")
                            return True
            
            self.logger.warning("Could not refresh window reference")
            return False
            
        except Exception as e:
            self.logger.debug(f"Error refreshing window reference: {e}")
            return False
    
    def setup_window(self) -> bool:
        """
        Setup CABAS window (activate, maximize, bring to front)
        """
        try:
            if not self.cabas_window:
                return False
            
            # Refresh window reference first
            if not self.refresh_window_reference():
                self.logger.warning("Could not refresh window reference, continuing anyway")
            
            # Activate window
            try:
                self.cabas_window.activate()
                time.sleep(self.default_wait)
            except Exception as e:
                self.logger.warning(f"Could not activate window: {e}")
                # Try alternative activation method
                try:
                    import win32gui
                    import win32con
                    hwnd = win32gui.FindWindow(None, self.cabas_window.title)
                    if hwnd:
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(self.default_wait)
                except ImportError:
                    self.logger.debug("win32gui not available for alternative activation")
                except Exception as e2:
                    self.logger.debug(f"Alternative activation failed: {e2}")
            
            # Maximize if not already maximized
            try:
                if not self.cabas_window.isMaximized:
                    self.cabas_window.maximize()
                    time.sleep(self.default_wait)
            except Exception as e:
                self.logger.warning(f"Could not maximize window: {e}")
            
            # Bring to front
            try:
                self.cabas_window.activate()
                time.sleep(self.short_wait)
            except Exception as e:
                self.logger.warning(f"Could not bring window to front: {e}")
            
            self.logger.info("Window setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up window: {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """
        Take screenshot with timestamp
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join("screenshots", filename)
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            self.logger.debug(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return ""
    
    def find_element_by_image(self, image_path: str, confidence: float = 0.8, region: Tuple[int, int, int, int] = None) -> Optional[Tuple[int, int]]:
        """
        Find element on screen using image matching
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
            
            location = pyautogui.locate(image_path, screenshot, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                return (center.x, center.y)
            return None
        except Exception as e:
            self.logger.debug(f"Image matching failed for {image_path}: {e}")
            return None
    
    def find_text_on_screen(self, text: str, region: Tuple[int, int, int, int] = None) -> List[Tuple[int, int]]:
        """
        Find text on screen using OCR
        """
        try:
            import pytesseract
            
            if region:
                screenshot = ImageGrab.grab(bbox=region)
            else:
                screenshot = ImageGrab.grab()
            
            # Convert to OpenCV format
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Use OCR to find text
            data = pytesseract.image_to_data(screenshot_cv, output_type=pytesseract.Output.DICT)
            
            positions = []
            for i, detected_text in enumerate(data['text']):
                if text.lower() in detected_text.lower() and int(data['conf'][i]) > 30:
                    x = data['left'][i] + data['width'][i] // 2
                    y = data['top'][i] + data['height'][i] // 2
                    if region:
                        x += region[0]
                        y += region[1]
                    positions.append((x, y))
            
            return positions
            
        except ImportError:
            self.logger.warning("pytesseract not available for OCR")
            return []
        except Exception as e:
            self.logger.debug(f"OCR text search failed for '{text}': {e}")
            return []
    
    def smart_click(self, x: int, y: int, double_click: bool = False, button: str = 'left'):
        """
        Enhanced click with error handling and verification
        """
        try:
            # Ensure coordinates are within screen bounds
            screen_width, screen_height = pyautogui.size()
            x = max(0, min(x, screen_width - 1))
            y = max(0, min(y, screen_height - 1))
            
            self.logger.debug(f"Clicking at ({x}, {y})")
            
            if double_click:
                pyautogui.doubleClick(x, y, button=button)
            else:
                pyautogui.click(x, y, button=button)
            
            time.sleep(self.short_wait)
            
        except Exception as e:
            self.logger.error(f"Error clicking at ({x}, {y}): {e}")
    
    def smart_type(self, text: str, clear_first: bool = True, slow_typing: bool = True):
        """
        Enhanced text typing with better reliability
        """
        try:
            if clear_first:
                # Clear field using multiple methods
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(self.short_wait)
                pyautogui.press('delete')
                time.sleep(self.short_wait)
                pyautogui.press('backspace')
                time.sleep(self.short_wait)
            
            if slow_typing:
                # Type character by character for reliability
                for char in text:
                    pyautogui.typewrite(char)
                    time.sleep(self.typing_delay)
            else:
                pyautogui.typewrite(text)
            
            time.sleep(self.short_wait)
            self.logger.debug(f"Typed text: {text[:10]}{'...' if len(text) > 10 else ''}")
            
        except Exception as e:
            self.logger.error(f"Error typing text: {e}")
    
    def find_login_fields(self) -> Dict[str, Tuple[int, int]]:
        """
        Find login fields using multiple detection strategies
        """
        fields = {}
        
        if not self.cabas_window:
            return fields
        
        try:
            # Refresh window reference first
            if not self.refresh_window_reference():
                self.logger.warning("Could not refresh window reference for field detection")
                return fields
            
            # Get window region
            window_region = (
                self.cabas_window.left,
                self.cabas_window.top,
                self.cabas_window.width,
                self.cabas_window.height
            )
            
            # Strategy 1: Look for common login field labels
            username_labels = ['username', 'user', 'email', 'login', 'användarnamn']
            password_labels = ['password', 'pass', 'lösenord']
            
            for label in username_labels:
                positions = self.find_text_on_screen(label, window_region)
                if positions:
                    # Assume input field is to the right or below the label
                    x, y = positions[0]
                    fields['username'] = (x + 100, y)
                    break
            
            for label in password_labels:
                positions = self.find_text_on_screen(label, window_region)
                if positions:
                    x, y = positions[0]
                    fields['password'] = (x + 100, y)
                    break
            
            # Strategy 2: Use common positions relative to window
            if not fields:
                center_x = self.cabas_window.left + self.cabas_window.width // 2
                center_y = self.cabas_window.top + self.cabas_window.height // 2
                
                # Common login form positions
                potential_positions = [
                    (center_x, center_y - 60),  # Username above center
                    (center_x, center_y - 20),  # Password near center
                    (center_x, center_y + 20),  # Alternative positions
                ]
                
                if len(potential_positions) >= 2:
                    fields['username'] = potential_positions[0]
                    fields['password'] = potential_positions[1]
            
            self.logger.debug(f"Found login fields: {fields}")
            return fields
            
        except Exception as e:
            self.logger.error(f"Error finding login fields: {e}")
            return fields
    
    def login_method_enhanced_detection(self) -> bool:
        """
        Enhanced login method using multiple detection strategies
        """
        try:
            self.logger.info("Attempting enhanced login detection method")
            
            # Take screenshot for debugging
            self.take_screenshot("login_attempt_start.png")
            
            # Try to setup window if available
            if self.cabas_window:
                try:
                    self.setup_window()
                    time.sleep(self.long_wait)
                except Exception as e:
                    self.logger.warning(f"Window setup failed, continuing without it: {e}")
            
            # Find login fields
            fields = self.find_login_fields()
            
            if 'username' in fields:
                # Click username field
                self.smart_click(fields['username'][0], fields['username'][1])
                time.sleep(self.default_wait)
                
                # Type username
                self.smart_type(self.username)
                time.sleep(self.default_wait)
                
                # Move to password field
                if 'password' in fields:
                    self.smart_click(fields['password'][0], fields['password'][1])
                else:
                    pyautogui.press('tab')  # Try tab navigation
                
                time.sleep(self.default_wait)
                
                # Type password
                self.smart_type(self.password)
                time.sleep(self.default_wait)
                
                # Submit form
                pyautogui.press('enter')
                time.sleep(self.long_wait)
                
                self.logger.info("Login credentials entered successfully")
                return True
            
            else:
                self.logger.warning("Could not locate login fields")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in enhanced login method: {e}")
            return False
    
    def login_method_fallback_coordinates(self) -> bool:
        """
        Fallback login method using coordinate-based approach
        """
        try:
            self.logger.info("Attempting fallback coordinate-based login")
            
            # Get screen dimensions for fallback positioning
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # If we have window info, use it; otherwise use screen center
            if self.cabas_window:
                try:
                    if self.refresh_window_reference():
                        center_x = self.cabas_window.left + self.cabas_window.width // 2
                        center_y = self.cabas_window.top + self.cabas_window.height // 2
                        self.logger.debug(f"Using window-based coordinates: {center_x}, {center_y}")
                    else:
                        self.logger.warning("Using screen-based coordinates as fallback")
                except Exception as e:
                    self.logger.warning(f"Window coordinate calculation failed, using screen center: {e}")
            
            # Try multiple coordinate combinations
            coordinate_sets = [
                # Set 1: Standard center-based positions
                [(center_x, center_y - 50), (center_x, center_y - 10)],
                # Set 2: Slightly offset positions
                [(center_x - 50, center_y - 30), (center_x - 50, center_y + 10)],
                # Set 3: Alternative positions
                [(center_x + 50, center_y - 30), (center_x + 50, center_y + 10)],
                # Set 4: Screen-based fallback positions
                [(screen_width // 2, screen_height // 2 - 60), (screen_width // 2, screen_height // 2 - 20)],
            ]
            
            for i, (username_pos, password_pos) in enumerate(coordinate_sets):
                try:
                    self.logger.debug(f"Trying coordinate set {i+1}: username at {username_pos}, password at {password_pos}")
                    
                    # Click username position
                    self.smart_click(username_pos[0], username_pos[1])
                    time.sleep(self.default_wait)
                    
                    # Type username
                    self.smart_type(self.username)
                    time.sleep(self.default_wait)
                    
                    # Click password position
                    self.smart_click(password_pos[0], password_pos[1])
                    time.sleep(self.default_wait)
                    
                    # Type password
                    self.smart_type(self.password)
                    time.sleep(self.default_wait)
                    
                    # Submit
                    pyautogui.press('enter')
                    time.sleep(self.long_wait)
                    
                    self.logger.info(f"Fallback login attempt {i+1} completed")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"Coordinate set {i+1} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in fallback login method: {e}")
            return False
    
    def login_method_screen_based(self) -> bool:
        """
        Screen-based login method that doesn't rely on window handles
        Specifically designed for the CABAS login window layout
        """
        try:
            self.logger.info("Attempting screen-based login method")
            
            # Get screen dimensions
            screen_width, screen_height = pyautogui.size()
            

            center_x = screen_width // 2
            center_y = screen_height // 2

            username_positions = [
                (center_x, center_y - 80),  # Higher up for username field
                (center_x, center_y - 60),  # Alternative higher position
                (center_x, center_y - 100), # Even higher for small window
                (center_x, center_y - 40),  # Medium height
                (center_x, center_y - 20),  # Slightly above center
                (center_x, center_y),       # Exact center
            ]
            
            for i, username_pos in enumerate(username_positions):
                try:
                    self.logger.debug(f"Trying username position {i+1}: {username_pos}")
                    
                    # Click on the username field
                    pyautogui.click(username_pos[0], username_pos[1])
                    time.sleep(self.default_wait)
                    
                    # Clear any existing text and type username
                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.2)
                    pyautogui.typewrite(self.username, interval=0.05)
                    time.sleep(self.default_wait)
                    
                    # Press Tab to move to password field (if it exists)
                    pyautogui.press('tab')
                    time.sleep(self.default_wait)
                    
                    # Type password
                    pyautogui.typewrite(self.password, interval=0.05)
                    time.sleep(self.default_wait)
                    
                    # Try to find and click the Continue button
                    # Look for blue button in the center area
                    continue_button_positions = [
                        (center_x, center_y + 40),   # Blue Continue button position
                        (center_x, center_y + 60),   # Alternative button position
                        (center_x, center_y + 20),   # Higher button position
                        (center_x, center_y + 80),   # Lower button position
                        (center_x, center_y + 100),  # Even lower position
                    ]
                    
                    button_clicked = False
                    for btn_pos in continue_button_positions:
                        try:
                            pyautogui.click(btn_pos[0], btn_pos[1])
                            button_clicked = True
                            self.logger.debug(f"Clicked Continue button at {btn_pos}")
                            break
                        except:
                            continue
                    
                    # If button click failed, try Enter key
                    if not button_clicked:
                        pyautogui.press('enter')
                        self.logger.debug("Used Enter key as fallback")
                    
                    time.sleep(self.long_wait)
                    
                    self.logger.info(f"Screen-based login attempt {i+1} completed")
                    return True
                    
                except Exception as e:
                    self.logger.warning(f"Username position {i+1} failed: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in screen-based login method: {e}")
            return False
    
    def login_to_cabas(self) -> bool:
        """
        Main login method that tries multiple approaches
        """
        try:
            self.logger.info("Starting CABAS login process")
            
            # Take initial screenshot
            self.take_screenshot("login_start.png")
            
            # Method 1: Enhanced detection
            if self.login_method_enhanced_detection():
                time.sleep(5)  # Wait for login to process
                if self.verify_login_success():
                    self.take_screenshot("login_success.png")
                    self.logger.info("Login successful using enhanced detection")
                    return True
            
            # Method 2: Fallback coordinates
            if self.login_method_fallback_coordinates():
                time.sleep(5)  # Wait for login to process
                if self.verify_login_success():
                    self.take_screenshot("login_success.png")
                    self.logger.info("Login successful using fallback coordinates")
                    return True
            
            # Method 3: Screen-based approach
            if self.login_method_screen_based():
                time.sleep(5)  # Wait for login to process
                if self.verify_login_success():
                    self.take_screenshot("login_success.png")
                    self.logger.info("Login successful using screen-based method")
                    return True
            
            # If all methods fail
            self.take_screenshot("login_failed.png")
            self.logger.error("All login methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in login process: {e}")
            self.take_screenshot("login_error.png")
            return False
    
    def verify_login_success(self) -> bool:
        """
        Enhanced login success verification
        """
        try:
            self.logger.info("Verifying login success")
            time.sleep(self.long_wait)
            
            # Method 1: Check window title changes
            if self.cabas_window:
                try:
                    # Refresh window reference
                    self.cabas_window = gw.getWindowsWithTitle(self.cabas_window.title)[0]
                    current_title = self.cabas_window.title.lower()
                    self.logger.info(f"Current window title: '{current_title}'")
                    
                    # Check for login failure indicators
                    failure_indicators = ['login', 'sign in', 'authentication', 'error', 'invalid']
                    if any(indicator in current_title for indicator in failure_indicators):
                        self.logger.debug("Login failure indicators found in title")
                        return False
                    
                    # Check for success indicators
                    success_indicators = ['dashboard', 'main', 'home', 'workspace', 'platform']
                    if any(indicator in current_title for indicator in success_indicators):
                        self.logger.info("Success indicators found in title")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Window title check failed: {e}")
            
            # Method 2: Look for UI elements that indicate successful login
            if self.cabas_window:
                window_region = (
                    self.cabas_window.left,
                    self.cabas_window.top,
                    self.cabas_window.width,
                    self.cabas_window.height
                )
                
                # Look for success indicators on screen
                success_texts = ['Welcome', 'Dashboard', 'Home', 'Menu', 'Logout', 'Profile', 'Settings']
                for text in success_texts:
                    positions = self.find_text_on_screen(text, window_region)
                    if positions:
                        self.logger.info(f"Found success indicator text: '{text}'")
                        return True
                
                # Look for failure indicators
                failure_texts = ['Invalid', 'Error', 'Failed', 'Incorrect', 'Try again']
                for text in failure_texts:
                    positions = self.find_text_on_screen(text, window_region)
                    if positions:
                        self.logger.warning(f"Found failure indicator text: '{text}'")
                        return False
            
            # Method 3: Check if login form is still visible
            login_form_texts = ['Username', 'Password', 'Login', 'Sign in']
            for text in login_form_texts:
                if self.find_text_on_screen(text):
                    self.logger.debug(f"Login form still visible (found '{text}')")
                    return False
            
            # If no clear indicators, assume success if no login form visible
            self.logger.info("No clear indicators found, assuming login success")
            return True
            
        except Exception as e:
            self.logger.error(f"Error verifying login success: {e}")
            return False
    
    def close_cabas(self) -> bool:
        """
        Enhanced CABAS closing with better error handling
        """
        try:
            self.logger.info("Closing CABAS application")
            
            # Try to close via window
            if self.cabas_window:
                try:
                    self.cabas_window.close()
                    time.sleep(self.default_wait)
                except Exception as e:
                    self.logger.warning(f"Could not close window normally: {e}")
            
            # Try to terminate process
            if self.process:
                try:
                    self.process.terminate()
                    self.process.wait(timeout=5)
                except Exception as e:
                    self.logger.warning(f"Could not terminate process normally: {e}")
                    try:
                        self.process.kill()
                    except Exception as e2:
                        self.logger.error(f"Could not kill process: {e2}")
            
            # Force close any remaining CABAS processes
            try:
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    if proc.info['exe'] and 'CAB' in proc.info['exe']:
                        proc.terminate()
                        time.sleep(1)
                        if proc.is_running():
                            proc.kill()
            except Exception as e:
                self.logger.warning(f"Error force closing CABAS processes: {e}")
            
            self.logger.info("CABAS application closed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error closing CABAS: {e}")
            return False


if __name__ == "__main__":
    # Test the enhanced automation
    config_path = "config.json"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        cabas_config = config.get('cabas', {})
        
        automation = DesktopCABASAutomation(
            cabas_exe_path=cabas_config.get('exe_path', ''),
            username=cabas_config.get('username', ''),
            password=cabas_config.get('password', '')
        )
        
        try:
            print("Testing enhanced CABAS automation...")
            if automation.launch_cabas():
                print("CABAS launched successfully")
                if automation.login_to_cabas():
                    print("Login successful")
                    input("Press Enter to close...")
                else:
                    print("Login failed")
            else:
                print("Failed to launch CABAS")
        finally:
            automation.close_cabas()
    else:
        print("Config file not found")