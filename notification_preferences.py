"""
Notification preferences system for PassportApp
Manage user notification settings and delivery channels
"""

from datetime import datetime
import json


class NotificationChannel:
    """Notification delivery channels"""
    EMAIL = 'email'
    SMS = 'sms'
    PUSH = 'push'
    WEBHOOK = 'webhook'
    IN_APP = 'in_app'


class NotificationType:
    """Types of notifications"""
    PASSPORT_CREATED = 'passport_created'
    PASSPORT_UPDATED = 'passport_updated'
    PASSPORT_EXPIRING = 'passport_expiring'
    NFT_MINTED = 'nft_minted'
    NFT_TRANSFERRED = 'nft_transferred'
    NFT_LISTED = 'nft_listed'
    NFT_SOLD = 'nft_sold'
    MARKETPLACE_PURCHASE = 'marketplace_purchase'
    TRANSACTION_CONFIRMED = 'transaction_confirmed'
    TRANSACTION_FAILED = 'transaction_failed'
    SECURITY_ALERT = 'security_alert'
    ACCOUNT_LOGIN = 'account_login'
    ACCOUNT_UPDATE = 'account_update'
    SYSTEM_MAINTENANCE = 'system_maintenance'
    BLOCKCHAIN_EVENT = 'blockchain_event'


class NotificationPreferences:
    """Manage notification preferences for a user"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.preferences = self._load_default_preferences()
    
    def _load_default_preferences(self):
        """Load default notification preferences"""
        return {
            NotificationType.PASSPORT_CREATED: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.PASSPORT_UPDATED: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.PASSPORT_EXPIRING: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PUSH]
            },
            NotificationType.NFT_MINTED: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.NFT_TRANSFERRED: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.NFT_LISTED: {
                'enabled': True,
                'channels': [NotificationChannel.IN_APP]
            },
            NotificationType.NFT_SOLD: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP]
            },
            NotificationType.MARKETPLACE_PURCHASE: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.TRANSACTION_CONFIRMED: {
                'enabled': True,
                'channels': [NotificationChannel.IN_APP]
            },
            NotificationType.TRANSACTION_FAILED: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.PUSH, NotificationChannel.IN_APP]
            },
            NotificationType.SECURITY_ALERT: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PUSH]
            },
            NotificationType.ACCOUNT_LOGIN: {
                'enabled': False,
                'channels': [NotificationChannel.EMAIL]
            },
            NotificationType.ACCOUNT_UPDATE: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.SYSTEM_MAINTENANCE: {
                'enabled': True,
                'channels': [NotificationChannel.EMAIL, NotificationChannel.IN_APP]
            },
            NotificationType.BLOCKCHAIN_EVENT: {
                'enabled': False,
                'channels': [NotificationChannel.IN_APP]
            }
        }
    
    def is_enabled(self, notification_type):
        """Check if notification type is enabled"""
        if notification_type not in self.preferences:
            return False
        
        return self.preferences[notification_type].get('enabled', False)
    
    def get_channels(self, notification_type):
        """Get enabled channels for notification type"""
        if not self.is_enabled(notification_type):
            return []
        
        return self.preferences[notification_type].get('channels', [])
    
    def enable_notification(self, notification_type):
        """Enable a notification type"""
        if notification_type in self.preferences:
            self.preferences[notification_type]['enabled'] = True
            return True
        return False
    
    def disable_notification(self, notification_type):
        """Disable a notification type"""
        if notification_type in self.preferences:
            self.preferences[notification_type]['enabled'] = False
            return True
        return False
    
    def add_channel(self, notification_type, channel):
        """Add a delivery channel to notification type"""
        if notification_type not in self.preferences:
            return False
        
        channels = self.preferences[notification_type].get('channels', [])
        
        if channel not in channels:
            channels.append(channel)
            self.preferences[notification_type]['channels'] = channels
            return True
        
        return False
    
    def remove_channel(self, notification_type, channel):
        """Remove a delivery channel from notification type"""
        if notification_type not in self.preferences:
            return False
        
        channels = self.preferences[notification_type].get('channels', [])
        
        if channel in channels:
            channels.remove(channel)
            self.preferences[notification_type]['channels'] = channels
            return True
        
        return False
    
    def set_channels(self, notification_type, channels):
        """Set delivery channels for notification type"""
        if notification_type not in self.preferences:
            return False
        
        self.preferences[notification_type]['channels'] = channels
        return True
    
    def get_all_preferences(self):
        """Get all notification preferences"""
        return self.preferences
    
    def update_preferences(self, new_preferences):
        """Update multiple preferences at once"""
        for notification_type, settings in new_preferences.items():
            if notification_type in self.preferences:
                if 'enabled' in settings:
                    self.preferences[notification_type]['enabled'] = settings['enabled']
                
                if 'channels' in settings:
                    self.preferences[notification_type]['channels'] = settings['channels']
        
        return True
    
    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'user_id': self.user_id,
            'preferences': self.preferences,
            'updated_at': datetime.utcnow().isoformat()
        }
    
    def from_dict(self, data):
        """Load preferences from dictionary"""
        if 'preferences' in data:
            self.preferences = data['preferences']
        
        return True


class NotificationSchedule:
    """Manage notification delivery schedules"""
    
    def __init__(self):
        self.quiet_hours = {
            'enabled': False,
            'start_hour': 22,  # 10 PM
            'end_hour': 8,     # 8 AM
            'timezone': 'UTC'
        }
        
        self.digest_settings = {
            'enabled': False,
            'frequency': 'daily',  # daily, weekly
            'time': '09:00',
            'types': []
        }
    
    def is_quiet_hours(self, current_time=None):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours['enabled']:
            return False
        
        if current_time is None:
            current_time = datetime.utcnow()
        
        current_hour = current_time.hour
        start = self.quiet_hours['start_hour']
        end = self.quiet_hours['end_hour']
        
        if start < end:
            return start <= current_hour < end
        else:
            return current_hour >= start or current_hour < end
    
    def enable_quiet_hours(self, start_hour, end_hour, timezone='UTC'):
        """Enable quiet hours"""
        self.quiet_hours = {
            'enabled': True,
            'start_hour': start_hour,
            'end_hour': end_hour,
            'timezone': timezone
        }
    
    def disable_quiet_hours(self):
        """Disable quiet hours"""
        self.quiet_hours['enabled'] = False
    
    def enable_digest(self, frequency='daily', time='09:00', types=None):
        """Enable notification digest"""
        self.digest_settings = {
            'enabled': True,
            'frequency': frequency,
            'time': time,
            'types': types or []
        }
    
    def disable_digest(self):
        """Disable notification digest"""
        self.digest_settings['enabled'] = False
    
    def should_digest(self, notification_type):
        """Check if notification should be included in digest"""
        if not self.digest_settings['enabled']:
            return False
        
        if not self.digest_settings['types']:
            return False
        
        return notification_type in self.digest_settings['types']


class NotificationFilter:
    """Filter notifications based on criteria"""
    
    def __init__(self):
        self.filters = {
            'min_value': None,  # Minimum transaction value to notify
            'keywords': [],     # Keyword filters
            'senders': [],      # Whitelist/blacklist of senders
            'priority': 'all'   # all, high, critical
        }
    
    def set_min_value(self, value):
        """Set minimum transaction value for notifications"""
        self.filters['min_value'] = value
    
    def add_keyword(self, keyword):
        """Add keyword filter"""
        if keyword not in self.filters['keywords']:
            self.filters['keywords'].append(keyword)
    
    def remove_keyword(self, keyword):
        """Remove keyword filter"""
        if keyword in self.filters['keywords']:
            self.filters['keywords'].remove(keyword)
    
    def set_priority(self, priority):
        """Set minimum priority level"""
        if priority in ['all', 'high', 'critical']:
            self.filters['priority'] = priority
            return True
        return False
    
    def should_notify(self, notification_data):
        """Check if notification passes filters"""
        # Check minimum value
        if self.filters['min_value'] is not None:
            value = notification_data.get('value', 0)
            if value < self.filters['min_value']:
                return False
        
        # Check priority
        priority = notification_data.get('priority', 'normal')
        if self.filters['priority'] == 'high' and priority not in ['high', 'critical']:
            return False
        elif self.filters['priority'] == 'critical' and priority != 'critical':
            return False
        
        # Check keywords
        if self.filters['keywords']:
            message = notification_data.get('message', '').lower()
            if not any(keyword.lower() in message for keyword in self.filters['keywords']):
                return False
        
        return True


class NotificationPreferenceManager:
    """Manage notification preferences for all users"""
    
    def __init__(self):
        self.user_preferences = {}
        self.user_schedules = {}
        self.user_filters = {}
    
    def get_preferences(self, user_id):
        """Get preferences for a user"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = NotificationPreferences(user_id)
        
        return self.user_preferences[user_id]
    
    def get_schedule(self, user_id):
        """Get schedule for a user"""
        if user_id not in self.user_schedules:
            self.user_schedules[user_id] = NotificationSchedule()
        
        return self.user_schedules[user_id]
    
    def get_filter(self, user_id):
        """Get filter for a user"""
        if user_id not in self.user_filters:
            self.user_filters[user_id] = NotificationFilter()
        
        return self.user_filters[user_id]
    
    def should_send_notification(self, user_id, notification_type, notification_data=None):
        """Check if notification should be sent to user"""
        # Check if notification type is enabled
        preferences = self.get_preferences(user_id)
        if not preferences.is_enabled(notification_type):
            return False, []
        
        # Check quiet hours
        schedule = self.get_schedule(user_id)
        if schedule.is_quiet_hours():
            # Check if this is critical notification
            if notification_data and notification_data.get('priority') == 'critical':
                pass  # Send critical notifications even during quiet hours
            else:
                return False, []
        
        # Check digest
        if schedule.should_digest(notification_type):
            return False, []  # Will be sent in digest
        
        # Check filters
        if notification_data:
            notification_filter = self.get_filter(user_id)
            if not notification_filter.should_notify(notification_data):
                return False, []
        
        # Get delivery channels
        channels = preferences.get_channels(notification_type)
        
        return True, channels
    
    def export_preferences(self, user_id):
        """Export user preferences to JSON"""
        data = {
            'user_id': user_id,
            'preferences': self.get_preferences(user_id).to_dict(),
            'schedule': {
                'quiet_hours': self.get_schedule(user_id).quiet_hours,
                'digest': self.get_schedule(user_id).digest_settings
            },
            'filters': self.get_filter(user_id).filters
        }
        
        return json.dumps(data, indent=2)
    
    def import_preferences(self, user_id, json_data):
        """Import user preferences from JSON"""
        try:
            data = json.loads(json_data) if isinstance(json_data, str) else json_data
            
            # Import preferences
            if 'preferences' in data:
                prefs = self.get_preferences(user_id)
                prefs.from_dict(data['preferences'])
            
            # Import schedule
            if 'schedule' in data:
                schedule = self.get_schedule(user_id)
                if 'quiet_hours' in data['schedule']:
                    schedule.quiet_hours = data['schedule']['quiet_hours']
                if 'digest' in data['schedule']:
                    schedule.digest_settings = data['schedule']['digest']
            
            # Import filters
            if 'filters' in data:
                notification_filter = self.get_filter(user_id)
                notification_filter.filters = data['filters']
            
            return True
        
        except Exception as e:
            print(f"Error importing preferences: {e}")
            return False


# Global notification preference manager
notification_manager = NotificationPreferenceManager()
