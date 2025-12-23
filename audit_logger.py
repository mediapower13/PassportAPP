"""
Audit trail and activity logging for PassportApp
Track all user actions and system events
"""

from datetime import datetime
import json
from flask import request, session
from functools import wraps


class AuditLogger:
    """Log audit trail for all activities"""
    
    def __init__(self, log_file='logs/audit.log'):
        self.log_file = log_file
        self.ensure_log_directory()
        self.activity_buffer = []
    
    def ensure_log_directory(self):
        """Ensure log directory exists"""
        import os
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_activity(self, user_id, action, resource_type, resource_id=None, 
                     details=None, ip_address=None, user_agent=None, status='success'):
        """Log user activity"""
        activity = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details or {},
            'ip_address': ip_address or self._get_ip_address(),
            'user_agent': user_agent or self._get_user_agent(),
            'status': status
        }
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(activity) + '\n')
        
        # Add to buffer
        self.activity_buffer.append(activity)
        
        # Keep only last 1000 in buffer
        if len(self.activity_buffer) > 1000:
            self.activity_buffer = self.activity_buffer[-1000:]
        
        return activity
    
    def log_login(self, user_id, success=True):
        """Log login attempt"""
        return self.log_activity(
            user_id=user_id,
            action='login',
            resource_type='auth',
            status='success' if success else 'failed'
        )
    
    def log_logout(self, user_id):
        """Log logout"""
        return self.log_activity(
            user_id=user_id,
            action='logout',
            resource_type='auth'
        )
    
    def log_passport_create(self, user_id, passport_id, passport_number):
        """Log passport creation"""
        return self.log_activity(
            user_id=user_id,
            action='create',
            resource_type='passport',
            resource_id=passport_id,
            details={'passport_number': passport_number}
        )
    
    def log_passport_update(self, user_id, passport_id, changes):
        """Log passport update"""
        return self.log_activity(
            user_id=user_id,
            action='update',
            resource_type='passport',
            resource_id=passport_id,
            details={'changes': changes}
        )
    
    def log_passport_delete(self, user_id, passport_id):
        """Log passport deletion"""
        return self.log_activity(
            user_id=user_id,
            action='delete',
            resource_type='passport',
            resource_id=passport_id
        )
    
    def log_nft_mint(self, user_id, token_id, passport_id, tx_hash):
        """Log NFT minting"""
        return self.log_activity(
            user_id=user_id,
            action='mint',
            resource_type='nft',
            resource_id=token_id,
            details={'passport_id': passport_id, 'tx_hash': tx_hash}
        )
    
    def log_nft_transfer(self, user_id, token_id, from_address, to_address, tx_hash):
        """Log NFT transfer"""
        return self.log_activity(
            user_id=user_id,
            action='transfer',
            resource_type='nft',
            resource_id=token_id,
            details={
                'from': from_address,
                'to': to_address,
                'tx_hash': tx_hash
            }
        )
    
    def log_marketplace_list(self, user_id, listing_id, token_id, price):
        """Log marketplace listing"""
        return self.log_activity(
            user_id=user_id,
            action='list',
            resource_type='marketplace',
            resource_id=listing_id,
            details={'token_id': token_id, 'price': price}
        )
    
    def log_marketplace_purchase(self, user_id, listing_id, token_id, price, tx_hash):
        """Log marketplace purchase"""
        return self.log_activity(
            user_id=user_id,
            action='purchase',
            resource_type='marketplace',
            resource_id=listing_id,
            details={
                'token_id': token_id,
                'price': price,
                'tx_hash': tx_hash
            }
        )
    
    def log_transaction(self, user_id, tx_hash, tx_type, status):
        """Log blockchain transaction"""
        return self.log_activity(
            user_id=user_id,
            action='transaction',
            resource_type='blockchain',
            resource_id=tx_hash,
            details={'type': tx_type, 'status': status}
        )
    
    def log_api_call(self, user_id, endpoint, method, status_code):
        """Log API call"""
        return self.log_activity(
            user_id=user_id,
            action='api_call',
            resource_type='api',
            details={
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code
            }
        )
    
    def log_error(self, user_id, error_type, error_message):
        """Log error"""
        return self.log_activity(
            user_id=user_id,
            action='error',
            resource_type='system',
            details={
                'error_type': error_type,
                'message': error_message
            },
            status='error'
        )
    
    def get_user_activity(self, user_id, limit=100):
        """Get recent activity for user"""
        activities = [
            activity for activity in self.activity_buffer
            if activity['user_id'] == user_id
        ]
        return activities[-limit:]
    
    def get_resource_activity(self, resource_type, resource_id, limit=100):
        """Get activity for specific resource"""
        activities = [
            activity for activity in self.activity_buffer
            if activity['resource_type'] == resource_type and 
               activity['resource_id'] == resource_id
        ]
        return activities[-limit:]
    
    def get_recent_activity(self, limit=100):
        """Get recent activity across all users"""
        return self.activity_buffer[-limit:]
    
    def _get_ip_address(self):
        """Get client IP address"""
        try:
            if request.headers.get('X-Forwarded-For'):
                return request.headers.get('X-Forwarded-For').split(',')[0]
            return request.remote_addr
        except:
            return 'unknown'
    
    def _get_user_agent(self):
        """Get user agent"""
        try:
            return request.headers.get('User-Agent', 'unknown')
        except:
            return 'unknown'


# Global audit logger
audit_logger = AuditLogger()


def audit_action(action, resource_type):
    """Decorator to automatically audit an action"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = session.get('user_id', 'anonymous')
            
            try:
                result = func(*args, **kwargs)
                
                # Extract resource_id from result if it's a dict
                resource_id = None
                if isinstance(result, dict):
                    resource_id = result.get('id') or result.get('resource_id')
                
                audit_logger.log_activity(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status='success'
                )
                
                return result
            
            except Exception as e:
                audit_logger.log_activity(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    status='failed',
                    details={'error': str(e)}
                )
                raise
        
        return wrapper
    return decorator


class ActivityTracker:
    """Track user activity statistics"""
    
    def __init__(self):
        self.activity_counts = {}
    
    def increment(self, user_id, activity_type):
        """Increment activity counter"""
        if user_id not in self.activity_counts:
            self.activity_counts[user_id] = {}
        
        if activity_type not in self.activity_counts[user_id]:
            self.activity_counts[user_id][activity_type] = 0
        
        self.activity_counts[user_id][activity_type] += 1
    
    def get_user_stats(self, user_id):
        """Get activity stats for user"""
        return self.activity_counts.get(user_id, {})
    
    def get_most_active_users(self, limit=10):
        """Get most active users"""
        user_totals = {
            user_id: sum(counts.values())
            for user_id, counts in self.activity_counts.items()
        }
        
        sorted_users = sorted(
            user_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_users[:limit]


# Global activity tracker
activity_tracker = ActivityTracker()


def get_audit_summary(days=7):
    """Get audit summary for last N days"""
    from datetime import timedelta
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    summary = {
        'total_activities': 0,
        'by_action': {},
        'by_resource': {},
        'by_status': {'success': 0, 'failed': 0, 'error': 0},
        'unique_users': set()
    }
    
    for activity in audit_logger.activity_buffer:
        activity_time = datetime.fromisoformat(activity['timestamp'])
        
        if activity_time < cutoff:
            continue
        
        summary['total_activities'] += 1
        
        # Count by action
        action = activity['action']
        summary['by_action'][action] = summary['by_action'].get(action, 0) + 1
        
        # Count by resource
        resource = activity['resource_type']
        summary['by_resource'][resource] = summary['by_resource'].get(resource, 0) + 1
        
        # Count by status
        status = activity['status']
        summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
        
        # Track unique users
        summary['unique_users'].add(activity['user_id'])
    
    summary['unique_users'] = len(summary['unique_users'])
    
    return summary
