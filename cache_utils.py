"""
Caching utilities for PassportApp
Implement caching strategies for improved performance
"""

from functools import wraps
from flask import request
import hashlib
import json
import time
from datetime import datetime, timedelta


class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key):
        """Get value from cache"""
        if key in self.cache:
            # Check if expired
            if key in self.timestamps:
                if time.time() > self.timestamps[key]:
                    # Expired
                    del self.cache[key]
                    del self.timestamps[key]
                    self.miss_count += 1
                    return None
            
            self.hit_count += 1
            return self.cache[key]
        
        self.miss_count += 1
        return None
    
    def set(self, key, value, timeout=300):
        """Set value in cache with optional timeout (seconds)"""
        self.cache[key] = value
        if timeout:
            self.timestamps[key] = time.time() + timeout
    
    def delete(self, key):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.timestamps:
                del self.timestamps[key]
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.timestamps.clear()
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total * 100) if total > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': f'{hit_rate:.2f}%'
        }
    
    def cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if current_time > timestamp
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)


# Global cache instance
cache = SimpleCache()


def cache_key(*args, **kwargs):
    """Generate cache key from arguments"""
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_str = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(timeout=300, key_prefix=''):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f'{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}'
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, timeout)
            
            return result
        return wrapper
    return decorator


def cache_page(timeout=60):
    """Decorator to cache entire page response"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from URL and query params
            cache_key_str = f'page:{request.url}'
            
            # Check cache
            result = cache.get(cache_key_str)
            if result is not None:
                return result
            
            # Call view function and cache response
            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern=None):
    """Invalidate cache entries matching pattern"""
    if pattern is None:
        cache.clear()
        return
    
    keys_to_delete = [
        key for key in cache.cache.keys()
        if pattern in key
    ]
    
    for key in keys_to_delete:
        cache.delete(key)
    
    return len(keys_to_delete)


class Web3Cache:
    """Specialized cache for Web3 data"""
    
    def __init__(self):
        self.transaction_cache = SimpleCache()
        self.contract_cache = SimpleCache()
        self.ipfs_cache = SimpleCache()
    
    def cache_transaction(self, tx_hash, tx_data, timeout=3600):
        """Cache transaction data"""
        self.transaction_cache.set(f'tx:{tx_hash}', tx_data, timeout)
    
    def get_transaction(self, tx_hash):
        """Get cached transaction"""
        return self.transaction_cache.get(f'tx:{tx_hash}')
    
    def cache_contract_call(self, contract_addr, method, params, result, timeout=300):
        """Cache contract call result"""
        key = f'contract:{contract_addr}:{method}:{cache_key(params)}'
        self.contract_cache.set(key, result, timeout)
    
    def get_contract_call(self, contract_addr, method, params):
        """Get cached contract call"""
        key = f'contract:{contract_addr}:{method}:{cache_key(params)}'
        return self.contract_cache.get(key)
    
    def cache_ipfs_content(self, ipfs_hash, content, timeout=7200):
        """Cache IPFS content"""
        self.ipfs_cache.set(f'ipfs:{ipfs_hash}', content, timeout)
    
    def get_ipfs_content(self, ipfs_hash):
        """Get cached IPFS content"""
        return self.ipfs_cache.get(f'ipfs:{ipfs_hash}')
    
    def clear_all(self):
        """Clear all Web3 caches"""
        self.transaction_cache.clear()
        self.contract_cache.clear()
        self.ipfs_cache.clear()


# Global Web3 cache instance
web3_cache = Web3Cache()


def get_cache_stats():
    """Get statistics for all caches"""
    return {
        'main_cache': cache.get_stats(),
        'web3': {
            'transactions': web3_cache.transaction_cache.get_stats(),
            'contracts': web3_cache.contract_cache.get_stats(),
            'ipfs': web3_cache.ipfs_cache.get_stats()
        }
    }


def cleanup_all_caches():
    """Cleanup expired entries from all caches"""
    stats = {
        'main': cache.cleanup_expired(),
        'web3_transactions': web3_cache.transaction_cache.cleanup_expired(),
        'web3_contracts': web3_cache.contract_cache.cleanup_expired(),
        'web3_ipfs': web3_cache.ipfs_cache.cleanup_expired()
    }
    
    return stats
