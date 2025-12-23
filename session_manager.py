"""
Session management utilities for PassportApp
Advanced session handling with Redis support
"""

from datetime import datetime, timedelta
import secrets
import json
import hashlib


class SessionManager:
    """Manage user sessions"""
    
    def __init__(self, session_timeout=3600):
        self.sessions = {}  # In-memory fallback
        self.session_timeout = session_timeout  # seconds
        self.redis_client = None
        self.use_redis = False
    
    def configure_redis(self, redis_url=None):
        """Configure Redis for session storage"""
        try:
            import redis
            
            if redis_url:
                self.redis_client = redis.from_url(redis_url)
            else:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
            
            # Test connection
            self.redis_client.ping()
            self.use_redis = True
            
            return True
        
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self.use_redis = False
            return False
    
    def create_session(self, user_id, user_data=None):
        """Create new session"""
        session_id = self._generate_session_id()
        
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'user_data': user_data or {},
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'ip_address': None,
            'user_agent': None
        }
        
        if self.use_redis:
            self._save_to_redis(session_id, session_data)
        else:
            self.sessions[session_id] = session_data
        
        return session_id
    
    def get_session(self, session_id):
        """Get session data"""
        if self.use_redis:
            return self._get_from_redis(session_id)
        else:
            return self.sessions.get(session_id)
    
    def update_session(self, session_id, updates):
        """Update session data"""
        session = self.get_session(session_id)
        
        if not session:
            return False
        
        session.update(updates)
        session['last_activity'] = datetime.utcnow().isoformat()
        
        if self.use_redis:
            self._save_to_redis(session_id, session)
        else:
            self.sessions[session_id] = session
        
        return True
    
    def delete_session(self, session_id):
        """Delete session"""
        if self.use_redis:
            self.redis_client.delete(f'session:{session_id}')
        else:
            if session_id in self.sessions:
                del self.sessions[session_id]
        
        return True
    
    def validate_session(self, session_id):
        """Validate session and check expiration"""
        session = self.get_session(session_id)
        
        if not session:
            return False, 'Session not found'
        
        # Check expiration
        last_activity = datetime.fromisoformat(session['last_activity'])
        elapsed = (datetime.utcnow() - last_activity).total_seconds()
        
        if elapsed > self.session_timeout:
            self.delete_session(session_id)
            return False, 'Session expired'
        
        # Update last activity
        self.update_session(session_id, {'last_activity': datetime.utcnow().isoformat()})
        
        return True, session
    
    def get_user_sessions(self, user_id):
        """Get all sessions for a user"""
        sessions = []
        
        if self.use_redis:
            # Scan for user sessions in Redis
            for key in self.redis_client.scan_iter(match='session:*'):
                session = self._get_from_redis(key.decode().replace('session:', ''))
                if session and session.get('user_id') == user_id:
                    sessions.append(session)
        else:
            sessions = [
                session for session in self.sessions.values()
                if session.get('user_id') == user_id
            ]
        
        return sessions
    
    def revoke_user_sessions(self, user_id, except_session=None):
        """Revoke all sessions for a user"""
        user_sessions = self.get_user_sessions(user_id)
        
        revoked_count = 0
        for session in user_sessions:
            session_id = session['session_id']
            
            if except_session and session_id == except_session:
                continue
            
            self.delete_session(session_id)
            revoked_count += 1
        
        return revoked_count
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        cutoff = datetime.utcnow() - timedelta(seconds=self.session_timeout)
        removed_count = 0
        
        if self.use_redis:
            # Redis TTL handles expiration automatically
            return 0
        else:
            expired_sessions = []
            
            for session_id, session in self.sessions.items():
                last_activity = datetime.fromisoformat(session['last_activity'])
                
                if last_activity < cutoff:
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.sessions[session_id]
                removed_count += 1
        
        return removed_count
    
    def get_session_stats(self):
        """Get session statistics"""
        if self.use_redis:
            session_count = len(list(self.redis_client.scan_iter(match='session:*')))
        else:
            session_count = len(self.sessions)
        
        return {
            'total_sessions': session_count,
            'storage': 'redis' if self.use_redis else 'memory',
            'timeout': self.session_timeout
        }
    
    def _generate_session_id(self):
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    def _save_to_redis(self, session_id, session_data):
        """Save session to Redis"""
        key = f'session:{session_id}'
        value = json.dumps(session_data)
        
        self.redis_client.setex(
            key,
            self.session_timeout,
            value
        )
    
    def _get_from_redis(self, session_id):
        """Get session from Redis"""
        key = f'session:{session_id}'
        data = self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        
        return None


# Global session manager
session_manager = SessionManager()


class SecureSession:
    """Secure session wrapper with additional security features"""
    
    def __init__(self, session_id, session_manager):
        self.session_id = session_id
        self.session_manager = session_manager
        self._data = None
    
    @property
    def data(self):
        """Lazy load session data"""
        if self._data is None:
            valid, result = self.session_manager.validate_session(self.session_id)
            if valid:
                self._data = result
        return self._data
    
    def get(self, key, default=None):
        """Get value from session"""
        if self.data:
            return self.data.get(key, default)
        return default
    
    def set(self, key, value):
        """Set value in session"""
        if self.data:
            self.session_manager.update_session(self.session_id, {key: value})
            self._data = None  # Invalidate cache
            return True
        return False
    
    def delete(self):
        """Delete session"""
        return self.session_manager.delete_session(self.session_id)
    
    def is_valid(self):
        """Check if session is valid"""
        valid, _ = self.session_manager.validate_session(self.session_id)
        return valid


def require_session(func):
    """Decorator to require valid session"""
    from functools import wraps
    from flask import request, jsonify
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_id = request.cookies.get('session_id') or request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 401
        
        valid, result = session_manager.validate_session(session_id)
        
        if not valid:
            return jsonify({'error': result}), 401
        
        # Add session to request context
        request.session_data = result
        
        return func(*args, **kwargs)
    
    return wrapper


def create_session_token(user_id, user_data=None):
    """Create session and return token"""
    session_id = session_manager.create_session(user_id, user_data)
    
    # Create secure token
    token_data = {
        'session_id': session_id,
        'user_id': user_id,
        'issued_at': datetime.utcnow().isoformat()
    }
    
    token = secrets.token_urlsafe(32)
    
    # Store token mapping
    session_manager.update_session(session_id, {'token': token})
    
    return token


def verify_session_token(token):
    """Verify session token"""
    # In production, use JWT or similar
    # This is a simplified version
    
    for session in session_manager.sessions.values():
        if session.get('token') == token:
            return True, session
    
    return False, None


def get_current_session():
    """Get current session from Flask request context"""
    from flask import request
    
    return getattr(request, 'session_data', None)


# Initialize Redis if available
def init_session_manager(redis_url=None):
    """Initialize session manager"""
    import os
    
    redis_url = redis_url or os.environ.get('REDIS_URL')
    
    if redis_url:
        session_manager.configure_redis(redis_url)
    
    return session_manager
