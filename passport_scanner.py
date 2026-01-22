"""
Passport Scanner Service
Handles OCR and MRZ extraction from passport images
"""

import pytesseract
from PIL import Image
import io
import base64
import re
from passporteye import read_mrz
import cv2
import numpy as np


class PassportScanner:
    """Handles passport scanning and MRZ extraction"""
    
    def __init__(self):
        # Configure tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_mrz_from_image(self, image_data):
        """Extract MRZ (Machine Readable Zone) from passport image"""
        try:
            # Decode base64 image
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            
            # Try using passporteye library first
            try:
                mrz = read_mrz(image_bytes)
                if mrz and mrz.mrz_type:
                    return self._parse_mrz_data(mrz)
            except:
                pass
            
            # Fallback to manual OCR
            return self._manual_ocr_extraction(image_bytes)
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error scanning passport: {str(e)}'
            }
    
    def _parse_mrz_data(self, mrz):
        """Parse MRZ data from passporteye result"""
        try:
            data = {
                'success': True,
                'passport_number': mrz.number if hasattr(mrz, 'number') else '',
                'full_name': f"{mrz.names} {mrz.surname}" if hasattr(mrz, 'names') else '',
                'nationality': mrz.nationality if hasattr(mrz, 'nationality') else '',
                'date_of_birth': mrz.date_of_birth if hasattr(mrz, 'date_of_birth') else '',
                'gender': mrz.sex if hasattr(mrz, 'sex') else '',
                'expiry_date': mrz.expiration_date if hasattr(mrz, 'expiration_date') else '',
                'issuing_country': mrz.country if hasattr(mrz, 'country') else '',
            }
            return data
        except Exception as e:
            return {
                'success': False,
                'message': f'Error parsing MRZ: {str(e)}'
            }
    
    def _manual_ocr_extraction(self, image_bytes):
        """Manual OCR extraction using pytesseract"""
        try:
            # Convert to PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Preprocess image
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Perform OCR
            text = pytesseract.image_to_string(binary)
            
            # Try to extract basic information
            data = {
                'success': True,
                'extracted_text': text,
                'message': 'Manual OCR completed. Please verify and fill in the details.',
                'passport_number': self._extract_passport_number(text),
                'full_name': '',
                'nationality': '',
                'date_of_birth': '',
                'gender': '',
                'expiry_date': '',
                'issuing_country': '',
            }
            
            return data
            
        except Exception as e:
            return {
                'success': False,
                'message': f'OCR extraction failed: {str(e)}'
            }
    
    def _extract_passport_number(self, text):
        """Try to extract passport number from OCR text"""
        # Common passport number patterns
        patterns = [
            r'[A-Z]{1,2}\d{6,9}',  # Most common format
            r'\d{8,9}',  # Numeric only
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return ''


# Global scanner instance
_scanner = None


def get_passport_scanner():
    """Get or create passport scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = PassportScanner()
    return _scanner
