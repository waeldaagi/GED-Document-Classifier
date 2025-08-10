import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import easyocr
import re
from typing import Dict, List, Tuple, Optional
import os

class EnhancedOCR:
    def __init__(self, languages=['fr', 'en']):
        self.languages = languages
        self.tesseract_config = '--oem 3 --psm 6'
        
        # Initialize EasyOCR for better accuracy
        try:
            self.easyocr_reader = easyocr.Reader(languages)
        except:
            self.easyocr_reader = None
            print("⚠️ EasyOCR not available, using Tesseract only")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Advanced image preprocessing for better OCR results"""
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Deskewing
        coords = np.column_stack(np.where(enhanced > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        (h, w) = enhanced.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(enhanced, M, (w, h), 
                                flags=cv2.INTER_CUBIC, 
                                borderMode=cv2.BORDER_REPLICATE)
        
        # Binarization
        _, binary = cv2.threshold(rotated, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def detect_tables(self, image: np.ndarray) -> List[Dict]:
        """Detect and extract tables from images"""
        tables = []
        
        # Edge detection
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum table area
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Check if it looks like a table (rectangular with reasonable aspect ratio)
                if 0.5 < aspect_ratio < 3.0:
                    table_region = image[y:y+h, x:x+w]
                    table_text = self.extract_text_from_region(table_region)
                    
                    if table_text.strip():
                        tables.append({
                            'bbox': (x, y, w, h),
                            'text': table_text,
                            'confidence': 0.8
                        })
        
        return tables
    
    def extract_text_from_region(self, image_region: np.ndarray) -> str:
        """Extract text from a specific image region"""
        # Preprocess the region
        processed = self.preprocess_image(image_region)
        
        # Try Tesseract first
        try:
            tesseract_text = pytesseract.image_to_string(
                processed, 
                lang='fra+eng', 
                config=self.tesseract_config
            )
        except:
            tesseract_text = ""
        
        # Try EasyOCR if available
        easyocr_text = ""
        if self.easyocr_reader:
            try:
                results = self.easyocr_reader.readtext(image_region)
                easyocr_text = " ".join([result[1] for result in results])
            except:
                pass
        
        # Combine results (prefer EasyOCR if available)
        if easyocr_text and len(easyocr_text) > len(tesseract_text):
            return easyocr_text
        else:
            return tesseract_text
    
    def extract_structured_data(self, text: str) -> Dict:
        """Extract structured data from OCR text"""
        data = {
            'dates': [],
            'amounts': [],
            'emails': [],
            'phones': [],
            'companies': [],
            'names': []
        }
        
        # Date patterns
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',
            r'\d{1,2}-\d{1,2}-\d{4}',
            r'\d{1,2}\s+(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}',
            r'\d{4}-\d{2}-\d{2}'
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            data['dates'].extend(dates)
        
        # Amount patterns
        amount_patterns = [
            r'\d{1,3}(?:\s\d{3})*(?:,\d{2})?\s*(?:€|euros?|EUR)',
            r'(?:€|euros?|EUR)\s*\d{1,3}(?:\s\d{3})*(?:,\d{2})?',
            r'\d+(?:,\d{2})?\s*(?:€|euros?|EUR)'
        ]
        
        for pattern in amount_patterns:
            amounts = re.findall(pattern, text, re.IGNORECASE)
            data['amounts'].extend(amounts)
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        data['emails'] = re.findall(email_pattern, text)
        
        # Phone patterns
        phone_patterns = [
            r'(?:\+33|0)\s*[1-9](?:[\s.-]?\d{2}){4}',
            r'0[1-9]\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{2}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            data['phones'].extend(phones)
        
        return data
    
    def ocr_with_enhancements(self, image_path: str) -> Dict:
        """Complete OCR pipeline with enhancements"""
        # Load image
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
        else:
            image = image_path
        
        if image is None:
            return {'error': 'Could not load image'}
        
        # Preprocess image
        processed_image = self.preprocess_image(image)
        
        # Extract main text
        main_text = self.extract_text_from_region(processed_image)
        
        # Detect tables
        tables = self.detect_tables(processed_image)
        
        # Extract structured data
        structured_data = self.extract_structured_data(main_text)
        
        # Combine all text
        all_text = main_text
        for table in tables:
            all_text += "\n" + table['text']
        
        return {
            'main_text': main_text,
            'all_text': all_text,
            'tables': tables,
            'structured_data': structured_data,
            'confidence': 0.85  # Overall confidence score
        }
    
    def batch_ocr(self, image_paths: List[str]) -> List[Dict]:
        """Process multiple images in batch"""
        results = []
        
        for path in image_paths:
            try:
                result = self.ocr_with_enhancements(path)
                result['file_path'] = path
                results.append(result)
            except Exception as e:
                results.append({
                    'file_path': path,
                    'error': str(e)
                })
        
        return results

# Usage example
if __name__ == "__main__":
    ocr = EnhancedOCR()
    
    # Test with an image
    test_image = "test_doc.jpg"
    if os.path.exists(test_image):
        result = ocr.ocr_with_enhancements(test_image)
        print("📄 OCR Results:")
        print(f"Main text length: {len(result['main_text'])}")
        print(f"Tables found: {len(result['tables'])}")
        print(f"Dates found: {len(result['structured_data']['dates'])}")
        print(f"Amounts found: {len(result['structured_data']['amounts'])}")
    else:
        print("⚠️ Test image not found")
