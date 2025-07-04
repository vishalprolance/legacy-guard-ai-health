"""
App Launcher Agent - Responsible for launching the bank application
"""

import os
import time
import logging
import subprocess
import pywinauto
from pywinauto.application import Application
from pywinauto.findwindows import ElementNotFoundError

logger = logging.getLogger(__name__)

class AppLauncherAgent:
    """Agent responsible for launching and initializing the bank application"""
    
    def __init__(self, config):
        self.config = config
        self.app_config = config.get('app_config', {})
        self.app_path = self.app_config.get('app_path', '')
        self.app_title = self.app_config.get('app_title', 'Bank Application')
        self.timeout = self.app_config.get('timeout', 30)
        self.app = None
        self.main_window = None
    
    def launch_application(self):
        """Launch the bank application"""
        logger.info(f"Launching application: {self.app_path}")
        
        try:
            # Check if application file exists
            if not os.path.exists(self.app_path):
                raise FileNotFoundError(f"Application not found: {self.app_path}")
            
            # Launch the application
            self.app = Application().start(self.app_path)
            logger.info("Application started successfully")
            
            # Wait for application to initialize
            time.sleep(5)
            
            # Connect to the main window
            self.connect_to_main_window()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch application: {str(e)}")
            return False
    
    def connect_to_main_window(self):
        """Connect to the main application window"""
        try:
            # Try to connect by window title
            self.app = Application().connect(title_re=f".*{self.app_title}.*")
            self.main_window = self.app.window(title_re=f".*{self.app_title}.*")
            
            # Wait for window to be ready
            self.main_window.wait('ready', timeout=self.timeout)
            
            logger.info("Connected to main application window")
            return True
            
        except ElementNotFoundError:
            logger.error(f"Could not find window with title containing: {self.app_title}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to main window: {str(e)}")
            return False
    
    def verify_application_ready(self):
        """Verify that the application is ready for interaction"""
        try:
            if not self.main_window:
                return False
            
            # Check if window is visible and enabled
            if not self.main_window.is_visible():
                logger.error("Main window is not visible")
                return False
            
            if not self.main_window.is_enabled():
                logger.error("Main window is not enabled")
                return False
            
            # Take initial screenshot
            self.take_screenshot("app_launched")
            
            logger.info("Application is ready for interaction")
            return True
            
        except Exception as e:
            logger.error(f"Application readiness check failed: {str(e)}")
            return False
    
    def take_screenshot(self, name):
        """Take screenshot of the current application state"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{name}_{timestamp}.png"
            
            if self.main_window:
                self.main_window.capture_as_image().save(screenshot_path)
                logger.info(f"Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                logger.error("No main window available for screenshot")
                return None
                
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def get_window_info(self):
        """Get information about the current window"""
        try:
            if not self.main_window:
                return None
            
            info = {
                'title': self.main_window.window_text(),
                'class_name': self.main_window.class_name(),
                'is_visible': self.main_window.is_visible(),
                'is_enabled': self.main_window.is_enabled(),
                'rectangle': self.main_window.rectangle()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get window info: {str(e)}")
            return None
    
    def close_application(self):
        """Close the application safely"""
        try:
            if self.main_window:
                self.main_window.close()
                logger.info("Application closed successfully")
                return True
            else:
                logger.warning("No application window to close")
                return True
                
        except Exception as e:
            logger.error(f"Failed to close application: {str(e)}")
            return False
    
    def execute_task(self):
        """Execute the app launcher task"""
        logger.info("Starting App Launcher Agent task")
        
        # Launch application
        if not self.launch_application():
            return {
                'status': 'FAILED',
                'message': 'Failed to launch application',
                'screenshot': None
            }
        
        # Verify application is ready
        if not self.verify_application_ready():
            return {
                'status': 'FAILED',
                'message': 'Application not ready for interaction',
                'screenshot': self.take_screenshot("app_not_ready")
            }
        
        # Get window information
        window_info = self.get_window_info()
        
        return {
            'status': 'PASSED',
            'message': 'Application launched successfully',
            'screenshot': self.take_screenshot("app_ready"),
            'window_info': window_info
        }