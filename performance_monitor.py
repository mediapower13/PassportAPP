"""
Performance monitoring utilities for PassportApp
Track and analyze application performance metrics
"""

import time
from functools import wraps
from datetime import datetime
import statistics


class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self):
        self.metrics = {}
        self.request_times = []
        self.db_query_times = []
        self.web3_call_times = []
        self.ipfs_upload_times = []
    
    def record_metric(self, metric_name, value, category='general'):
        """Record a performance metric"""
        if category not in self.metrics:
            self.metrics[category] = {}
        
        if metric_name not in self.metrics[category]:
            self.metrics[category][metric_name] = []
        
        self.metrics[category][metric_name].append({
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def get_metric_stats(self, metric_name, category='general'):
        """Get statistics for a metric"""
        if category not in self.metrics or metric_name not in self.metrics[category]:
            return None
        
        values = [m['value'] for m in self.metrics[category][metric_name]]
        
        if not values:
            return None
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0
        }
    
    def record_request_time(self, duration):
        """Record request processing time"""
        self.request_times.append(duration)
        self.record_metric('request_time', duration, 'requests')
    
    def record_db_query_time(self, duration):
        """Record database query time"""
        self.db_query_times.append(duration)
        self.record_metric('db_query_time', duration, 'database')
    
    def record_web3_call_time(self, duration):
        """Record Web3 call time"""
        self.web3_call_times.append(duration)
        self.record_metric('web3_call_time', duration, 'blockchain')
    
    def record_ipfs_upload_time(self, duration):
        """Record IPFS upload time"""
        self.ipfs_upload_times.append(duration)
        self.record_metric('ipfs_upload_time', duration, 'ipfs')
    
    def get_summary(self):
        """Get performance summary"""
        summary = {
            'total_requests': len(self.request_times),
            'total_db_queries': len(self.db_query_times),
            'total_web3_calls': len(self.web3_call_times),
            'total_ipfs_uploads': len(self.ipfs_upload_times)
        }
        
        if self.request_times:
            summary['avg_request_time'] = statistics.mean(self.request_times)
            summary['max_request_time'] = max(self.request_times)
        
        if self.db_query_times:
            summary['avg_db_query_time'] = statistics.mean(self.db_query_times)
            summary['max_db_query_time'] = max(self.db_query_times)
        
        if self.web3_call_times:
            summary['avg_web3_call_time'] = statistics.mean(self.web3_call_times)
            summary['max_web3_call_time'] = max(self.web3_call_times)
        
        if self.ipfs_upload_times:
            summary['avg_ipfs_upload_time'] = statistics.mean(self.ipfs_upload_times)
            summary['max_ipfs_upload_time'] = max(self.ipfs_upload_times)
        
        return summary
    
    def clear_metrics(self):
        """Clear all metrics"""
        self.metrics.clear()
        self.request_times.clear()
        self.db_query_times.clear()
        self.web3_call_times.clear()
        self.ipfs_upload_times.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def measure_time(category='general', metric_name=None):
    """Decorator to measure function execution time"""
    def decorator(func):
        name = metric_name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000  # milliseconds
            
            performance_monitor.record_metric(name, duration, category)
            
            return result
        return wrapper
    return decorator


def measure_request_time(func):
    """Decorator to measure request processing time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start_time) * 1000
        
        performance_monitor.record_request_time(duration)
        
        return result
    return wrapper


def measure_db_query(func):
    """Decorator to measure database query time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start_time) * 1000
        
        performance_monitor.record_db_query_time(duration)
        
        return result
    return wrapper


def measure_web3_call(func):
    """Decorator to measure Web3 call time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = (time.time() - start_time) * 1000
        
        performance_monitor.record_web3_call_time(duration)
        
        return result
    return wrapper


class PerformanceAnalyzer:
    """Analyze performance bottlenecks"""
    
    @staticmethod
    def find_slow_endpoints(threshold=1000):
        """Find endpoints slower than threshold (ms)"""
        slow_endpoints = []
        
        if 'requests' in performance_monitor.metrics:
            for metric_name, records in performance_monitor.metrics['requests'].items():
                values = [r['value'] for r in records]
                avg_time = statistics.mean(values) if values else 0
                
                if avg_time > threshold:
                    slow_endpoints.append({
                        'endpoint': metric_name,
                        'avg_time': avg_time,
                        'max_time': max(values) if values else 0,
                        'count': len(values)
                    })
        
        return sorted(slow_endpoints, key=lambda x: x['avg_time'], reverse=True)
    
    @staticmethod
    def find_slow_queries(threshold=100):
        """Find database queries slower than threshold (ms)"""
        slow_queries = []
        
        if 'database' in performance_monitor.metrics:
            for metric_name, records in performance_monitor.metrics['database'].items():
                values = [r['value'] for r in records]
                avg_time = statistics.mean(values) if values else 0
                
                if avg_time > threshold:
                    slow_queries.append({
                        'query': metric_name,
                        'avg_time': avg_time,
                        'max_time': max(values) if values else 0,
                        'count': len(values)
                    })
        
        return sorted(slow_queries, key=lambda x: x['avg_time'], reverse=True)
    
    @staticmethod
    def get_performance_report():
        """Generate comprehensive performance report"""
        summary = performance_monitor.get_summary()
        slow_endpoints = PerformanceAnalyzer.find_slow_endpoints()
        slow_queries = PerformanceAnalyzer.find_slow_queries()
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': summary,
            'slow_endpoints': slow_endpoints[:10],  # Top 10
            'slow_queries': slow_queries[:10],  # Top 10
            'categories': {}
        }
        
        # Add category-wise stats
        for category, metrics in performance_monitor.metrics.items():
            report['categories'][category] = {}
            for metric_name in metrics.keys():
                stats = performance_monitor.get_metric_stats(metric_name, category)
                if stats:
                    report['categories'][category][metric_name] = stats
        
        return report
    
    @staticmethod
    def check_performance_health():
        """Check overall performance health"""
        summary = performance_monitor.get_summary()
        issues = []
        
        # Check average request time
        if 'avg_request_time' in summary and summary['avg_request_time'] > 500:
            issues.append({
                'severity': 'warning',
                'message': f"Average request time is high: {summary['avg_request_time']:.2f}ms"
            })
        
        # Check max request time
        if 'max_request_time' in summary and summary['max_request_time'] > 3000:
            issues.append({
                'severity': 'critical',
                'message': f"Maximum request time is critical: {summary['max_request_time']:.2f}ms"
            })
        
        # Check database query time
        if 'avg_db_query_time' in summary and summary['avg_db_query_time'] > 100:
            issues.append({
                'severity': 'warning',
                'message': f"Average database query time is high: {summary['avg_db_query_time']:.2f}ms"
            })
        
        # Check Web3 call time
        if 'avg_web3_call_time' in summary and summary['avg_web3_call_time'] > 2000:
            issues.append({
                'severity': 'info',
                'message': f"Average Web3 call time is elevated: {summary['avg_web3_call_time']:.2f}ms"
            })
        
        health_status = 'healthy' if not issues else 'degraded'
        critical_count = sum(1 for i in issues if i['severity'] == 'critical')
        if critical_count > 0:
            health_status = 'critical'
        
        return {
            'status': health_status,
            'issues': issues,
            'summary': summary
        }


def log_performance_metrics(logger):
    """Log current performance metrics"""
    summary = performance_monitor.get_summary()
    
    logger.info('Performance Metrics:')
    logger.info(f"  Total Requests: {summary.get('total_requests', 0)}")
    logger.info(f"  Avg Request Time: {summary.get('avg_request_time', 0):.2f}ms")
    logger.info(f"  Total DB Queries: {summary.get('total_db_queries', 0)}")
    logger.info(f"  Avg DB Query Time: {summary.get('avg_db_query_time', 0):.2f}ms")
    logger.info(f"  Total Web3 Calls: {summary.get('total_web3_calls', 0)}")
    logger.info(f"  Avg Web3 Call Time: {summary.get('avg_web3_call_time', 0):.2f}ms")
