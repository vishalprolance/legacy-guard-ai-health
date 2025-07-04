"""
OCR Validation Utility
Handles text extraction and validation using Tesseract OCR
"""

import os
import re
import logging
import pytesseract
from PIL import Image
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class OCRValidator:
    """Utility class for OCR-based text extraction and validation"""
    
    def __init__(self, config):
        self.config = config
        self.confidence_threshold = config.get('validation', {}).get('ocr_confidence_threshold', 60)
        
        # Configure Tesseract path if needed (adjust for your system)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR results"""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to load image: {image_path}")
                return None
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply morphological operations to clean up the image
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return None
    
    def extract_text(self, image_path, preprocess=True):
        """Extract text from image using OCR"""
        try:
            if preprocess:
                # Use preprocessed image
                processed_img = self.preprocess_image(image_path)
                if processed_img is None:
                    return ""
                
                # Convert numpy array back to PIL Image for Tesseract
                pil_img = Image.fromarray(processed_img)
            else:
                # Use original image
                pil_img = Image.open(image_path)
            
            # Configure OCR
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(pil_img, config=custom_config)
            
            # Clean up extracted text
            cleaned_text = self.clean_extracted_text(text)
            
            logger.info(f"OCR extracted {len(cleaned_text)} characters of text")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {str(e)}")
            return ""
    
    def extract_text_with_confidence(self, image_path, preprocess=True):
        """Extract text with confidence scores"""
        try:
            if preprocess:
                processed_img = self.preprocess_image(image_path)
                if processed_img is None:
                    return {"text": "", "confidence": 0, "words": []}
                
                pil_img = Image.fromarray(processed_img)
            else:
                pil_img = Image.open(image_path)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
            
            # Extract words with confidence above threshold
            valid_words = []
            all_text = []
            total_confidence = 0
            valid_count = 0
            
            for i in range(len(ocr_data['text'])):
                word = ocr_data['text'][i].strip()
                confidence = ocr_data['conf'][i]
                
                if word and confidence > 0:  # Valid word found
                    all_text.append(word)
                    total_confidence += confidence
                    valid_count += 1
                    
                    if confidence >= self.confidence_threshold:
                        valid_words.append({
                            'word': word,
                            'confidence': confidence,
                            'bbox': {
                                'x': ocr_data['left'][i],
                                'y': ocr_data['top'][i],
                                'width': ocr_data['width'][i],
                                'height': ocr_data['height'][i]
                            }
                        })
            
            # Calculate average confidence
            avg_confidence = total_confidence / valid_count if valid_count > 0 else 0
            
            # Combine all text
            full_text = ' '.join(all_text)
            cleaned_text = self.clean_extracted_text(full_text)
            
            result = {
                'text': cleaned_text,
                'confidence': avg_confidence,
                'words': valid_words,
                'total_words': len(all_text),
                'high_confidence_words': len(valid_words)
            }
            
            logger.info(f"OCR with confidence: {len(valid_words)} high-confidence words, avg confidence: {avg_confidence:.1f}")
            return result
            
        except Exception as e:
            logger.error(f"OCR with confidence failed: {str(e)}")
            return {"text": "", "confidence": 0, "words": []}
    
    def clean_extracted_text(self, text):
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove special characters but keep alphanumeric and common punctuation
        cleaned = re.sub(r'[^\w\s\.\,\-\$\(\)\/]', '', cleaned)
        
        # Normalize currency symbols
        cleaned = re.sub(r'\$(\d)', r'$\1', cleaned)
        
        return cleaned.strip()
    
    def validate_expected_text(self, image_path, expected_texts, case_sensitive=False):
        """Validate that expected text elements are present in the image"""
        try:
            # Extract text with confidence
            ocr_result = self.extract_text_with_confidence(image_path)
            extracted_text = ocr_result['text']
            
            if not extracted_text:
                return {
                    'status': 'FAILED',
                    'message': 'No text extracted from image',
                    'found_texts': [],
                    'missing_texts': expected_texts,
                    'extracted_text': '',
                    'confidence': 0
                }
            
            # Prepare text for comparison
            search_text = extracted_text if case_sensitive else extracted_text.lower()
            
            found_texts = []
            missing_texts = []
            
            for expected in expected_texts:
                search_expected = expected if case_sensitive else expected.lower()
                
                if search_expected in search_text:
                    found_texts.append(expected)
                else:
                    missing_texts.append(expected)
            
            # Determine validation status
            if len(missing_texts) == 0:
                status = 'PASSED'
                message = f"All {len(expected_texts)} expected texts found"
            else:
                status = 'FAILED'
                message = f"{len(missing_texts)} texts missing: {missing_texts[:3]}"
            
            return {
                'status': status,
                'message': message,
                'found_texts': found_texts,
                'missing_texts': missing_texts,
                'extracted_text': extracted_text,
                'confidence': ocr_result['confidence']
            }
            
        except Exception as e:
            logger.error(f"Text validation failed: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Validation error: {str(e)}',
                'found_texts': [],
                'missing_texts': expected_texts,
                'extracted_text': '',
                'confidence': 0
            }
    
    def extract_specific_patterns(self, image_path, patterns):
        """Extract specific patterns (like account numbers, amounts) from image"""
        try:
            extracted_text = self.extract_text(image_path)
            
            if not extracted_text:
                return {'status': 'FAILED', 'patterns': {}}
            
            pattern_results = {}
            
            for pattern_name, regex_pattern in patterns.items():
                matches = re.findall(regex_pattern, extracted_text, re.IGNORECASE)
                pattern_results[pattern_name] = {
                    'matches': matches,
                    'count': len(matches),
                    'found': len(matches) > 0
                }
            
            # Determine overall status
            total_patterns = len(patterns)
            found_patterns = sum(1 for result in pattern_results.values() if result['found'])
            
            status = 'PASSED' if found_patterns == total_patterns else 'PARTIAL' if found_patterns > 0 else 'FAILED'
            
            return {
                'status': status,
                'message': f"Found {found_patterns}/{total_patterns} expected patterns",
                'patterns': pattern_results,
                'extracted_text': extracted_text
            }
            
        except Exception as e:
            logger.error(f"Pattern extraction failed: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Pattern extraction error: {str(e)}',
                'patterns': {}
            }
    
    def validate_ui_labels(self, image_path, required_labels):
        """Validate that required UI labels are present and readable"""
        try:
            # Extract text with confidence scores
            ocr_result = self.extract_text_with_confidence(image_path)
            
            if ocr_result['confidence'] < self.confidence_threshold:
                return {
                    'status': 'FAILED',
                    'message': f"OCR confidence too low: {ocr_result['confidence']:.1f}",
                    'labels_found': [],
                    'labels_missing': required_labels
                }
            
            # Check for required labels
            extracted_text = ocr_result['text'].lower()
            labels_found = []
            labels_missing = []
            
            for label in required_labels:
                if label.lower() in extracted_text:
                    labels_found.append(label)
                else:
                    labels_missing.append(label)
            
            # Determine status
            if len(labels_missing) == 0:
                status = 'PASSED'
                message = f"All {len(required_labels)} UI labels found"
            else:
                status = 'FAILED'
                message = f"{len(labels_missing)} labels missing"
            
            return {
                'status': status,
                'message': message,
                'labels_found': labels_found,
                'labels_missing': labels_missing,
                'ocr_confidence': ocr_result['confidence'],
                'extracted_text': ocr_result['text']
            }
            
        except Exception as e:
            logger.error(f"UI label validation failed: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Label validation error: {str(e)}',
                'labels_found': [],
                'labels_missing': required_labels
            }