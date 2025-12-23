"""
WebSocket handler for real-time notifications in PassportApp
Enable real-time updates for blockchain events and system notifications
"""

from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from functools import wraps
from datetime import datetime
import json


socketio = SocketIO(cors_allowed_origins="*")


class WebSocketManager:
    """Manage WebSocket connections and rooms"""
    
    def __init__(self):
        self.active_connections = {}
        self.user_rooms = {}
    
    def add_connection(self, sid, user_id=None):
        """Add new connection"""
        self.active_connections[sid] = {
            'user_id': user_id,
            'connected_at': datetime.utcnow().isoformat(),
            'rooms': []
        }
    
    def remove_connection(self, sid):
        """Remove connection"""
        if sid in self.active_connections:
            del self.active_connections[sid]
    
    def get_connection_count(self):
        """Get total active connections"""
        return len(self.active_connections)
    
    def get_user_connections(self, user_id):
        """Get all connections for a user"""
        return [
            sid for sid, data in self.active_connections.items()
            if data.get('user_id') == user_id
        ]


# Global WebSocket manager
ws_manager = WebSocketManager()


def authenticated_only(f):
    """Decorator to require authentication for WebSocket events"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Check if user is authenticated
        # Implement your auth check here
        return f(*args, **kwargs)
    return wrapped


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    from flask import request
    
    sid = request.sid
    user_id = request.args.get('user_id')
    
    ws_manager.add_connection(sid, user_id)
    
    emit('connected', {
        'message': 'Connected to PassportApp WebSocket',
        'timestamp': datetime.utcnow().isoformat()
    })
    
    print(f'Client connected: {sid}, User: {user_id}')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    from flask import request
    
    sid = request.sid
    ws_manager.remove_connection(sid)
    
    print(f'Client disconnected: {sid}')


@socketio.on('join')
def handle_join(data):
    """Join a room for specific updates"""
    room = data.get('room')
    
    if room:
        join_room(room)
        emit('joined', {'room': room, 'timestamp': datetime.utcnow().isoformat()})
        print(f'Client joined room: {room}')


@socketio.on('leave')
def handle_leave(data):
    """Leave a room"""
    room = data.get('room')
    
    if room:
        leave_room(room)
        emit('left', {'room': room, 'timestamp': datetime.utcnow().isoformat()})
        print(f'Client left room: {room}')


@socketio.on('subscribe_passport')
def handle_subscribe_passport(data):
    """Subscribe to passport updates"""
    passport_id = data.get('passport_id')
    
    if passport_id:
        room = f'passport_{passport_id}'
        join_room(room)
        emit('subscribed', {
            'type': 'passport',
            'passport_id': passport_id,
            'timestamp': datetime.utcnow().isoformat()
        })


@socketio.on('subscribe_nft')
def handle_subscribe_nft(data):
    """Subscribe to NFT updates"""
    token_id = data.get('token_id')
    
    if token_id:
        room = f'nft_{token_id}'
        join_room(room)
        emit('subscribed', {
            'type': 'nft',
            'token_id': token_id,
            'timestamp': datetime.utcnow().isoformat()
        })


@socketio.on('subscribe_wallet')
def handle_subscribe_wallet(data):
    """Subscribe to wallet updates"""
    wallet_address = data.get('wallet_address')
    
    if wallet_address:
        room = f'wallet_{wallet_address}'
        join_room(room)
        emit('subscribed', {
            'type': 'wallet',
            'wallet_address': wallet_address,
            'timestamp': datetime.utcnow().isoformat()
        })


def notify_passport_update(passport_id, update_type, data):
    """Notify subscribers about passport updates"""
    room = f'passport_{passport_id}'
    socketio.emit('passport_update', {
        'passport_id': passport_id,
        'update_type': update_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)


def notify_nft_update(token_id, update_type, data):
    """Notify subscribers about NFT updates"""
    room = f'nft_{token_id}'
    socketio.emit('nft_update', {
        'token_id': token_id,
        'update_type': update_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)


def notify_transaction_status(tx_hash, status, data=None):
    """Notify about transaction status"""
    socketio.emit('transaction_status', {
        'tx_hash': tx_hash,
        'status': status,
        'data': data or {},
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)


def notify_blockchain_event(event_type, event_data):
    """Notify about blockchain events"""
    socketio.emit('blockchain_event', {
        'event': event_type,
        'data': event_data,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)


def notify_marketplace_update(listing_id, update_type, data):
    """Notify about marketplace updates"""
    socketio.emit('marketplace_update', {
        'listing_id': listing_id,
        'update_type': update_type,
        'data': data,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)


def notify_user(user_id, notification_type, message, data=None):
    """Send notification to specific user"""
    connections = ws_manager.get_user_connections(user_id)
    
    for sid in connections:
        socketio.emit('notification', {
            'type': notification_type,
            'message': message,
            'data': data or {},
            'timestamp': datetime.utcnow().isoformat()
        }, room=sid)


def broadcast_system_message(message, level='info'):
    """Broadcast system message to all connected clients"""
    socketio.emit('system_message', {
        'message': message,
        'level': level,
        'timestamp': datetime.utcnow().isoformat()
    }, broadcast=True)


def get_connection_stats():
    """Get WebSocket connection statistics"""
    return {
        'active_connections': ws_manager.get_connection_count(),
        'timestamp': datetime.utcnow().isoformat()
    }


def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    return socketio
