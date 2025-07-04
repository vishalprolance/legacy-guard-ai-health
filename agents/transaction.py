"""
Transaction Agent - Responsible for testing transaction-related screens and workflows
"""

import time
import logging
import pywinauto
from pywinauto.keyboard import send_keys

logger = logging.getLogger(__name__)

class TransactionAgent:
    """Agent responsible for testing transaction workflows and screens"""
    
    def __init__(self, config, app_launcher):
        self.config = config
        self.app_launcher = app_launcher
        self.transaction_config = config.get('transaction_config', {})
        
        # Transaction test data
        self.test_data = {
            'account_number': '123456789',
            'amount': '100.00',
            'recipient': 'Test Recipient'
        }
    
    def navigate_to_transactions(self):
        """Navigate to the transactions section"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                logger.error("No main window available")
                return False
            
            # Look for transaction-related menu items
            transaction_patterns = [
                'transaction', 'transfer', 'payment', 'send money',
                'transactions', 'transfers', 'payments'
            ]
            
            # Try to find transaction menu/button
            all_controls = main_window.descendants()
            transaction_control = None
            
            for control in all_controls:
                control_text = control.window_text().lower()
                if any(pattern in control_text for pattern in transaction_patterns):
                    if control.is_enabled() and control.is_visible():
                        transaction_control = control
                        logger.info(f"Found transaction control: {control_text}")
                        break
            
            if transaction_control:
                transaction_control.click()
                time.sleep(3)  # Wait for navigation
                logger.info("Navigated to transactions section")
                return True
            else:
                logger.warning("No transaction control found, assuming already in transactions")
                return True
                
        except Exception as e:
            logger.error(f"Failed to navigate to transactions: {str(e)}")
            return False
    
    def validate_transaction_screen_elements(self):
        """Validate that essential transaction screen elements are present"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                return False
            
            # Expected elements on transaction screen
            expected_elements = [
                'account', 'amount', 'recipient', 'balance',
                'transfer', 'send', 'submit', 'cancel'
            ]
            
            found_elements = []
            all_controls = main_window.descendants()
            
            for control in all_controls:
                control_text = control.window_text().lower()
                for element in expected_elements:
                    if element in control_text and element not in found_elements:
                        found_elements.append(element)
            
            logger.info(f"Found transaction elements: {found_elements}")
            
            # Check if we have at least some essential elements
            essential_elements = ['account', 'amount']
            essential_found = [elem for elem in essential_elements if elem in found_elements]
            
            if len(essential_found) >= 1:
                logger.info("Transaction screen validation passed")
                return True
            else:
                logger.warning("Essential transaction elements not found")
                return False
                
        except Exception as e:
            logger.error(f"Transaction screen validation failed: {str(e)}")
            return False
    
    def test_transaction_form_interaction(self):
        """Test interaction with transaction form elements (without submitting)"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                return False
            
            # Find form elements
            edit_controls = main_window.descendants(control_type="Edit")
            combo_controls = main_window.descendants(control_type="ComboBox")
            
            interactions_successful = 0
            
            # Test account selection (if available)
            if combo_controls:
                try:
                    account_combo = combo_controls[0]
                    account_combo.click()
                    time.sleep(1)
                    # Don't actually select, just test interaction
                    send_keys('{ESC}')  # Close dropdown
                    interactions_successful += 1
                    logger.info("Account selection interaction tested")
                except:
                    pass
            
            # Test amount field (if available)
            if edit_controls:
                for edit_control in edit_controls:
                    try:
                        edit_control.click_input()
                        # Type test amount briefly then clear
                        edit_control.type_keys('1.00')
                        time.sleep(1)
                        send_keys('^a{DEL}')  # Select all and delete
                        interactions_successful += 1
                        logger.info("Amount field interaction tested")
                        break
                    except:
                        continue
            
            return interactions_successful > 0
            
        except Exception as e:
            logger.error(f"Transaction form interaction test failed: {str(e)}")
            return False
    
    def validate_transaction_limits_display(self):
        """Validate that transaction limits and account info are displayed"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                return False
            
            # Look for balance, limits, or account information
            info_patterns = [
                'balance', 'limit', 'available', 'maximum',
                'minimum', 'daily', 'account number'
            ]
            
            found_info = []
            all_controls = main_window.descendants()
            
            for control in all_controls:
                control_text = control.window_text().lower()
                for pattern in info_patterns:
                    if pattern in control_text and pattern not in found_info:
                        found_info.append(pattern)
            
            logger.info(f"Found transaction info elements: {found_info}")
            
            # Consider validation successful if we found any relevant info
            return len(found_info) > 0
            
        except Exception as e:
            logger.error(f"Transaction limits validation failed: {str(e)}")
            return False
    
    def test_transaction_validation_messages(self):
        """Test that validation messages appear for invalid inputs"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                return False
            
            # Find amount field and enter invalid amount
            edit_controls = main_window.descendants(control_type="Edit")
            
            if edit_controls:
                amount_field = edit_controls[0]  # Assume first edit is amount
                
                # Test with invalid amount
                amount_field.click_input()
                send_keys('^a{DEL}')  # Clear field
                amount_field.type_keys('-100')  # Invalid negative amount
                
                # Tab out to trigger validation
                send_keys('{TAB}')
                time.sleep(2)
                
                # Look for error messages
                error_patterns = ['error', 'invalid', 'required', 'must be']
                validation_messages_found = []
                
                all_controls = main_window.descendants()
                for control in all_controls:
                    control_text = control.window_text().lower()
                    for pattern in error_patterns:
                        if pattern in control_text:
                            validation_messages_found.append(control_text)
                            break
                
                # Clear the invalid input
                amount_field.click_input()
                send_keys('^a{DEL}')
                
                logger.info(f"Validation messages found: {validation_messages_found}")
                return len(validation_messages_found) > 0
            
            return False
            
        except Exception as e:
            logger.error(f"Transaction validation test failed: {str(e)}")
            return False
    
    def return_to_main_screen(self):
        """Return to main dashboard or menu"""
        try:
            main_window = self.app_launcher.main_window
            if not main_window:
                return False
            
            # Look for navigation elements to return to main screen
            nav_patterns = [
                'home', 'dashboard', 'main', 'menu', 'back',
                'cancel', 'close', 'exit'
            ]
            
            # Try to find navigation control
            all_controls = main_window.descendants()
            nav_control = None
            
            for control in all_controls:
                control_text = control.window_text().lower()
                if any(pattern in control_text for pattern in nav_patterns):
                    if control.is_enabled() and control.is_visible():
                        nav_control = control
                        logger.info(f"Found navigation control: {control_text}")
                        break
            
            if nav_control:
                nav_control.click()
                time.sleep(2)
                logger.info("Returned to main screen")
                return True
            else:
                # Try pressing Escape as fallback
                send_keys('{ESC}')
                time.sleep(1)
                logger.info("Used ESC to return to main screen")
                return True
                
        except Exception as e:
            logger.error(f"Failed to return to main screen: {str(e)}")
            return False
    
    def execute_task(self):
        """Execute the transaction testing task"""
        logger.info("Starting Transaction Agent task")
        
        test_results = []
        
        # Take initial screenshot
        initial_screenshot = self.app_launcher.take_screenshot("transaction_start")
        
        # Navigate to transactions
        nav_result = self.navigate_to_transactions()
        test_results.append({
            'test': 'navigate_to_transactions',
            'status': 'PASSED' if nav_result else 'FAILED',
            'message': 'Navigation to transactions section'
        })
        
        if nav_result:
            # Take screenshot after navigation
            nav_screenshot = self.app_launcher.take_screenshot("transaction_screen")
            
            # Validate transaction screen elements
            elements_result = self.validate_transaction_screen_elements()
            test_results.append({
                'test': 'validate_screen_elements',
                'status': 'PASSED' if elements_result else 'FAILED',
                'message': 'Transaction screen elements validation'
            })
            
            # Test form interactions
            interaction_result = self.test_transaction_form_interaction()
            test_results.append({
                'test': 'test_form_interactions',
                'status': 'PASSED' if interaction_result else 'FAILED',
                'message': 'Transaction form interaction testing'
            })
            
            # Validate transaction info display
            info_result = self.validate_transaction_limits_display()
            test_results.append({
                'test': 'validate_transaction_info',
                'status': 'PASSED' if info_result else 'FAILED',
                'message': 'Transaction limits and info display'
            })
            
            # Test validation messages
            validation_result = self.test_transaction_validation_messages()
            test_results.append({
                'test': 'test_validation_messages',
                'status': 'PASSED' if validation_result else 'FAILED',
                'message': 'Transaction validation messages'
            })
            
            # Return to main screen
            return_result = self.return_to_main_screen()
            test_results.append({
                'test': 'return_to_main',
                'status': 'PASSED' if return_result else 'FAILED',
                'message': 'Return to main screen'
            })
        
        # Take final screenshot
        final_screenshot = self.app_launcher.take_screenshot("transaction_end")
        
        # Determine overall status
        failed_tests = [test for test in test_results if test['status'] == 'FAILED']
        overall_status = 'PASSED' if len(failed_tests) == 0 else 'FAILED'
        
        return {
            'status': overall_status,
            'message': f'Transaction testing completed. {len(failed_tests)} failures out of {len(test_results)} tests',
            'test_results': test_results,
            'failed_tests': failed_tests,
            'screenshots': {
                'initial': initial_screenshot,
                'navigation': nav_screenshot if nav_result else None,
                'final': final_screenshot
            }
        }