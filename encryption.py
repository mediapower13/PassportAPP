"""
Encryption Service for PassportApp
Handles secure encryption/decryption of sensitive data
"""

from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import base64

load_dotenv()


class EncryptionService:
    """Handles encryption and decryption of sensitive passport data"""
    
    def __init__(self, key=None):
        """Initialize encryption service with a key"""
        if key:
            self.key = key
        else:
            # Get key from environment or generate new one
            key_str = os.getenv('ENCRYPTION_KEY')
            if key_str:
                self.key = key_str.encode()
            else:
                # Generate new key (save this to .env in production!)
                self.key = Fernet.generate_key()
                print(f"⚠️  Generated new encryption key. Add to .env: ENCRYPTION_KEY={self.key.decode()}")
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data):
        """Encrypt string data"""
        if not data:
            return None
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted = self.cipher.encrypt(data)
        return encrypted.decode('utf-8')
    
    def decrypt(self, encrypted_data):
        """Decrypt encrypted data"""
        if not encrypted_data:
            return None
        
        if isinstance(encrypted_data, str):
            encrypted_data = encrypted_data.encode('utf-8')
        
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    
    def encrypt_file(self, file_data):
        """Encrypt file binary data"""
        if not file_data:
            return None
        
        encrypted = self.cipher.encrypt(file_data)
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_file(self, encrypted_data):
        """Decrypt file binary data"""
        if not encrypted_data:
            return None
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted


# Global encryption service instance
_encryption_service = None


def get_encryption_service():
    """Get or create encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def init_encryption(key=None):
    """Initialize encryption service with optional key"""
    global _encryption_service
    _encryption_service = EncryptionService(key)
    return _encryption_service
