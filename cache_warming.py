"""
Cache warming utilities for PassportApp
Preload frequently accessed data into cache
"""

import time
from datetime import datetime, timedelta
import threading


class CacheWarmer:
    """Warm up cache with frequently accessed data"""
    
    def __init__(self, cache_client):
        self.cache = cache_client
        self.warming_tasks = []
        self.stats = {
            'total_warmed': 0,
            'last_warm': None,
            'failed': 0
        }
    
    def register_warming_task(self, name, data_func, ttl=3600, priority=1):
        """Register a cache warming task"""
        task = {
            'name': name,
            'data_func': data_func,
            'ttl': ttl,
            'priority': priority,
            'last_run': None
        }
        
        self.warming_tasks.append(task)
        self.warming_tasks.sort(key=lambda t: t['priority'], reverse=True)
    
    def warm_cache(self, task_name=None):
        """Warm cache with data"""
        if task_name:
            tasks = [t for t in self.warming_tasks if t['name'] == task_name]
        else:
            tasks = self.warming_tasks
        
        for task in tasks:
            try:
                print(f"Warming cache: {task['name']}")
                
                # Get data
                data = task['data_func']()
                
                # Store in cache
                if isinstance(data, dict):
                    for key, value in data.items():
                        self.cache.set(key, value, task['ttl'])
                        self.stats['total_warmed'] += 1
                else:
                    self.cache.set(task['name'], data, task['ttl'])
                    self.stats['total_warmed'] += 1
                
                task['last_run'] = datetime.utcnow()
                self.stats['last_warm'] = datetime.utcnow()
                
                print(f"Cache warmed: {task['name']}")
            
            except Exception as e:
                print(f"Failed to warm cache {task['name']}: {e}")
                self.stats['failed'] += 1
    
    def warm_on_startup(self):
        """Warm cache on application startup"""
        print("Warming cache on startup...")
        self.warm_cache()
        print("Cache warming completed")
    
    def warm_periodically(self, interval=3600):
        """Warm cache periodically in background"""
        def warm_loop():
            while True:
                time.sleep(interval)
                self.warm_cache()
        
        thread = threading.Thread(target=warm_loop, daemon=True)
        thread.start()
    
    def get_stats(self):
        """Get cache warming statistics"""
        return self.stats


class DataPreloader:
    """Preload frequently accessed data"""
    
    def __init__(self, cache_client):
        self.cache = cache_client
    
    def preload_popular_passports(self, db):
        """Preload most viewed passports"""
        print("Preloading popular passports...")
        
        # Simulate fetching popular passports
        popular_passports = []  # Would query from DB
        
        data = {}
        for passport in popular_passports:
            key = f"passport:{passport['id']}"
            data[key] = passport
        
        return data
    
    def preload_active_users(self, db):
        """Preload active user data"""
        print("Preloading active users...")
        
        # Simulate fetching active users
        active_users = []  # Would query from DB
        
        data = {}
        for user in active_users:
            key = f"user:{user['id']}"
            data[key] = user
        
        return data
    
    def preload_nft_metadata(self, db):
        """Preload NFT metadata"""
        print("Preloading NFT metadata...")
        
        # Simulate fetching NFT metadata
        nfts = []  # Would query from DB
        
        data = {}
        for nft in nfts:
            key = f"nft:{nft['token_id']}"
            data[key] = nft
        
        return data
    
    def preload_marketplace_listings(self, db):
        """Preload active marketplace listings"""
        print("Preloading marketplace listings...")
        
        # Simulate fetching listings
        listings = []  # Would query from DB
        
        return {'marketplace:listings': listings}
    
    def preload_user_settings(self, db):
        """Preload user settings"""
        print("Preloading user settings...")
        
        # Simulate fetching settings
        settings = []  # Would query from DB
        
        data = {}
        for setting in settings:
            key = f"settings:{setting['user_id']}"
            data[key] = setting
        
        return data


class QueryResultCache:
    """Cache database query results"""
    
    def __init__(self, cache_client):
        self.cache = cache_client
        self.default_ttl = 300  # 5 minutes
    
    def get_or_execute(self, cache_key, query_func, ttl=None):
        """Get from cache or execute query"""
        if ttl is None:
            ttl = self.default_ttl
        
        # Try to get from cache
        cached_result = self.cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result, True  # From cache
        
        # Execute query
        result = query_func()
        
        # Store in cache
        if result is not None:
            self.cache.set(cache_key, result, ttl)
        
        return result, False  # Fresh query
    
    def invalidate(self, cache_key):
        """Invalidate cache entry"""
        self.cache.delete(cache_key)
    
    def invalidate_pattern(self, pattern):
        """Invalidate all keys matching pattern"""
        # This would depend on cache implementation
        # For Redis: SCAN + DEL
        pass


class CacheStrategy:
    """Different caching strategies"""
    
    @staticmethod
    def cache_aside(cache, key, fetch_func, ttl=3600):
        """Cache-aside (lazy loading)"""
        # Check cache
        value = cache.get(key)
        
        if value is not None:
            return value
        
        # Fetch from source
        value = fetch_func()
        
        # Store in cache
        if value is not None:
            cache.set(key, value, ttl)
        
        return value
    
    @staticmethod
    def write_through(cache, db, key, value, ttl=3600):
        """Write-through caching"""
        # Write to database
        db.save(key, value)
        
        # Write to cache
        cache.set(key, value, ttl)
    
    @staticmethod
    def write_behind(cache, queue, key, value, ttl=3600):
        """Write-behind caching"""
        # Write to cache immediately
        cache.set(key, value, ttl)
        
        # Queue database write
        queue.put(('write', key, value))
    
    @staticmethod
    def refresh_ahead(cache, key, fetch_func, ttl=3600, refresh_threshold=0.8):
        """Refresh-ahead caching"""
        # Get from cache with TTL info
        value, ttl_remaining = cache.get_with_ttl(key)
        
        if value is None:
            # Cache miss - fetch and cache
            value = fetch_func()
            cache.set(key, value, ttl)
            return value
        
        # Check if we should refresh
        if ttl_remaining < (ttl * refresh_threshold):
            # Refresh in background
            threading.Thread(
                target=lambda: cache.set(key, fetch_func(), ttl),
                daemon=True
            ).start()
        
        return value


class CachePreheatScheduler:
    """Schedule cache preheating"""
    
    def __init__(self, cache_warmer):
        self.warmer = cache_warmer
        self.schedules = []
    
    def schedule_daily(self, hour=2, minute=0):
        """Schedule daily cache warming"""
        schedule = {
            'type': 'daily',
            'hour': hour,
            'minute': minute
        }
        
        self.schedules.append(schedule)
    
    def schedule_hourly(self, minute=0):
        """Schedule hourly cache warming"""
        schedule = {
            'type': 'hourly',
            'minute': minute
        }
        
        self.schedules.append(schedule)
    
    def schedule_interval(self, seconds):
        """Schedule cache warming at interval"""
        schedule = {
            'type': 'interval',
            'seconds': seconds
        }
        
        self.schedules.append(schedule)
    
    def run_scheduler(self):
        """Run scheduled cache warming"""
        def scheduler_loop():
            while True:
                now = datetime.utcnow()
                
                for schedule in self.schedules:
                    if self._should_run(schedule, now):
                        self.warmer.warm_cache()
                
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=scheduler_loop, daemon=True)
        thread.start()
    
    def _should_run(self, schedule, now):
        """Check if schedule should run"""
        if schedule['type'] == 'daily':
            return now.hour == schedule['hour'] and now.minute == schedule['minute']
        
        elif schedule['type'] == 'hourly':
            return now.minute == schedule['minute']
        
        elif schedule['type'] == 'interval':
            # This would need to track last run time
            pass
        
        return False


# Simple in-memory cache for testing
class SimpleCache:
    """Simple in-memory cache"""
    
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key):
        """Get value from cache"""
        if key in self.expiry:
            if datetime.utcnow() > self.expiry[key]:
                del self.cache[key]
                del self.expiry[key]
                return None
        
        return self.cache.get(key)
    
    def get_with_ttl(self, key):
        """Get value with remaining TTL"""
        value = self.get(key)
        
        if value is None:
            return None, 0
        
        if key in self.expiry:
            remaining = (self.expiry[key] - datetime.utcnow()).total_seconds()
            return value, max(0, remaining)
        
        return value, 0
    
    def set(self, key, value, ttl=3600):
        """Set value in cache"""
        self.cache[key] = value
        
        if ttl:
            self.expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)
    
    def delete(self, key):
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
        
        if key in self.expiry:
            del self.expiry[key]


# Initialize cache warming
def init_cache_warming(cache_client, db):
    """Initialize cache warming system"""
    warmer = CacheWarmer(cache_client)
    preloader = DataPreloader(cache_client)
    
    # Register warming tasks
    warmer.register_warming_task(
        'popular_passports',
        lambda: preloader.preload_popular_passports(db),
        ttl=1800,
        priority=5
    )
    
    warmer.register_warming_task(
        'active_users',
        lambda: preloader.preload_active_users(db),
        ttl=600,
        priority=4
    )
    
    warmer.register_warming_task(
        'nft_metadata',
        lambda: preloader.preload_nft_metadata(db),
        ttl=3600,
        priority=3
    )
    
    warmer.register_warming_task(
        'marketplace_listings',
        lambda: preloader.preload_marketplace_listings(db),
        ttl=300,
        priority=5
    )
    
    # Warm on startup
    warmer.warm_on_startup()
    
    # Schedule periodic warming
    scheduler = CachePreheatScheduler(warmer)
    scheduler.schedule_hourly(minute=0)
    scheduler.run_scheduler()
    
    return warmer
