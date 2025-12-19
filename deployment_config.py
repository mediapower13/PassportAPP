"""
Deployment configuration and scripts for PassportApp
Configure deployment settings for different environments
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///passportapp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Blockchain
    WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI') or 'http://localhost:8545'
    CONTRACT_ADDRESS = os.environ.get('CONTRACT_ADDRESS')
    NFT_CONTRACT_ADDRESS = os.environ.get('NFT_CONTRACT_ADDRESS')
    MARKETPLACE_CONTRACT_ADDRESS = os.environ.get('MARKETPLACE_CONTRACT_ADDRESS')
    
    # IPFS
    IPFS_API_URL = os.environ.get('IPFS_API_URL') or 'https://api.pinata.cloud'
    IPFS_API_KEY = os.environ.get('IPFS_API_KEY')
    IPFS_SECRET_KEY = os.environ.get('IPFS_SECRET_KEY')
    
    # Encryption
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # Upload
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/passportapp.log'
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = 'memory://'


class DevelopmentConfig(Config):
    """Development configuration"""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Use local blockchain
    WEB3_PROVIDER_URI = 'http://localhost:8545'
    
    # Disable CSRF for development
    WTF_CSRF_ENABLED = False
    
    # Session settings
    SESSION_COOKIE_SECURE = False
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    SQLALCHEMY_ECHO = True
    
    # Cache
    CACHE_TYPE = 'simple'


class TestingConfig(Config):
    """Testing configuration"""
    
    DEBUG = False
    TESTING = True
    ENV = 'testing'
    
    # Use in-memory database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Session settings
    SESSION_COOKIE_SECURE = False
    
    # Use test blockchain
    WEB3_PROVIDER_URI = 'http://localhost:8545'
    
    # Disable rate limiting for tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Require environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in production")
    
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    if not ENCRYPTION_KEY:
        raise ValueError("ENCRYPTION_KEY environment variable must be set in production")
    
    # Database - prefer PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable must be set in production")
    
    # Use production blockchain network
    WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI')
    if not WEB3_PROVIDER_URI:
        raise ValueError("WEB3_PROVIDER_URI environment variable must be set in production")
    
    # Require contract addresses
    if not os.environ.get('CONTRACT_ADDRESS'):
        raise ValueError("CONTRACT_ADDRESS environment variable must be set")
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    
    # Logging
    LOG_LEVEL = 'WARNING'
    
    # Cache - use Redis in production
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Rate limiting - use Redis
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')


class StagingConfig(ProductionConfig):
    """Staging configuration (similar to production but with some relaxed settings)"""
    
    ENV = 'staging'
    DEBUG = False
    
    # Use test network
    WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI') or 'https://sepolia.infura.io/v3/YOUR-PROJECT-ID'
    
    # Logging
    LOG_LEVEL = 'INFO'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])


# Deployment checklist
DEPLOYMENT_CHECKLIST = """
PassportApp Deployment Checklist
=================================

1. Environment Variables
   ☐ SECRET_KEY - Strong random secret key
   ☐ DATABASE_URL - PostgreSQL connection string
   ☐ WEB3_PROVIDER_URI - Blockchain RPC endpoint
   ☐ CONTRACT_ADDRESS - Main contract address
   ☐ NFT_CONTRACT_ADDRESS - NFT contract address
   ☐ MARKETPLACE_CONTRACT_ADDRESS - Marketplace contract address
   ☐ IPFS_API_KEY - Pinata API key
   ☐ IPFS_SECRET_KEY - Pinata secret key
   ☐ ENCRYPTION_KEY - Fernet encryption key
   ☐ REDIS_URL - Redis connection string (optional)

2. Database Setup
   ☐ Create database
   ☐ Run migrations: flask db upgrade
   ☐ Create indexes: python -c "from database_utils import add_indexes; add_indexes()"
   ☐ Verify integrity: python -c "from database_utils import verify_database_integrity; verify_database_integrity()"

3. Smart Contracts
   ☐ Deploy contracts to target network
   ☐ Verify contracts on block explorer
   ☐ Update contract addresses in .env
   ☐ Test contract interactions

4. Security
   ☐ Enable HTTPS/SSL
   ☐ Configure CORS properly
   ☐ Set secure session cookies
   ☐ Enable rate limiting
   ☐ Configure CSP headers
   ☐ Review error handlers

5. Performance
   ☐ Configure Redis caching
   ☐ Set up database connection pooling
   ☐ Enable gzip compression
   ☐ Configure CDN for static files
   ☐ Set cache headers

6. Monitoring
   ☐ Configure logging
   ☐ Set up error tracking (e.g., Sentry)
   ☐ Configure uptime monitoring
   ☐ Set up performance monitoring
   ☐ Configure alerts

7. Backup
   ☐ Set up database backups
   ☐ Configure IPFS pinning service
   ☐ Backup smart contract ABIs
   ☐ Document recovery procedures

8. Testing
   ☐ Run unit tests
   ☐ Run integration tests
   ☐ Test blockchain interactions
   ☐ Verify IPFS uploads
   ☐ Load testing

9. Documentation
   ☐ Update README.md
   ☐ Document API endpoints
   ☐ Create deployment guide
   ☐ Document environment variables
   ☐ Create troubleshooting guide

10. Launch
    ☐ Final security review
    ☐ Database migration
    ☐ DNS configuration
    ☐ SSL certificate
    ☐ Smoke tests
    ☐ Monitor for errors
"""


def print_deployment_checklist():
    """Print deployment checklist"""
    print(DEPLOYMENT_CHECKLIST)


if __name__ == '__main__':
    print_deployment_checklist()
