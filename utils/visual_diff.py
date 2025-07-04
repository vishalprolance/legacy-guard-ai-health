"""
Visual Difference Validation Utility
Handles screenshot comparison and visual validation using SSIM and other metrics
"""

import os
import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import logging

logger = logging.getLogger(__name__)

class VisualDiffValidator:
    """Utility class for visual comparison and validation"""
    
    def __init__(self, config):
        self.config = config
        self.similarity_threshold = config.get('validation', {}).get('similarity_threshold', 0.85)
        self.diff_output_dir = 'reports/visual_diffs'
        os.makedirs(self.diff_output_dir, exist_ok=True)
    
    def calculate_ssim(self, image1_path, image2_path):
        """Calculate Structural Similarity Index (SSIM) between two images"""
        try:
            # Load images
            img1 = Image.open(image1_path).convert('RGB')
            img2 = Image.open(image2_path).convert('RGB')
            
            # Resize to same dimensions if different
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            # Convert to numpy arrays
            img1_array = np.array(img1)
            img2_array = np.array(img2)
            
            # Calculate SSIM
            similarity_score = ssim(img1_array, img2_array, multichannel=True, channel_axis=2)
            
            logger.info(f"SSIM calculated: {similarity_score:.4f}")
            return similarity_score
            
        except Exception as e:
            logger.error(f"Failed to calculate SSIM: {str(e)}")
            return 0.0
    
    def calculate_histogram_similarity(self, image1_path, image2_path):
        """Calculate histogram-based similarity between two images"""
        try:
            # Load images using OpenCV
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                logger.error("Failed to load images for histogram comparison")
                return 0.0
            
            # Resize to same dimensions if different
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Calculate histograms
            hist1 = cv2.calcHist([img1], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([img2], [0, 1, 2], None, [50, 50, 50], [0, 256, 0, 256, 0, 256])
            
            # Compare histograms using correlation
            similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            logger.info(f"Histogram similarity calculated: {similarity:.4f}")
            return similarity
            
        except Exception as e:
            logger.error(f"Failed to calculate histogram similarity: {str(e)}")
            return 0.0
    
    def generate_difference_image(self, image1_path, image2_path, output_path=None):
        """Generate a visual difference image highlighting changes"""
        try:
            # Load images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                logger.error("Failed to load images for difference generation")
                return None
            
            # Resize to same dimensions if different
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Calculate absolute difference
            diff = cv2.absdiff(img1, img2)
            
            # Convert to grayscale for threshold
            gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to highlight significant differences
            _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
            
            # Create colored difference image
            diff_colored = diff.copy()
            diff_colored[thresh > 0] = [0, 0, 255]  # Highlight differences in red
            
            # Blend with original image
            blended = cv2.addWeighted(img1, 0.7, diff_colored, 0.3, 0)
            
            # Save difference image
            if not output_path:
                timestamp = int(time.time())
                output_path = os.path.join(self.diff_output_dir, f"diff_{timestamp}.png")
            
            cv2.imwrite(output_path, blended)
            logger.info(f"Difference image generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate difference image: {str(e)}")
            return None
    
    def validate_visual_elements(self, screenshot_path, expected_elements=None):
        """Validate presence of specific visual elements using template matching"""
        try:
            if not expected_elements:
                return {'status': 'SKIPPED', 'message': 'No expected elements provided'}
            
            # Load screenshot
            screenshot = cv2.imread(screenshot_path)
            if screenshot is None:
                return {'status': 'ERROR', 'message': 'Failed to load screenshot'}
            
            found_elements = []
            missing_elements = []
            
            for element in expected_elements:
                element_path = f"baseline/elements/{element}.png"
                
                if not os.path.exists(element_path):
                    missing_elements.append(f"Template not found: {element}")
                    continue
                
                # Load template
                template = cv2.imread(element_path)
                if template is None:
                    missing_elements.append(f"Failed to load template: {element}")
                    continue
                
                # Perform template matching
                result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                
                # Consider element found if match confidence > 0.8
                if max_val > 0.8:
                    found_elements.append({
                        'element': element,
                        'confidence': max_val,
                        'location': max_loc
                    })
                else:
                    missing_elements.append(f"Element not found: {element} (confidence: {max_val:.3f})")
            
            # Determine validation status
            if len(missing_elements) == 0:
                status = 'PASSED'
                message = f"All {len(found_elements)} expected elements found"
            else:
                status = 'FAILED' 
                message = f"{len(missing_elements)} elements missing: {missing_elements[:3]}"
            
            return {
                'status': status,
                'message': message,
                'found_elements': found_elements,
                'missing_elements': missing_elements
            }
            
        except Exception as e:
            logger.error(f"Visual element validation failed: {str(e)}")
            return {'status': 'ERROR', 'message': f'Validation error: {str(e)}'}
    
    def compare_images(self, current_image_path, baseline_image_path, generate_diff=True):
        """Comprehensive image comparison with multiple metrics"""
        try:
            if not os.path.exists(baseline_image_path):
                return {
                    'status': 'NO_BASELINE',
                    'message': 'Baseline image not found',
                    'similarity_scores': {}
                }
            
            # Calculate different similarity metrics
            ssim_score = self.calculate_ssim(current_image_path, baseline_image_path)
            hist_score = self.calculate_histogram_similarity(current_image_path, baseline_image_path)
            
            # Generate difference image if requested
            diff_image_path = None
            if generate_diff:
                diff_image_path = self.generate_difference_image(
                    baseline_image_path, 
                    current_image_path
                )
            
            # Determine overall status based on SSIM (primary metric)
            status = 'PASSED' if ssim_score >= self.similarity_threshold else 'FAILED'
            
            # Create detailed result
            result = {
                'status': status,
                'message': f'Visual comparison completed - SSIM: {ssim_score:.3f}',
                'similarity_scores': {
                    'ssim': ssim_score,
                    'histogram': hist_score,
                    'threshold': self.similarity_threshold
                },
                'diff_image': diff_image_path,
                'baseline_image': baseline_image_path,
                'current_image': current_image_path
            }
            
            logger.info(f"Image comparison result: {status} (SSIM: {ssim_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Image comparison failed: {str(e)}")
            return {
                'status': 'ERROR',
                'message': f'Comparison error: {str(e)}',
                'similarity_scores': {}
            }
    
    def create_baseline_image(self, source_image_path, baseline_name):
        """Create a baseline image for future comparisons"""
        try:
            baseline_dir = 'baseline'
            os.makedirs(baseline_dir, exist_ok=True)
            
            baseline_path = os.path.join(baseline_dir, f"{baseline_name}.png")
            
            # Copy source image to baseline location
            img = Image.open(source_image_path)
            img.save(baseline_path)
            
            logger.info(f"Baseline image created: {baseline_path}")
            return baseline_path
            
        except Exception as e:
            logger.error(f"Failed to create baseline image: {str(e)}")
            return None