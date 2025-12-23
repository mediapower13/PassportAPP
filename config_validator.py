"""
Configuration validator for PassportApp
Validate environment variables and configuration settings
"""

import os
import re
from datetime import datetime


class ConfigValidator:
    """Validate configuration settings"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.validated = False
    
    def validate_all(self):
        """Run all validation checks"""
        self.errors.clear()
        self.warnings.clear()
        
        self.validate_flask_config()
        self.validate_database_config()
        self.validate_web3_config()
        self.validate_ipfs_config()
        self.validate_security_config()
        self.validate_email_config()
        
        self.validated = True
        
        return len(self.errors) == 0
    
    def validate_flask_config(self):
        """Validate Flask configuration"""
        # Secret key
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            self.errors.append('SECRET_KEY environment variable is required')
        elif len(secret_key) < 32:
            self.warnings.append('SECRET_KEY should be at least 32 characters long')
        
        # Flask environment
        flask_env = os.environ.get('FLASK_ENV', 'production')
        if flask_env not in ['development', 'production', 'testing', 'staging']:
            self.warnings.append(f'Unknown FLASK_ENV: {flask_env}')
        
        # Debug mode
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        if debug and flask_env == 'production':
            self.errors.append('DEBUG mode should not be enabled in production')
    
    def validate_database_config(self):
        """Validate database configuration"""
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            self.warnings.append('DATABASE_URL not set, using default SQLite')
            return
        
        # Check database type
        if database_url.startswith('sqlite'):
            self.warnings.append('SQLite is not recommended for production')
        elif database_url.startswith('postgresql'):
            # Validate PostgreSQL connection string
            if not self._validate_postgres_url(database_url):
                self.errors.append('Invalid PostgreSQL connection string')
        elif database_url.startswith('mysql'):
            # Validate MySQL connection string
            if not self._validate_mysql_url(database_url):
                self.errors.append('Invalid MySQL connection string')
    
    def validate_web3_config(self):
        """Validate Web3/blockchain configuration"""
        provider_uri = os.environ.get('WEB3_PROVIDER_URI')
        
        if not provider_uri:
            self.errors.append('WEB3_PROVIDER_URI is required')
            return
        
        # Validate provider URI format
        if not (provider_uri.startswith('http://') or 
                provider_uri.startswith('https://') or 
                provider_uri.startswith('ws://') or 
                provider_uri.startswith('wss://')):
            self.errors.append('WEB3_PROVIDER_URI must be a valid URL')
        
        # Check for localhost in production
        flask_env = os.environ.get('FLASK_ENV', 'production')
        if flask_env == 'production' and 'localhost' in provider_uri:
            self.warnings.append('Using localhost Web3 provider in production')
        
        # Contract addresses
        contract_address = os.environ.get('CONTRACT_ADDRESS')
        if not contract_address:
            self.warnings.append('CONTRACT_ADDRESS not set')
        elif not self._validate_eth_address(contract_address):
            self.errors.append('Invalid CONTRACT_ADDRESS format')
        
        nft_contract = os.environ.get('NFT_CONTRACT_ADDRESS')
        if nft_contract and not self._validate_eth_address(nft_contract):
            self.errors.append('Invalid NFT_CONTRACT_ADDRESS format')
        
        marketplace_contract = os.environ.get('MARKETPLACE_CONTRACT_ADDRESS')
        if marketplace_contract and not self._validate_eth_address(marketplace_contract):
            self.errors.append('Invalid MARKETPLACE_CONTRACT_ADDRESS format')
    
    def validate_ipfs_config(self):
        """Validate IPFS configuration"""
        ipfs_api_url = os.environ.get('IPFS_API_URL')
        ipfs_api_key = os.environ.get('IPFS_API_KEY')
        ipfs_secret = os.environ.get('IPFS_SECRET_KEY')
        
        if not ipfs_api_url:
            self.warnings.append('IPFS_API_URL not set')
        
        if not ipfs_api_key:
            self.warnings.append('IPFS_API_KEY not set, IPFS uploads may fail')
        
        if not ipfs_secret:
            self.warnings.append('IPFS_SECRET_KEY not set')
    
    def validate_security_config(self):
        """Validate security configuration"""
        encryption_key = os.environ.get('ENCRYPTION_KEY')
        
        if not encryption_key:
            self.errors.append('ENCRYPTION_KEY is required for data encryption')
        elif len(encryption_key) != 44:  # Fernet key length
            self.errors.append('ENCRYPTION_KEY must be a valid Fernet key (44 characters)')
        
        # CORS settings
        cors_origins = os.environ.get('CORS_ORIGINS', '*')
        flask_env = os.environ.get('FLASK_ENV', 'production')
        
        if cors_origins == '*' and flask_env == 'production':
            self.warnings.append('CORS is set to allow all origins in production')
        
        # Rate limiting
        rate_limit_enabled = os.environ.get('RATELIMIT_ENABLED', 'True').lower() == 'true'
        if not rate_limit_enabled and flask_env == 'production':
            self.warnings.append('Rate limiting is disabled in production')
    
    def validate_email_config(self):
        """Validate email configuration"""
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not smtp_server:
            self.warnings.append('SMTP_SERVER not configured, email notifications disabled')
        
        if smtp_server and not smtp_username:
            self.warnings.append('SMTP_USERNAME not set')
        
        if smtp_server and not smtp_password:
            self.warnings.append('SMTP_PASSWORD not set')
    
    def _validate_postgres_url(self, url):
        """Validate PostgreSQL connection string"""
        pattern = r'postgresql:\/\/[\w-]+:[\w-]+@[\w\.-]+:\d+\/[\w-]+'
        return bool(re.match(pattern, url))
    
    def _validate_mysql_url(self, url):
        """Validate MySQL connection string"""
        pattern = r'mysql:\/\/[\w-]+:[\w-]+@[\w\.-]+:\d+\/[\w-]+'
        return bool(re.match(pattern, url))
    
    def _validate_eth_address(self, address):
        """Validate Ethereum address format"""
        if not address.startswith('0x'):
            return False
        if len(address) != 42:
            return False
        try:
            int(address, 16)
            return True
        except ValueError:
            return False
    
    def get_report(self):
        """Get validation report"""
        if not self.validated:
            self.validate_all()
        
        return {
            'valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def print_report(self):
        """Print validation report"""
        report = self.get_report()
        
        print("\n" + "=" * 50)
        print("Configuration Validation Report")
        print("=" * 50)
        
        if report['valid']:
            print("✓ Configuration is valid")
        else:
            print("✗ Configuration has errors")
        
        if report['errors']:
            print(f"\n❌ Errors ({len(report['errors'])}):")
            for error in report['errors']:
                print(f"  - {error}")
        
        if report['warnings']:
            print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
            for warning in report['warnings']:
                print(f"  - {warning}")
        
        if not report['errors'] and not report['warnings']:
            print("\n✓ No issues found")
        
        print("=" * 50 + "\n")


# Global validator
config_validator = ConfigValidator()


def validate_config():
    """Validate configuration and return report"""
    return config_validator.get_report()


def require_valid_config(func):
    """Decorator to ensure configuration is valid before running"""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not config_validator.validate_all():
            raise RuntimeError(
                f"Invalid configuration: {', '.join(config_validator.errors)}"
            )
        return func(*args, **kwargs)
    
    return wrapper


# Environment variable checklist
REQUIRED_ENV_VARS = {
    'production': [
        'SECRET_KEY',
        'DATABASE_URL',
        'WEB3_PROVIDER_URI',
        'ENCRYPTION_KEY'
    ],
    'development': [
        'SECRET_KEY'
    ],
    'testing': [
        'SECRET_KEY'
    ]
}


OPTIONAL_ENV_VARS = [
    'FLASK_DEBUG',
    'CONTRACT_ADDRESS',
    'NFT_CONTRACT_ADDRESS',
    'MARKETPLACE_CONTRACT_ADDRESS',
    'IPFS_API_URL',
    'IPFS_API_KEY',
    'IPFS_SECRET_KEY',
    'SMTP_SERVER',
    'SMTP_PORT',
    'SMTP_USERNAME',
    'SMTP_PASSWORD',
    'FROM_EMAIL',
    'REDIS_URL',
    'CORS_ORIGINS',
    'RATELIMIT_ENABLED',
    'LOG_LEVEL'
]


def check_env_vars(env='production'):
    """Check which environment variables are set"""
    required = REQUIRED_ENV_VARS.get(env, [])
    
    report = {
        'environment': env,
        'required': {},
        'optional': {},
        'missing_required': [],
        'set_optional': []
    }
    
    # Check required
    for var in required:
        value = os.environ.get(var)
        report['required'][var] = bool(value)
        if not value:
            report['missing_required'].append(var)
    
    # Check optional
    for var in OPTIONAL_ENV_VARS:
        value = os.environ.get(var)
        report['optional'][var] = bool(value)
        if value:
            report['set_optional'].append(var)
    
    return report


if __name__ == '__main__':
    config_validator.print_report()
