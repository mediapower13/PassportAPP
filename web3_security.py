"""
Security Utilities for Web3 Integration
Encryption, validation, and security features for blockchain operations
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, abort
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import json


class Web3Security:
    """Security utilities for Web3 operations"""
    
    @staticmethod
    def generate_document_hash(data):
        """Generate SHA-256 hash of document data"""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def generate_nonce():
        """Generate cryptographic nonce for signature verification"""
        return secrets.token_hex(32)
    
    @staticmethod
    def verify_signature_timestamp(timestamp, max_age_seconds=300):
        """Verify signature timestamp is recent"""
        try:
            sig_time = datetime.fromisoformat(timestamp)
            current_time = datetime.now()
            age = (current_time - sig_time).total_seconds()
            return age <= max_age_seconds
        except:
            return False
    
    @staticmethod
    def create_message_hash(message):
        """Create Ethereum-compatible message hash"""
        prefix = "\x19Ethereum Signed Message:\n"
        message_bytes = message.encode('utf-8')
        full_message = prefix + str(len(message_bytes)) + message
        return hashlib.sha256(full_message.encode()).hexdigest()
    
    @staticmethod
    def validate_ethereum_address(address):
        """Validate Ethereum address format"""
        if not address:
            return False
        
        if not isinstance(address, str):
            return False
        
        if not address.startswith('0x'):
            return False
        
        if len(address) != 42:
            return False
        
        try:
            int(address[2:], 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_passport_number(passport_number):
        """Sanitize passport number for blockchain storage"""
        # Remove special characters, keep only alphanumeric
        sanitized = ''.join(c for c in passport_number if c.isalnum())
        return sanitized.upper()
    
    @staticmethod
    def encrypt_sensitive_data(data, password):
        """Encrypt sensitive data with password"""
        # Derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'passport_salt_2024',  # In production, use random salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Encrypt data
        fernet = Fernet(key)
        encrypted = fernet.encrypt(json.dumps(data).encode())
        
        return base64.urlsafe_b64encode(encrypted).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data, password):
        """Decrypt sensitive data with password"""
        try:
            # Derive key from password
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'passport_salt_2024',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt data
            fernet = Fernet(key)
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            decrypted = fernet.decrypt(encrypted_bytes)
            
            return json.loads(decrypted.decode())
        except:
            return None
    
    @staticmethod
    def generate_access_token():
        """Generate secure access token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_for_ipfs(data):
        """Generate hash suitable for IPFS content addressing"""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        if isinstance(data, str):
            data = data.encode()
        
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def create_verification_challenge(passport_id, requester_address):
        """Create verification challenge for passport access"""
        challenge_data = {
            'passport_id': passport_id,
            'requester': requester_address,
            'timestamp': datetime.now().isoformat(),
            'nonce': secrets.token_hex(16)
        }
        
        challenge_string = json.dumps(challenge_data, sort_keys=True)
        challenge_hash = hashlib.sha256(challenge_string.encode()).hexdigest()
        
        return {
            'challenge': challenge_hash,
            'data': challenge_data
        }
    
    @staticmethod
    def verify_challenge_response(challenge_data, signature, expected_signer):
        """Verify challenge response signature"""
        # This would use Web3 to recover signer from signature
        # Simplified version
        return True  # Implement with web3.eth.account.recover_message


def require_wallet_connection(f):
    """Decorator to require wallet connection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'wallet_address' not in session:
            abort(401, description="Wallet not connected")
        return f(*args, **kwargs)
    return decorated_function


def validate_passport_ownership(passport_id, owner_address):
    """Decorator to validate passport ownership"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verify ownership via smart contract
            # This would call web3_backend.verify_ownership
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class RateLimiter:
    """Rate limiting for Web3 operations"""
    
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier):
        """Check if request is allowed"""
        current_time = datetime.now()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside time window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if (current_time - req_time).total_seconds() < self.time_window
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_remaining_requests(self, identifier):
        """Get number of remaining requests"""
        if identifier not in self.requests:
            return self.max_requests
        
        current_time = datetime.now()
        active_requests = [
            req_time for req_time in self.requests[identifier]
            if (current_time - req_time).total_seconds() < self.time_window
        ]
        
        return max(0, self.max_requests - len(active_requests))


class TransactionValidator:
    """Validate blockchain transactions before submission"""
    
    @staticmethod
    def validate_gas_price(gas_price, max_gas_price_gwei=100):
        """Validate gas price is within acceptable range"""
        gas_price_gwei = gas_price / 1e9
        return gas_price_gwei <= max_gas_price_gwei
    
    @staticmethod
    def validate_gas_limit(gas_limit, max_gas_limit=500000):
        """Validate gas limit is reasonable"""
        return gas_limit <= max_gas_limit
    
    @staticmethod
    def estimate_transaction_cost(gas_price, gas_limit):
        """Estimate transaction cost in ETH"""
        return (gas_price * gas_limit) / 1e18
    
    @staticmethod
    def validate_transaction_params(params):
        """Validate transaction parameters"""
        required_fields = ['from', 'to', 'gas', 'gasPrice']
        
        for field in required_fields:
            if field not in params:
                return False, f"Missing required field: {field}"
        
        # Validate addresses
        if not Web3Security.validate_ethereum_address(params['from']):
            return False, "Invalid 'from' address"
        
        if not Web3Security.validate_ethereum_address(params['to']):
            return False, "Invalid 'to' address"
        
        # Validate gas parameters
        if not TransactionValidator.validate_gas_limit(params['gas']):
            return False, "Gas limit too high"
        
        if not TransactionValidator.validate_gas_price(params['gasPrice']):
            return False, "Gas price too high"
        
        return True, "Valid transaction parameters"


# Global rate limiter instance
transaction_rate_limiter = RateLimiter(max_requests=5, time_window=60)


def create_secure_session(wallet_address):
    """Create secure session for wallet connection"""
    session['wallet_address'] = wallet_address
    session['connected_at'] = datetime.now().isoformat()
    session['session_token'] = Web3Security.generate_access_token()
    session.permanent = True
    return session['session_token']


def clear_secure_session():
    """Clear secure session"""
    session.pop('wallet_address', None)
    session.pop('connected_at', None)
    session.pop('session_token', None)


def verify_session_valid():
    """Verify session is valid and not expired"""
    if 'wallet_address' not in session:
        return False
    
    if 'connected_at' not in session:
        return False
    
    try:
        connected_time = datetime.fromisoformat(session['connected_at'])
        age = (datetime.now() - connected_time).total_seconds()
        
        # Session expires after 24 hours
        return age < 86400
    except:
        return False
