"""
Logging configuration for PassportApp
Configure comprehensive logging for debugging and monitoring
"""

import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime


def setup_logging(app):
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set logging level
    if app.config.get('DEBUG'):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler for general logs (rotating by size)
    file_handler = RotatingFileHandler(
        'logs/passportapp.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(log_level)
    
    # File handler for errors only (rotating by time)
    error_handler = TimedRotatingFileHandler(
        'logs/errors.log',
        when='midnight',
        interval=1,
        backupCount=30
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # File handler for Web3 operations
    web3_handler = RotatingFileHandler(
        'logs/web3.log',
        maxBytes=5242880,  # 5MB
        backupCount=5
    )
    web3_handler.setFormatter(detailed_formatter)
    web3_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure app logger
    app.logger.setLevel(log_level)
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    app.logger.addHandler(console_handler)
    
    # Configure Web3 logger
    web3_logger = logging.getLogger('web3')
    web3_logger.setLevel(logging.INFO)
    web3_logger.addHandler(web3_handler)
    
    # Configure blockchain logger
    blockchain_logger = logging.getLogger('blockchain')
    blockchain_logger.setLevel(logging.INFO)
    blockchain_logger.addHandler(web3_handler)
    
    # Log startup
    app.logger.info('=' * 50)
    app.logger.info('PassportApp Starting')
    app.logger.info(f'Environment: {app.config.get("ENV", "production")}')
    app.logger.info(f'Debug Mode: {app.config.get("DEBUG", False)}')
    app.logger.info('=' * 50)
    
    return app.logger


def log_request(logger, request):
    """Log incoming request"""
    logger.info(f'Request: {request.method} {request.path} from {request.remote_addr}')


def log_response(logger, response, duration=None):
    """Log outgoing response"""
    duration_str = f' ({duration:.2f}ms)' if duration else ''
    logger.info(f'Response: {response.status_code}{duration_str}')


def log_error(logger, error, context=None):
    """Log error with context"""
    error_msg = f'Error: {str(error)}'
    if context:
        error_msg += f' | Context: {context}'
    logger.error(error_msg, exc_info=True)


def log_web3_transaction(logger, tx_type, tx_hash, status='pending'):
    """Log Web3 transaction"""
    logger.info(f'Web3 Transaction: {tx_type} | Hash: {tx_hash} | Status: {status}')


def log_blockchain_event(logger, event_type, event_data):
    """Log blockchain event"""
    logger.info(f'Blockchain Event: {event_type} | Data: {event_data}')


class RequestLogger:
    """Middleware for request logging"""
    
    def __init__(self, app):
        self.app = app
        self.logger = app.logger
    
    def __call__(self, environ, start_response):
        """Log request and response"""
        from time import time
        
        start_time = time()
        
        # Log request
        method = environ.get('REQUEST_METHOD')
        path = environ.get('PATH_INFO')
        remote_addr = environ.get('REMOTE_ADDR')
        
        self.logger.debug(f'→ {method} {path} from {remote_addr}')
        
        def custom_start_response(status, headers, exc_info=None):
            # Log response
            duration = (time() - start_time) * 1000
            self.logger.debug(f'← {status} ({duration:.2f}ms)')
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)


def configure_logger(name, log_file, level=logging.INFO):
    """Configure a custom logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = RotatingFileHandler(
        f'logs/{log_file}',
        maxBytes=5242880,
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Create specialized loggers
security_logger = None
performance_logger = None


def init_specialized_loggers():
    """Initialize specialized loggers"""
    global security_logger, performance_logger
    
    security_logger = configure_logger('security', 'security.log', logging.WARNING)
    performance_logger = configure_logger('performance', 'performance.log', logging.INFO)
    
    return security_logger, performance_logger
