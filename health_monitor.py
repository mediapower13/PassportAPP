"""
Health check and monitoring endpoints for PassportApp
Monitor system health, database, blockchain connectivity
"""

from datetime import datetime
import psutil
import os


class HealthChecker:
    """System health checker"""
    
    @staticmethod
    def check_database():
        """Check database connectivity"""
        try:
            from flask import current_app
            from models import db
            
            # Try simple query
            db.session.execute('SELECT 1')
            
            return {
                'status': 'healthy',
                'message': 'Database connection successful',
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database error: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def check_blockchain():
        """Check blockchain connectivity"""
        try:
            from web3 import Web3
            import os
            
            provider_uri = os.environ.get('WEB3_PROVIDER_URI', 'http://localhost:8545')
            web3 = Web3(Web3.HTTPProvider(provider_uri))
            
            if web3.is_connected():
                block_number = web3.eth.block_number
                
                return {
                    'status': 'healthy',
                    'message': 'Blockchain connected',
                    'block_number': block_number,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'Cannot connect to blockchain',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Blockchain error: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def check_ipfs():
        """Check IPFS connectivity"""
        try:
            import requests
            import os
            
            ipfs_api = os.environ.get('IPFS_API_URL', 'https://api.pinata.cloud')
            api_key = os.environ.get('IPFS_API_KEY')
            
            if not api_key:
                return {
                    'status': 'warning',
                    'message': 'IPFS API key not configured',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            headers = {'pinata_api_key': api_key}
            response = requests.get(f'{ipfs_api}/data/testAuthentication', headers=headers, timeout=5)
            
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': 'IPFS connected',
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'message': 'IPFS authentication failed',
                    'timestamp': datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'IPFS error: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def check_disk_space():
        """Check disk space"""
        try:
            disk = psutil.disk_usage('/')
            
            percent_used = disk.percent
            free_gb = disk.free / (1024 ** 3)
            
            if percent_used > 90:
                status = 'critical'
                message = f'Disk space critical: {percent_used}% used'
            elif percent_used > 80:
                status = 'warning'
                message = f'Disk space low: {percent_used}% used'
            else:
                status = 'healthy'
                message = f'Disk space available: {free_gb:.2f} GB free'
            
            return {
                'status': status,
                'message': message,
                'percent_used': percent_used,
                'free_gb': round(free_gb, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Cannot check disk space: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def check_memory():
        """Check memory usage"""
        try:
            memory = psutil.virtual_memory()
            
            percent_used = memory.percent
            available_gb = memory.available / (1024 ** 3)
            
            if percent_used > 90:
                status = 'critical'
                message = f'Memory critical: {percent_used}% used'
            elif percent_used > 80:
                status = 'warning'
                message = f'Memory high: {percent_used}% used'
            else:
                status = 'healthy'
                message = f'Memory available: {available_gb:.2f} GB free'
            
            return {
                'status': status,
                'message': message,
                'percent_used': percent_used,
                'available_gb': round(available_gb, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Cannot check memory: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def check_cpu():
        """Check CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            
            if cpu_percent > 90:
                status = 'critical'
                message = f'CPU critical: {cpu_percent}% used'
            elif cpu_percent > 80:
                status = 'warning'
                message = f'CPU high: {cpu_percent}% used'
            else:
                status = 'healthy'
                message = f'CPU normal: {cpu_percent}% used'
            
            return {
                'status': status,
                'message': message,
                'percent_used': cpu_percent,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unknown',
                'message': f'Cannot check CPU: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def comprehensive_health_check():
        """Run comprehensive health check"""
        checks = {
            'database': HealthChecker.check_database(),
            'blockchain': HealthChecker.check_blockchain(),
            'ipfs': HealthChecker.check_ipfs(),
            'disk': HealthChecker.check_disk_space(),
            'memory': HealthChecker.check_memory(),
            'cpu': HealthChecker.check_cpu()
        }
        
        # Determine overall status
        statuses = [check['status'] for check in checks.values()]
        
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'unhealthy' in statuses:
            overall_status = 'unhealthy'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'
        
        return {
            'overall_status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': checks
        }


class SystemMetrics:
    """Collect system metrics"""
    
    @staticmethod
    def get_uptime():
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = datetime.utcnow().timestamp() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                'seconds': uptime_seconds,
                'formatted': f'{days}d {hours}h {minutes}m'
            }
        except:
            return {'seconds': 0, 'formatted': 'Unknown'}
    
    @staticmethod
    def get_process_info():
        """Get current process information"""
        try:
            process = psutil.Process(os.getpid())
            
            return {
                'pid': process.pid,
                'memory_mb': round(process.memory_info().rss / (1024 ** 2), 2),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'threads': process.num_threads(),
                'created': datetime.fromtimestamp(process.create_time()).isoformat()
            }
        except:
            return {}
    
    @staticmethod
    def get_network_stats():
        """Get network statistics"""
        try:
            net_io = psutil.net_io_counters()
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            }
        except:
            return {}
    
    @staticmethod
    def get_all_metrics():
        """Get all system metrics"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': SystemMetrics.get_uptime(),
            'process': SystemMetrics.get_process_info(),
            'network': SystemMetrics.get_network_stats(),
            'disk': HealthChecker.check_disk_space(),
            'memory': HealthChecker.check_memory(),
            'cpu': HealthChecker.check_cpu()
        }


# Global health checker instance
health_checker = HealthChecker()


def get_health_status():
    """Get current health status"""
    return health_checker.comprehensive_health_check()


def get_readiness():
    """Check if application is ready to serve requests"""
    db_check = HealthChecker.check_database()
    
    if db_check['status'] == 'healthy':
        return {'ready': True, 'timestamp': datetime.utcnow().isoformat()}
    else:
        return {'ready': False, 'reason': db_check['message'], 'timestamp': datetime.utcnow().isoformat()}


def get_liveness():
    """Check if application is alive"""
    return {'alive': True, 'timestamp': datetime.utcnow().isoformat()}
