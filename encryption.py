"""
Security utilities for encrypting and decrypting sensitive passport data
Uses AES-256 encryption with Fernet (symmetric encryption)
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os


class EncryptionService:
    """Handle encryption and decryption of sensitive data"""
    
    def __init__(self, secret_key=None):
        """
        Initialize encryption service with a secret key
        
        Args:
            secret_key: Master key for encryption (from environment variable)
        """
        if secret_key is None:
            secret_key = os.getenv('ENCRYPTION_KEY')
            
        if not secret_key:
            raise ValueError("Encryption key must be provided or set in ENCRYPTION_KEY environment variable")
        
        # Derive a key from the secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'passport_app_salt_2025',  # In production, use a random salt per user
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        """
        Encrypt sensitive data
        
        Args:
            data: String data to encrypt
            
        Returns:
            Encrypted data as string
        """
        if data is None:
            return None
        
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"Encryption error: {e}")
            return None
    
    def decrypt(self, encrypted_data):
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data: Encrypted string
            
        Returns:
            Decrypted data as string
        """
        if encrypted_data is None:
            return None
        
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"Decryption error: {e}")
            return None


def generate_encryption_key():
    """Generate a new encryption key for the application"""
    return Fernet.generate_key().decode()


# Singleton instance
_encryption_service = None

def get_encryption_service():
    """Get or create encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
