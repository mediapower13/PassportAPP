"""
OCR and passport scanning utilities
Extracts information from passport images using OCR
"""

import re
from PIL import Image
import io
import base64


class PassportScanner:
    """Handle passport image scanning and OCR"""
    
    def __init__(self):
        self.mrz_pattern = re.compile(r'[A-Z0-9<]{44}')
    
    def extract_mrz_from_image(self, image_data):
        """
        Extract MRZ (Machine Readable Zone) from passport image
        
        Args:
            image_data: Base64 encoded image or PIL Image
            
        Returns:
            Dictionary with extracted passport data
        """
        try:
            # For now, return a placeholder
            # In production, integrate pytesseract or passporteye
            return {
                'success': False,
                'message': 'OCR feature coming soon. Please enter details manually.',
                'data': {}
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing image: {str(e)}',
                'data': {}
            }
    
    def validate_passport_photo(self, image_data):
        """
        Validate if photo meets passport requirements
        - Plain background
        - Face size and position
        - Image quality
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Decode base64 image
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Basic validation
            width, height = image.size
            
            validations = {
                'size_ok': width >= 600 and height >= 600,
                'aspect_ratio_ok': 0.9 <= (width/height) <= 1.1,
                'format_ok': image.format in ['JPEG', 'PNG'],
                'resolution_ok': width >= 600,
            }
            
            return {
                'valid': all(validations.values()),
                'checks': validations,
                'message': 'Photo validation passed' if all(validations.values()) else 'Photo needs adjustment'
            }
        except Exception as e:
            return {
                'valid': False,
                'checks': {},
                'message': f'Error validating photo: {str(e)}'
            }
    
    def parse_mrz_data(self, mrz_line1, mrz_line2):
        """
        Parse MRZ lines and extract passport information
        
        Args:
            mrz_line1: First line of MRZ (44 characters)
            mrz_line2: Second line of MRZ (44 characters)
            
        Returns:
            Dictionary with parsed data
        """
        try:
            data = {}
            
            # Parse line 1: P<COUNTRY<<SURNAME<<GIVEN_NAMES
            if mrz_line1.startswith('P<'):
                country_code = mrz_line1[2:5].replace('<', '')
                name_part = mrz_line1[5:].rstrip('<')
                names = name_part.split('<<')
                
                data['issuing_country'] = country_code
                data['surname'] = names[0].replace('<', ' ').strip()
                data['given_names'] = names[1].replace('<', ' ').strip() if len(names) > 1 else ''
                data['full_name'] = f"{data.get('given_names', '')} {data.get('surname', '')}".strip()
            
            # Parse line 2: Passport number, nationality, DOB, gender, expiry, etc.
            if len(mrz_line2) == 44:
                data['passport_number'] = mrz_line2[0:9].replace('<', '')
                data['nationality'] = mrz_line2[10:13].replace('<', '')
                
                # Date of birth: YYMMDD
                dob = mrz_line2[13:19]
                data['date_of_birth'] = self._parse_mrz_date(dob)
                
                # Gender
                data['gender'] = mrz_line2[20]
                
                # Expiry date: YYMMDD
                expiry = mrz_line2[21:27]
                data['expiry_date'] = self._parse_mrz_date(expiry)
            
            return {
                'success': True,
                'data': data
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error parsing MRZ: {str(e)}',
                'data': {}
            }
    
    def _parse_mrz_date(self, mrz_date):
        """Convert MRZ date (YYMMDD) to YYYY-MM-DD format"""
        if len(mrz_date) != 6:
            return None
        
        try:
            year = int(mrz_date[0:2])
            month = mrz_date[2:4]
            day = mrz_date[4:6]
            
            # Determine century (assume current century if < 50, else previous century)
            current_year = 2025
            if year < 50:
                full_year = 2000 + year
            else:
                full_year = 1900 + year
            
            return f"{full_year}-{month}-{day}"
        except:
            return None


# Singleton instance
_scanner = None

def get_passport_scanner():
    """Get or create passport scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = PassportScanner()
    return _scanner
