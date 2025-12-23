"""
Prometheus metrics exporter for PassportApp
Export application metrics in Prometheus format
"""

from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest, CollectorRegistry
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from flask import Response
import time
from functools import wraps


class MetricsCollector:
    """Collect and export Prometheus metrics"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        # HTTP metrics
        self.http_requests_total = Counter(
            'http_requests_total',
            'Total HTTP requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.http_request_duration = Histogram(
            'http_request_duration_seconds',
            'HTTP request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_queries_total = Counter(
            'db_queries_total',
            'Total database queries',
            ['operation'],
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'db_query_duration_seconds',
            'Database query duration',
            ['operation'],
            registry=self.registry
        )
        
        # Web3 metrics
        self.web3_calls_total = Counter(
            'web3_calls_total',
            'Total Web3 calls',
            ['method'],
            registry=self.registry
        )
        
        self.web3_transactions_total = Counter(
            'web3_transactions_total',
            'Total Web3 transactions',
            ['status'],
            registry=self.registry
        )
        
        self.web3_call_duration = Histogram(
            'web3_call_duration_seconds',
            'Web3 call duration',
            ['method'],
            registry=self.registry
        )
        
        # NFT metrics
        self.nft_minted_total = Counter(
            'nft_minted_total',
            'Total NFTs minted',
            registry=self.registry
        )
        
        self.nft_transferred_total = Counter(
            'nft_transferred_total',
            'Total NFT transfers',
            registry=self.registry
        )
        
        # Marketplace metrics
        self.marketplace_listings_total = Counter(
            'marketplace_listings_total',
            'Total marketplace listings',
            registry=self.registry
        )
        
        self.marketplace_sales_total = Counter(
            'marketplace_sales_total',
            'Total marketplace sales',
            registry=self.registry
        )
        
        self.marketplace_revenue = Counter(
            'marketplace_revenue_eth',
            'Total marketplace revenue in ETH',
            registry=self.registry
        )
        
        # IPFS metrics
        self.ipfs_uploads_total = Counter(
            'ipfs_uploads_total',
            'Total IPFS uploads',
            ['status'],
            registry=self.registry
        )
        
        self.ipfs_upload_duration = Histogram(
            'ipfs_upload_duration_seconds',
            'IPFS upload duration',
            registry=self.registry
        )
        
        # User metrics
        self.users_total = Gauge(
            'users_total',
            'Total registered users',
            registry=self.registry
        )
        
        self.active_sessions = Gauge(
            'active_sessions',
            'Active user sessions',
            registry=self.registry
        )
        
        # Passport metrics
        self.passports_total = Gauge(
            'passports_total',
            'Total passports',
            registry=self.registry
        )
        
        self.passports_created_total = Counter(
            'passports_created_total',
            'Total passports created',
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits_total = Counter(
            'cache_hits_total',
            'Total cache hits',
            registry=self.registry
        )
        
        self.cache_misses_total = Counter(
            'cache_misses_total',
            'Total cache misses',
            registry=self.registry
        )
        
        # Error metrics
        self.errors_total = Counter(
            'errors_total',
            'Total errors',
            ['type'],
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'memory_usage_percent',
            'Memory usage percentage',
            registry=self.registry
        )
        
        self.disk_usage = Gauge(
            'disk_usage_percent',
            'Disk usage percentage',
            registry=self.registry
        )
    
    def record_http_request(self, method, endpoint, status, duration):
        """Record HTTP request metrics"""
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_db_query(self, operation, duration):
        """Record database query metrics"""
        self.db_queries_total.labels(operation=operation).inc()
        self.db_query_duration.labels(operation=operation).observe(duration)
    
    def record_web3_call(self, method, duration):
        """Record Web3 call metrics"""
        self.web3_calls_total.labels(method=method).inc()
        self.web3_call_duration.labels(method=method).observe(duration)
    
    def record_web3_transaction(self, status):
        """Record Web3 transaction"""
        self.web3_transactions_total.labels(status=status).inc()
    
    def record_nft_mint(self):
        """Record NFT minting"""
        self.nft_minted_total.inc()
    
    def record_nft_transfer(self):
        """Record NFT transfer"""
        self.nft_transferred_total.inc()
    
    def record_marketplace_listing(self):
        """Record marketplace listing"""
        self.marketplace_listings_total.inc()
    
    def record_marketplace_sale(self, price_eth):
        """Record marketplace sale"""
        self.marketplace_sales_total.inc()
        self.marketplace_revenue.inc(price_eth)
    
    def record_ipfs_upload(self, status, duration):
        """Record IPFS upload"""
        self.ipfs_uploads_total.labels(status=status).inc()
        self.ipfs_upload_duration.observe(duration)
    
    def record_passport_created(self):
        """Record passport creation"""
        self.passports_created_total.inc()
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.cache_hits_total.inc()
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.cache_misses_total.inc()
    
    def record_error(self, error_type):
        """Record error"""
        self.errors_total.labels(type=error_type).inc()
    
    def update_gauge_metrics(self):
        """Update gauge metrics"""
        try:
            import psutil
            
            # System metrics
            self.cpu_usage.set(psutil.cpu_percent())
            self.memory_usage.set(psutil.virtual_memory().percent)
            self.disk_usage.set(psutil.disk_usage('/').percent)
            
        except ImportError:
            pass
        
        # Update from database
        try:
            from models import db, User, Passport
            
            self.users_total.set(User.query.count())
            self.passports_total.set(Passport.query.count())
            
        except:
            pass
    
    def get_metrics(self):
        """Get metrics in Prometheus format"""
        self.update_gauge_metrics()
        return generate_latest(self.registry)


# Global metrics collector
metrics_collector = MetricsCollector()


def metrics_endpoint():
    """Flask endpoint to expose Prometheus metrics"""
    return Response(metrics_collector.get_metrics(), mimetype=CONTENT_TYPE_LATEST)


def track_http_request(func):
    """Decorator to track HTTP request metrics"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request
        
        start_time = time.time()
        
        try:
            response = func(*args, **kwargs)
            
            duration = time.time() - start_time
            
            # Get status code
            if isinstance(response, tuple):
                status = response[1]
            else:
                status = 200
            
            metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=status,
                duration=duration
            )
            
            return response
        
        except Exception as e:
            duration = time.time() - start_time
            
            metrics_collector.record_http_request(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=500,
                duration=duration
            )
            
            metrics_collector.record_error(type(e).__name__)
            
            raise
    
    return wrapper


def track_db_query(operation):
    """Decorator to track database query metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_db_query(operation, duration)
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_db_query(operation, duration)
                metrics_collector.record_error('DatabaseError')
                raise
        
        return wrapper
    return decorator


def track_web3_call(method):
    """Decorator to track Web3 call metrics"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics_collector.record_web3_call(method, duration)
                return result
            
            except Exception as e:
                duration = time.time() - start_time
                metrics_collector.record_web3_call(method, duration)
                metrics_collector.record_error('Web3Error')
                raise
        
        return wrapper
    return decorator


# Helper functions
def increment_metric(metric_name, **labels):
    """Increment a counter metric"""
    if hasattr(metrics_collector, metric_name):
        metric = getattr(metrics_collector, metric_name)
        if labels:
            metric.labels(**labels).inc()
        else:
            metric.inc()


def observe_metric(metric_name, value, **labels):
    """Observe a histogram/summary metric"""
    if hasattr(metrics_collector, metric_name):
        metric = getattr(metrics_collector, metric_name)
        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)


def set_gauge(metric_name, value, **labels):
    """Set a gauge metric"""
    if hasattr(metrics_collector, metric_name):
        metric = getattr(metrics_collector, metric_name)
        if labels:
            metric.labels(**labels).set(value)
        else:
            metric.set(value)
