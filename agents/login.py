"""
Login Agent - Responsible for handling authentication and login processes
"""

import os
import time
import logging
import pywinauto
from pywinauto.keyboard import send_keys
from pywinauto.findwindows import ElementNotFoundError

logger = logging.getLogger(__name__)

class LoginAgent:
    """Agent responsible for handling login and authentication"""
    
    def __init__(self, config, app_launcher):
        self.config = config
        self.app_launcher = app_launcher
        self.credentials = {
            'username': os.getenv('TEST_USERNAME', 'testuser'),
            'password': os.getenv('TEST_PASSWORD', 'testpass')
        }
        self.login_elements = {
            'username_field': 'Username',
            'password_field': 'Password', 
            'login_button': 'Login',
            'dashboard_indicator': 'Dashboard'
        }
    
    def find_login_elements(self):
        """Find login form elements"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                logger.error("No main window available")
                return False
            
            # Try to find username field
            self.username_field = None
            self.password_field = None
            self.login_button = None
            
            # Search for common username field patterns
            username_patterns = ['username', 'user', 'login', 'email']
            password_patterns = ['password', 'pass', 'pwd']
            button_patterns = ['login', 'sign in', 'enter', 'ok']
            
            # Find all edit controls
            edit_controls = main_window.descendants(control_type="Edit")
            
            if len(edit_controls) >= 2:
                self.username_field = edit_controls[0]
                self.password_field = edit_controls[1]
                logger.info("Found username and password fields")
            else:
                logger.error("Could not find sufficient input fields")
                return False
            
            # Find login button
            buttons = main_window.descendants(control_type="Button")
            for button in buttons:
                button_text = button.window_text().lower()
                if any(pattern in button_text for pattern in button_patterns):
                    self.login_button = button
                    logger.info(f"Found login button: {button.window_text()}")
                    break
            
            if not self.login_button:
                logger.error("Could not find login button")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to find login elements: {str(e)}")
            return False
    
    def enter_credentials(self):
        """Enter login credentials"""
        try:
            # Clear and enter username
            if self.username_field:
                self.username_field.click_input()
                send_keys('^a')  # Select all
                send_keys('{DEL}')  # Delete
                self.username_field.type_keys(self.credentials['username'])
                logger.info("Username entered")
            else:
                logger.error("Username field not available")
                return False
            
            time.sleep(1)
            
            # Clear and enter password
            if self.password_field:
                self.password_field.click_input()
                send_keys('^a')  # Select all
                send_keys('{DEL}')  # Delete
                self.password_field.type_keys(self.credentials['password'])
                logger.info("Password entered")
            else:
                logger.error("Password field not available")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to enter credentials: {str(e)}")
            return False
    
    def click_login_button(self):
        """Click the login button"""
        try:
            if self.login_button:
                self.login_button.click()
                logger.info("Login button clicked")
                
                # Wait for login process
                time.sleep(3)
                return True
            else:
                logger.error("Login button not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to click login button: {str(e)}")
            return False
    
    def verify_login_success(self):
        """Verify that login was successful"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                logger.error("No main window available for verification")
                return False
            
            # Wait for potential screen changes
            time.sleep(5)
            
            # Look for dashboard indicators
            dashboard_indicators = [
                'dashboard', 'main menu', 'home', 'welcome',
                'account', 'balance', 'transactions'
            ]
            
            # Check window title
            window_title = main_window.window_text().lower()
            if any(indicator in window_title for indicator in dashboard_indicators):
                logger.info(f"Login success detected in window title: {window_title}")
                return True
            
            # Check for dashboard elements
            try:
                # Look for common dashboard elements
                all_controls = main_window.descendants()
                for control in all_controls:
                    control_text = control.window_text().lower()
                    if any(indicator in control_text for indicator in dashboard_indicators):
                        logger.info(f"Login success detected - found dashboard element: {control_text}")
                        return True
            except:
                pass
            
            # If no specific indicators found, assume success if no error dialogs
            error_indicators = ['error', 'invalid', 'failed', 'incorrect']
            for control in main_window.descendants():
                control_text = control.window_text().lower()
                if any(error in control_text for error in error_indicators):
                    logger.error(f"Login error detected: {control_text}")
                    return False
            
            # Default to success if no errors found
            logger.info("Login appears successful - no error indicators found")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify login success: {str(e)}")
            return False
    
    def handle_login_errors(self):
        """Handle any login error dialogs"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                return False
            
            # Look for error dialogs
            error_patterns = ['error', 'invalid', 'failed', 'warning']
            
            dialogs = main_window.descendants(control_type="Dialog")
            for dialog in dialogs:
                dialog_text = dialog.window_text().lower()
                if any(pattern in dialog_text for pattern in error_patterns):
                    logger.warning(f"Error dialog detected: {dialog_text}")
                    
                    # Try to close the dialog
                    ok_buttons = dialog.descendants(control_type="Button")
                    for button in ok_buttons:
                        if 'ok' in button.window_text().lower():
                            button.click()
                            logger.info("Error dialog closed")
                            break
                    
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to handle login errors: {str(e)}")
            return False
    
    def execute_task(self):
        """Execute the login task"""
        logger.info("Starting Login Agent task")
        
        # Take screenshot before login
        screenshot_before = self.app_launcher.take_screenshot("before_login")
        
        # Find login elements
        if not self.find_login_elements():
            return {
                'status': 'FAILED',
                'message': 'Could not find login elements',
                'screenshot': self.app_launcher.take_screenshot("login_elements_not_found")
            }
        
        # Enter credentials
        if not self.enter_credentials():
            return {
                'status': 'FAILED', 
                'message': 'Failed to enter credentials',
                'screenshot': self.app_launcher.take_screenshot("credentials_entry_failed")
            }
        
        # Take screenshot after entering credentials
        screenshot_credentials = self.app_launcher.take_screenshot("credentials_entered")
        
        # Click login button
        if not self.click_login_button():
            return {
                'status': 'FAILED',
                'message': 'Failed to click login button',
                'screenshot': self.app_launcher.take_screenshot("login_button_failed")
            }
        
        # Handle any error dialogs
        self.handle_login_errors()
        
        # Verify login success
        if not self.verify_login_success():
            return {
                'status': 'FAILED',
                'message': 'Login verification failed',
                'screenshot': self.app_launcher.take_screenshot("login_verification_failed")
            }
        
        # Take screenshot after successful login
        screenshot_after = self.app_launcher.take_screenshot("after_login")
        
        return {
            'status': 'PASSED',
            'message': 'Login completed successfully',
            'screenshots': {
                'before': screenshot_before,
                'credentials_entered': screenshot_credentials,
                'after': screenshot_after
            }
        }