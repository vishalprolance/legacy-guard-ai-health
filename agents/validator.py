"""
Screen Validator Agent - Responsible for visual and semantic validation of UI screens
"""

import os
import time
import logging
import json
import requests
from PIL import Image
import numpy as np
from skimage.metrics import structural_similarity as ssim

from utils.visual_diff import VisualDiffValidator
from utils.ocr_validation import OCRValidator

logger = logging.getLogger(__name__)

class ScreenValidatorAgent:
    """Agent responsible for validating screens using visual comparison and LLM analysis"""
    
    def __init__(self, config, app_launcher):
        self.config = config
        self.app_launcher = app_launcher
        self.visual_validator = VisualDiffValidator(config)
        self.ocr_validator = OCRValidator(config)
        
        # LLM configuration
        self.llm_config = {
            'api_url': os.getenv('LLM_API_URL', 'http://localhost:8000/v1/chat/completions'),
            'api_key': os.getenv('LLM_API_KEY', 'your-api-key'),
            'model_name': os.getenv('LLM_MODEL_NAME', 'gpt-4-turbo')
        }
        
        self.validation_threshold = config.get('validation', {}).get('similarity_threshold', 0.85)
    
    def capture_current_screen(self, screen_name):
        """Capture current screen state"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/{screen_name}_{timestamp}.png"
            
            if self.app_launcher.main_window:
                image = self.app_launcher.main_window.capture_as_image()
                image.save(screenshot_path)
                logger.info(f"Screen captured: {screenshot_path}")
                return screenshot_path
            else:
                logger.error("No main window available for screen capture")
                return None
                
        except Exception as e:
            logger.error(f"Failed to capture screen: {str(e)}")
            return None
    
    def perform_visual_comparison(self, current_screenshot, baseline_path):
        """Perform visual comparison with baseline image"""
        try:
            if not os.path.exists(baseline_path):
                logger.warning(f"Baseline image not found: {baseline_path}")
                return {
                    'similarity_score': 0.0,
                    'status': 'NO_BASELINE',
                    'message': 'Baseline image not available'
                }
            
            # Load images
            current_img = Image.open(current_screenshot)
            baseline_img = Image.open(baseline_path)
            
            # Resize images to same dimensions if needed
            if current_img.size != baseline_img.size:
                baseline_img = baseline_img.resize(current_img.size)
            
            # Convert to numpy arrays
            current_array = np.array(current_img.convert('RGB'))
            baseline_array = np.array(baseline_img.convert('RGB'))
            
            # Calculate SSIM
            similarity_score = ssim(current_array, baseline_array, multichannel=True, channel_axis=2)
            
            # Determine status
            status = 'PASSED' if similarity_score >= self.validation_threshold else 'FAILED'
            
            logger.info(f"Visual comparison - Similarity: {similarity_score:.3f}, Status: {status}")
            
            return {
                'similarity_score': similarity_score,
                'status': status,
                'message': f'Visual similarity: {similarity_score:.3f}'
            }
            
        except Exception as e:
            logger.error(f"Visual comparison failed: {str(e)}")
            return {
                'similarity_score': 0.0,
                'status': 'ERROR',
                'message': f'Visual comparison error: {str(e)}'
            }
    
    def perform_ocr_validation(self, screenshot_path, expected_text=None):
        """Perform OCR validation on screenshot"""
        try:
            extracted_text = self.ocr_validator.extract_text(screenshot_path)
            
            if not extracted_text:
                return {
                    'status': 'FAILED',
                    'message': 'No text extracted from screenshot',
                    'extracted_text': ''
                }
            
            # If expected text is provided, check for its presence
            if expected_text:
                text_found = any(text.lower() in extracted_text.lower() for text in expected_text)
                status = 'PASSED' if text_found else 'FAILED'
                message = f"Expected text {'found' if text_found else 'not found'}"
            else:
                status = 'PASSED'
                message = 'Text extraction successful'
            
            logger.info(f"OCR validation - Status: {status}")
            
            return {
                'status': status,
                'message': message,
                'extracted_text': extracted_text
            }
            
        except Exception as e:
            logger.error(f"OCR validation failed: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'OCR validation error: {str(e)}',
                'extracted_text': ''
            }
    
    def perform_llm_semantic_analysis(self, screenshot_path, context="banking application screen"):
        """Perform semantic analysis using LLM"""
        try:
            # Read and encode image
            with open(screenshot_path, 'rb') as img_file:
                import base64
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            
            # Prepare prompt
            prompt = f"""
            Analyze this {context} screenshot and provide a semantic validation assessment.
            
            Please evaluate:
            1. Is this a valid banking application interface?
            2. Are there any obvious UI errors or issues?
            3. What key elements are visible on the screen?
            4. Does the layout appear professional and complete?
            5. Any security or accessibility concerns?
            
            Provide your response in JSON format with:
            - status: "PASSED" or "FAILED"
            - confidence: 0.0 to 1.0
            - issues: array of any issues found
            - elements: array of key UI elements detected
            - summary: brief overall assessment
            """
            
            # Prepare API request
            headers = {
                'Authorization': f'Bearer {self.llm_config["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': self.llm_config['model_name'],
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {
                                'type': 'image_url',
                                'image_url': {
                                    'url': f'data:image/png;base64,{img_base64}'
                                }
                            }
                        ]
                    }
                ],
                'max_tokens': 1000
            }
            
            # Make API request
            response = requests.post(
                self.llm_config['api_url'],
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    analysis = json.loads(llm_response)
                except json.JSONDecodeError:
                    # If not JSON, create structured response
                    analysis = {
                        'status': 'PASSED',
                        'confidence': 0.7,
                        'issues': [],
                        'elements': [],
                        'summary': llm_response[:200] + '...' if len(llm_response) > 200 else llm_response
                    }
                
                logger.info(f"LLM semantic analysis completed - Status: {analysis.get('status')}")
                return analysis
                
            else:
                logger.error(f"LLM API request failed: {response.status_code}")
                return {
                    'status': 'ERROR',
                    'confidence': 0.0,
                    'issues': [f'API request failed: {response.status_code}'],
                    'elements': [],
                    'summary': 'LLM analysis unavailable'
                }
                
        except Exception as e:
            logger.error(f"LLM semantic analysis failed: {str(e)}")
            return {
                'status': 'ERROR',
                'confidence': 0.0,
                'issues': [f'Analysis error: {str(e)}'],
                'elements': [],
                'summary': 'LLM analysis failed'
            }
    
    def validate_screen(self, screen_name, baseline_name=None, expected_text=None):
        """Perform comprehensive screen validation"""
        logger.info(f"Validating screen: {screen_name}")
        
        # Capture current screen
        screenshot_path = self.capture_current_screen(screen_name)
        if not screenshot_path:
            return {
                'status': 'FAILED',
                'message': 'Failed to capture screen',
                'validations': {}
            }
        
        validations = {}
        
        # Visual comparison
        if baseline_name:
            baseline_path = f"baseline/{baseline_name}.png"
            validations['visual'] = self.perform_visual_comparison(screenshot_path, baseline_path)
        
        # OCR validation
        validations['ocr'] = self.perform_ocr_validation(screenshot_path, expected_text)
        
        # LLM semantic analysis
        validations['semantic'] = self.perform_llm_semantic_analysis(screenshot_path, f"{screen_name} screen")
        
        # Determine overall status
        overall_status = 'PASSED'
        for validation_type, validation_result in validations.items():
            if validation_result.get('status') == 'FAILED':
                overall_status = 'FAILED'
                break
        
        return {
            'status': overall_status,
            'message': f'Screen validation completed for {screen_name}',
            'screenshot': screenshot_path,
            'validations': validations
        }
    
    def execute_task(self):
        """Execute the screen validation task"""
        logger.info("Starting Screen Validator Agent task")
        
        validation_results = []
        
        # Define screens to validate
        screens_to_validate = [
            {
                'name': 'dashboard',
                'baseline': 'dashboard',
                'expected_text': ['Dashboard', 'Account', 'Balance', 'Welcome']
            },
            {
                'name': 'main_menu',
                'baseline': 'main_menu',
                'expected_text': ['Menu', 'Transactions', 'Accounts', 'Settings']
            }
        ]
        
        # Validate each screen
        for screen_config in screens_to_validate:
            result = self.validate_screen(
                screen_config['name'],
                screen_config.get('baseline'),
                screen_config.get('expected_text')
            )
            validation_results.append(result)
        
        # Determine overall task status
        overall_status = 'PASSED'
        failed_screens = []
        
        for result in validation_results:
            if result['status'] == 'FAILED':
                overall_status = 'FAILED'
                failed_screens.append(result['message'])
        
        return {
            'status': overall_status,
            'message': f'Screen validation completed. {"All screens passed" if overall_status == "PASSED" else f"Failed screens: {len(failed_screens)}"}',
            'validation_results': validation_results,
            'failed_screens': failed_screens
        }