"""
Input validation utilities
Validate and sanitize user inputs
"""

import re
from datetime import datetime


class InputValidator:
    """Input validation class"""
    
    @staticmethod
    def validate_passport_number(passport_number):
        """Validate passport number format"""
        if not passport_number or not isinstance(passport_number, str):
            return False, "Passport number is required"
        
        # Remove whitespace
        passport_number = passport_number.strip()
        
        # Check length (typically 6-9 characters)
        if len(passport_number) < 6 or len(passport_number) > 12:
            return False, "Passport number must be 6-12 characters"
        
        # Check format (alphanumeric)
        if not re.match(r'^[A-Z0-9]+$', passport_number.upper()):
            return False, "Passport number must contain only letters and numbers"
        
        return True, passport_number.upper()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False, "Email is required"
        
        email = email.strip().lower()
        
        # Basic email regex
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        return True, email
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        # Check for uppercase
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digit
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        return True, password
    
    @staticmethod
    def validate_ethereum_address(address):
        """Validate Ethereum address"""
        if not address or not isinstance(address, str):
            return False, "Ethereum address is required"
        
        address = address.strip()
        
        # Check format
        if not address.startswith('0x'):
            return False, "Ethereum address must start with 0x"
        
        if len(address) != 42:
            return False, "Ethereum address must be 42 characters"
        
        # Check if hex
        try:
            int(address[2:], 16)
        except ValueError:
            return False, "Invalid Ethereum address format"
        
        return True, address
    
    @staticmethod
    def validate_date(date_string, format='%Y-%m-%d'):
        """Validate date string"""
        if not date_string:
            return False, "Date is required"
        
        try:
            date_obj = datetime.strptime(str(date_string), format)
            return True, date_obj
        except ValueError:
            return False, f"Invalid date format. Expected: {format}"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent path traversal"""
        if not filename:
            return False, "Filename is required"
        
        # Remove path separators
        filename = filename.replace('/', '').replace('\\', '')
        
        # Remove potentially dangerous characters
        filename = re.sub(r'[^\w\s.-]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        if not filename:
            return False, "Invalid filename"
        
        return True, filename
    
    @staticmethod
    def validate_country_code(code):
        """Validate country code (ISO 3166-1 alpha-2)"""
        if not code or not isinstance(code, str):
            return False, "Country code is required"
        
        code = code.strip().upper()
        
        if len(code) != 2:
            return False, "Country code must be 2 characters"
        
        if not re.match(r'^[A-Z]{2}$', code):
            return False, "Invalid country code format"
        
        return True, code
    
    @staticmethod
    def validate_phone_number(phone):
        """Validate phone number"""
        if not phone or not isinstance(phone, str):
            return False, "Phone number is required"
        
        # Remove common separators
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check if contains only digits and optional leading +
        if not re.match(r'^\+?\d{10,15}$', phone):
            return False, "Invalid phone number format"
        
        return True, phone
    
    @staticmethod
    def validate_ipfs_hash(ipfs_hash):
        """Validate IPFS hash format"""
        if not ipfs_hash or not isinstance(ipfs_hash, str):
            return False, "IPFS hash is required"
        
        ipfs_hash = ipfs_hash.strip()
        
        # Check if starts with Qm (IPFS v0) or b (IPFS v1)
        if not (ipfs_hash.startswith('Qm') or ipfs_hash.startswith('b')):
            return False, "Invalid IPFS hash format"
        
        # Check length
        if len(ipfs_hash) < 46:
            return False, "IPFS hash too short"
        
        return True, ipfs_hash
    
    @staticmethod
    def validate_transaction_hash(tx_hash):
        """Validate Ethereum transaction hash"""
        if not tx_hash or not isinstance(tx_hash, str):
            return False, "Transaction hash is required"
        
        tx_hash = tx_hash.strip()
        
        if not tx_hash.startswith('0x'):
            return False, "Transaction hash must start with 0x"
        
        if len(tx_hash) != 66:
            return False, "Transaction hash must be 66 characters"
        
        try:
            int(tx_hash[2:], 16)
        except ValueError:
            return False, "Invalid transaction hash format"
        
        return True, tx_hash
    
    @staticmethod
    def validate_positive_integer(value, min_value=1, max_value=None):
        """Validate positive integer"""
        try:
            int_value = int(value)
            
            if int_value < min_value:
                return False, f"Value must be at least {min_value}"
            
            if max_value and int_value > max_value:
                return False, f"Value must not exceed {max_value}"
            
            return True, int_value
        except (ValueError, TypeError):
            return False, "Value must be an integer"
    
    @staticmethod
    def validate_price(price, min_price=0.0, max_price=None):
        """Validate price value"""
        try:
            float_price = float(price)
            
            if float_price < min_price:
                return False, f"Price must be at least {min_price}"
            
            if max_price and float_price > max_price:
                return False, f"Price must not exceed {max_price}"
            
            return True, float_price
        except (ValueError, TypeError):
            return False, "Invalid price format"


def validate_form_data(data, required_fields):
    """Validate form data has required fields"""
    errors = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field} is required")
    
    if errors:
        return False, errors
    
    return True, None
