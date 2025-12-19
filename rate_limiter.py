"""
API rate limiting and security utilities for PassportApp
Implement rate limiting to prevent abuse and enhance security
"""

from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
import time


class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self):
        self.requests = {}  # IP -> list of timestamps
        self.blocked_ips = {}  # IP -> block_until timestamp
    
    def is_blocked(self, ip):
        """Check if IP is currently blocked"""
        if ip in self.blocked_ips:
            if time.time() < self.blocked_ips[ip]:
                return True
            else:
                # Unblock expired
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip, duration=3600):
        """Block an IP for specified duration (seconds)"""
        self.blocked_ips[ip] = time.time() + duration
    
    def check_rate_limit(self, ip, max_requests=100, window=3600):
        """
        Check if IP has exceeded rate limit
        
        Args:
            ip: IP address to check
            max_requests: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            (allowed, remaining, reset_time)
        """
        if self.is_blocked(ip):
            return False, 0, self.blocked_ips[ip]
        
        current_time = time.time()
        cutoff_time = current_time - window
        
        # Initialize or cleanup old requests
        if ip not in self.requests:
            self.requests[ip] = []
        
        # Remove old requests outside window
        self.requests[ip] = [
            timestamp for timestamp in self.requests[ip]
            if timestamp > cutoff_time
        ]
        
        # Check limit
        request_count = len(self.requests[ip])
        
        if request_count >= max_requests:
            # Rate limit exceeded
            reset_time = self.requests[ip][0] + window
            return False, 0, reset_time
        
        # Add current request
        self.requests[ip].append(current_time)
        
        remaining = max_requests - (request_count + 1)
        reset_time = current_time + window
        
        return True, remaining, reset_time
    
    def get_stats(self):
        """Get rate limiter statistics"""
        return {
            'tracked_ips': len(self.requests),
            'blocked_ips': len(self.blocked_ips),
            'total_requests': sum(len(reqs) for reqs in self.requests.values())
        }


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(max_requests=100, window=3600, block_duration=3600):
    """Decorator to apply rate limiting to routes"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr
            
            # Check rate limit
            allowed, remaining, reset_time = rate_limiter.check_rate_limit(
                ip, max_requests, window
            )
            
            if not allowed:
                # Block IP if repeatedly exceeding limit
                if remaining == 0:
                    rate_limiter.block_ip(ip, block_duration)
                
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': int(reset_time - time.time())
                }), 429
            
            # Add rate limit headers
            response = func(*args, **kwargs)
            
            # Handle tuple responses (response, status_code)
            if isinstance(response, tuple):
                resp_obj, status_code = response[0], response[1]
            else:
                resp_obj, status_code = response, 200
            
            # Set headers if response object supports it
            if hasattr(resp_obj, 'headers'):
                resp_obj.headers['X-RateLimit-Limit'] = str(max_requests)
                resp_obj.headers['X-RateLimit-Remaining'] = str(remaining)
                resp_obj.headers['X-RateLimit-Reset'] = str(int(reset_time))
            
            if isinstance(response, tuple):
                return resp_obj, status_code
            return resp_obj
        
        return wrapper
    return decorator


def api_rate_limit(max_requests=60, window=60):
    """Stricter rate limit for API endpoints"""
    return rate_limit(max_requests=max_requests, window=window)


def auth_rate_limit(max_requests=5, window=300):
    """Strict rate limit for authentication endpoints"""
    return rate_limit(max_requests=max_requests, window=window, block_duration=1800)


class SecurityMiddleware:
    """Security middleware for Flask app"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com;"
        return response
    
    @staticmethod
    def validate_content_type(request, expected='application/json'):
        """Validate request content type"""
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '')
            if expected not in content_type:
                return False, f'Content-Type must be {expected}'
        return True, None
    
    @staticmethod
    def check_csrf_token(request):
        """Basic CSRF token validation"""
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
            if not token:
                return False, 'CSRF token missing'
            # Add actual token validation logic here
        return True, None


def secure_route(func):
    """Decorator to add security checks to routes"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Validate content type for API routes
        if request.path.startswith('/api/'):
            valid, error = SecurityMiddleware.validate_content_type(request)
            if not valid:
                return jsonify({'error': error}), 400
        
        # Execute route
        response = func(*args, **kwargs)
        
        # Add security headers
        if hasattr(response, 'headers'):
            response = SecurityMiddleware.add_security_headers(response)
        
        return response
    
    return wrapper


def get_client_ip():
    """Get real client IP address (handle proxies)"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def log_suspicious_activity(ip, activity, details=None):
    """Log suspicious activity for security monitoring"""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'ip': ip,
        'activity': activity,
        'details': details,
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    # Log to security log (implement actual logging)
    print(f"[SECURITY] {log_entry}")
    
    return log_entry


def cleanup_rate_limiter():
    """Cleanup old rate limit data"""
    current_time = time.time()
    
    # Remove old request records
    for ip in list(rate_limiter.requests.keys()):
        rate_limiter.requests[ip] = [
            ts for ts in rate_limiter.requests[ip]
            if current_time - ts < 3600  # Keep last hour
        ]
        if not rate_limiter.requests[ip]:
            del rate_limiter.requests[ip]
    
    # Remove expired blocks
    for ip in list(rate_limiter.blocked_ips.keys()):
        if current_time >= rate_limiter.blocked_ips[ip]:
            del rate_limiter.blocked_ips[ip]
