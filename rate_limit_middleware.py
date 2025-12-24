"""
API rate limit middleware for PassportApp
Implement rate limiting with multiple strategies
"""

from datetime import datetime, timedelta
from functools import wraps
import time
import hashlib


class RateLimitStrategy:
    """Rate limiting strategies"""
    FIXED_WINDOW = 'fixed_window'
    SLIDING_WINDOW = 'sliding_window'
    TOKEN_BUCKET = 'token_bucket'
    LEAKY_BUCKET = 'leaky_bucket'


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, retry_after):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class FixedWindowRateLimiter:
    """Fixed window rate limiting"""
    
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key):
        """Check if request is allowed"""
        now = datetime.utcnow()
        window_start = now.replace(second=0, microsecond=0)
        
        if key not in self.requests:
            self.requests[key] = {'window': window_start, 'count': 0}
        
        request_info = self.requests[key]
        
        # Reset if new window
        if request_info['window'] < window_start:
            request_info['window'] = window_start
            request_info['count'] = 0
        
        if request_info['count'] >= self.max_requests:
            window_end = window_start + timedelta(seconds=self.window_seconds)
            retry_after = (window_end - now).total_seconds()
            return False, retry_after
        
        request_info['count'] += 1
        return True, 0
    
    def get_remaining(self, key):
        """Get remaining requests in current window"""
        if key not in self.requests:
            return self.max_requests
        
        request_info = self.requests[key]
        return max(0, self.max_requests - request_info['count'])


class SlidingWindowRateLimiter:
    """Sliding window rate limiting"""
    
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key):
        """Check if request is allowed"""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside window
        cutoff = now - self.window_seconds
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        if len(self.requests[key]) >= self.max_requests:
            oldest = self.requests[key][0]
            retry_after = oldest + self.window_seconds - now
            return False, retry_after
        
        self.requests[key].append(now)
        return True, 0
    
    def get_remaining(self, key):
        """Get remaining requests in current window"""
        if key not in self.requests:
            return self.max_requests
        
        now = time.time()
        cutoff = now - self.window_seconds
        current_requests = [req for req in self.requests[key] if req > cutoff]
        
        return max(0, self.max_requests - len(current_requests))


class TokenBucketRateLimiter:
    """Token bucket rate limiting"""
    
    def __init__(self, capacity, refill_rate):
        """
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets = {}
    
    def is_allowed(self, key):
        """Check if request is allowed"""
        now = time.time()
        
        if key not in self.buckets:
            self.buckets[key] = {
                'tokens': self.capacity,
                'last_update': now
            }
        
        bucket = self.buckets[key]
        
        # Add tokens based on time passed
        time_passed = now - bucket['last_update']
        tokens_to_add = time_passed * self.refill_rate
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now
        
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True, 0
        
        # Calculate retry after
        tokens_needed = 1 - bucket['tokens']
        retry_after = tokens_needed / self.refill_rate
        return False, retry_after
    
    def get_remaining(self, key):
        """Get remaining tokens"""
        if key not in self.buckets:
            return self.capacity
        
        now = time.time()
        bucket = self.buckets[key]
        
        time_passed = now - bucket['last_update']
        tokens_to_add = time_passed * self.refill_rate
        current_tokens = min(self.capacity, bucket['tokens'] + tokens_to_add)
        
        return int(current_tokens)


class RateLimitMiddleware:
    """Flask middleware for rate limiting"""
    
    def __init__(self, app=None):
        self.app = app
        self.limiters = {}
        self.default_limits = {
            'anonymous': (100, 3600),  # 100 requests per hour
            'authenticated': (1000, 3600),  # 1000 requests per hour
            'premium': (10000, 3600)  # 10000 requests per hour
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Configure from app config
        strategy = app.config.get('RATE_LIMIT_STRATEGY', RateLimitStrategy.SLIDING_WINDOW)
        
        for tier, (max_requests, window) in self.default_limits.items():
            if strategy == RateLimitStrategy.FIXED_WINDOW:
                self.limiters[tier] = FixedWindowRateLimiter(max_requests, window)
            elif strategy == RateLimitStrategy.SLIDING_WINDOW:
                self.limiters[tier] = SlidingWindowRateLimiter(max_requests, window)
            elif strategy == RateLimitStrategy.TOKEN_BUCKET:
                refill_rate = max_requests / window
                self.limiters[tier] = TokenBucketRateLimiter(max_requests, refill_rate)
    
    def get_client_key(self, request):
        """Get unique key for client"""
        # Try to get user ID if authenticated
        if hasattr(request, 'user') and request.user:
            return f"user:{request.user.id}"
        
        # Fall back to IP address
        ip = request.remote_addr
        if request.headers.get('X-Forwarded-For'):
            ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
        
        return f"ip:{ip}"
    
    def get_tier(self, request):
        """Get rate limit tier for request"""
        if hasattr(request, 'user') and request.user:
            if hasattr(request.user, 'is_premium') and request.user.is_premium:
                return 'premium'
            return 'authenticated'
        
        return 'anonymous'
    
    def check_rate_limit(self, request):
        """Check if request should be rate limited"""
        key = self.get_client_key(request)
        tier = self.get_tier(request)
        
        limiter = self.limiters.get(tier)
        if not limiter:
            return True, 0, self.default_limits[tier][0]
        
        allowed, retry_after = limiter.is_allowed(key)
        remaining = limiter.get_remaining(key)
        
        return allowed, retry_after, remaining


def rate_limit(max_requests=None, window_seconds=None, strategy=None):
    """
    Decorator for rate limiting endpoints
    
    Usage:
        @app.route('/api/endpoint')
        @rate_limit(max_requests=10, window_seconds=60)
        def endpoint():
            return 'Success'
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import request, jsonify
            
            # Create limiter for this endpoint
            endpoint_key = f"{request.endpoint}:{request.remote_addr}"
            
            if strategy == RateLimitStrategy.TOKEN_BUCKET:
                refill_rate = max_requests / window_seconds
                limiter = TokenBucketRateLimiter(max_requests, refill_rate)
            elif strategy == RateLimitStrategy.FIXED_WINDOW:
                limiter = FixedWindowRateLimiter(max_requests, window_seconds)
            else:
                limiter = SlidingWindowRateLimiter(max_requests, window_seconds)
            
            allowed, retry_after = limiter.is_allowed(endpoint_key)
            
            if not allowed:
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': int(retry_after)
                })
                response.status_code = 429
                response.headers['Retry-After'] = str(int(retry_after))
                return response
            
            # Add rate limit headers
            remaining = limiter.get_remaining(endpoint_key)
            response = f(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(max_requests)
                response.headers['X-RateLimit-Remaining'] = str(remaining)
                response.headers['X-RateLimit-Reset'] = str(int(time.time() + window_seconds))
            
            return response
        
        return wrapped
    return decorator


class RateLimitConfig:
    """Rate limit configuration for different endpoints"""
    
    ENDPOINTS = {
        '/api/auth/login': {
            'max_requests': 5,
            'window_seconds': 300,  # 5 requests per 5 minutes
            'strategy': RateLimitStrategy.SLIDING_WINDOW
        },
        '/api/auth/register': {
            'max_requests': 3,
            'window_seconds': 3600,  # 3 requests per hour
            'strategy': RateLimitStrategy.FIXED_WINDOW
        },
        '/api/passport/create': {
            'max_requests': 10,
            'window_seconds': 3600,  # 10 passports per hour
            'strategy': RateLimitStrategy.SLIDING_WINDOW
        },
        '/api/nft/mint': {
            'max_requests': 20,
            'window_seconds': 3600,  # 20 mints per hour
            'strategy': RateLimitStrategy.TOKEN_BUCKET
        },
        '/api/marketplace/purchase': {
            'max_requests': 50,
            'window_seconds': 3600,
            'strategy': RateLimitStrategy.SLIDING_WINDOW
        },
        '/api/search': {
            'max_requests': 100,
            'window_seconds': 60,  # 100 searches per minute
            'strategy': RateLimitStrategy.TOKEN_BUCKET
        }
    }
    
    @classmethod
    def get_config(cls, endpoint):
        """Get rate limit config for endpoint"""
        return cls.ENDPOINTS.get(endpoint, {
            'max_requests': 100,
            'window_seconds': 60,
            'strategy': RateLimitStrategy.SLIDING_WINDOW
        })


# Global rate limit middleware
rate_limit_middleware = None


def init_rate_limiting(app):
    """Initialize rate limiting for Flask app"""
    global rate_limit_middleware
    rate_limit_middleware = RateLimitMiddleware(app)
    
    # Register before_request handler
    @app.before_request
    def check_rate_limit():
        from flask import request, jsonify
        
        # Skip for static files
        if request.path.startswith('/static'):
            return None
        
        allowed, retry_after, remaining = rate_limit_middleware.check_rate_limit(request)
        
        if not allowed:
            response = jsonify({
                'error': 'Rate limit exceeded',
                'retry_after': int(retry_after)
            })
            response.status_code = 429
            response.headers['Retry-After'] = str(int(retry_after))
            return response
        
        # Store for after_request
        request.rate_limit_remaining = remaining
        return None
    
    # Add rate limit headers to responses
    @app.after_request
    def add_rate_limit_headers(response):
        from flask import request
        
        if hasattr(request, 'rate_limit_remaining'):
            tier = rate_limit_middleware.get_tier(request)
            max_requests = rate_limit_middleware.default_limits[tier][0]
            
            response.headers['X-RateLimit-Limit'] = str(max_requests)
            response.headers['X-RateLimit-Remaining'] = str(request.rate_limit_remaining)
        
        return response
    
    return rate_limit_middleware
