"""
Webhook delivery system for PassportApp
Send HTTP webhooks for events with retry logic
"""

import requests
import json
from datetime import datetime, timedelta
import time
import hmac
import hashlib
from threading import Thread
import queue


class WebhookEvent:
    """Webhook event types"""
    PASSPORT_CREATED = 'passport.created'
    PASSPORT_UPDATED = 'passport.updated'
    PASSPORT_DELETED = 'passport.deleted'
    NFT_MINTED = 'nft.minted'
    NFT_TRANSFERRED = 'nft.transferred'
    NFT_LISTED = 'nft.listed'
    NFT_SOLD = 'nft.sold'
    TRANSACTION_CONFIRMED = 'transaction.confirmed'
    TRANSACTION_FAILED = 'transaction.failed'
    USER_REGISTERED = 'user.registered'
    USER_UPDATED = 'user.updated'


class WebhookDelivery:
    """Single webhook delivery attempt"""
    
    def __init__(self, webhook_id, url, event, payload, secret=None):
        self.webhook_id = webhook_id
        self.url = url
        self.event = event
        self.payload = payload
        self.secret = secret
        self.attempts = 0
        self.max_attempts = 5
        self.last_attempt = None
        self.status = 'pending'
        self.response_code = None
        self.response_body = None
        self.created_at = datetime.utcnow()
    
    def generate_signature(self, payload_str):
        """Generate HMAC signature for payload"""
        if not self.secret:
            return None
        
        signature = hmac.new(
            self.secret.encode('utf-8'),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def send(self, timeout=30):
        """Send webhook request"""
        self.attempts += 1
        self.last_attempt = datetime.utcnow()
        
        # Prepare payload
        webhook_payload = {
            'event': self.event,
            'timestamp': datetime.utcnow().isoformat(),
            'webhook_id': self.webhook_id,
            'data': self.payload
        }
        
        payload_str = json.dumps(webhook_payload)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'PassportApp-Webhook/1.0',
            'X-Webhook-Event': self.event,
            'X-Webhook-ID': str(self.webhook_id),
            'X-Webhook-Attempt': str(self.attempts)
        }
        
        # Add signature if secret provided
        if self.secret:
            signature = self.generate_signature(payload_str)
            headers['X-Webhook-Signature'] = f'sha256={signature}'
        
        try:
            response = requests.post(
                self.url,
                data=payload_str,
                headers=headers,
                timeout=timeout
            )
            
            self.response_code = response.status_code
            self.response_body = response.text[:1000]  # Limit stored response
            
            if 200 <= response.status_code < 300:
                self.status = 'delivered'
                return True
            else:
                self.status = 'failed'
                return False
        
        except requests.exceptions.Timeout:
            self.status = 'timeout'
            self.response_body = 'Request timeout'
            return False
        
        except requests.exceptions.ConnectionError:
            self.status = 'connection_error'
            self.response_body = 'Connection error'
            return False
        
        except Exception as e:
            self.status = 'error'
            self.response_body = str(e)
            return False
    
    def should_retry(self):
        """Check if delivery should be retried"""
        if self.status == 'delivered':
            return False
        
        if self.attempts >= self.max_attempts:
            return False
        
        return True
    
    def get_retry_delay(self):
        """Get delay before next retry (exponential backoff)"""
        if self.attempts == 0:
            return 0
        
        # Exponential backoff: 1, 2, 4, 8, 16 seconds
        return min(2 ** (self.attempts - 1), 60)


class WebhookQueue:
    """Queue for webhook deliveries"""
    
    def __init__(self, num_workers=4):
        self.queue = queue.Queue()
        self.workers = []
        self.num_workers = num_workers
        self.running = False
    
    def start(self):
        """Start worker threads"""
        self.running = True
        
        for i in range(self.num_workers):
            worker = Thread(target=self._worker, name=f'WebhookWorker-{i}')
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """Stop worker threads"""
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
    
    def _worker(self):
        """Worker thread for processing webhooks"""
        while self.running:
            try:
                delivery = self.queue.get(timeout=1)
                
                # Send webhook
                success = delivery.send()
                
                # Retry if needed
                if not success and delivery.should_retry():
                    retry_delay = delivery.get_retry_delay()
                    time.sleep(retry_delay)
                    self.queue.put(delivery)
                
                self.queue.task_done()
            
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in webhook worker: {e}")
    
    def enqueue(self, delivery):
        """Add delivery to queue"""
        self.queue.put(delivery)
    
    def get_queue_size(self):
        """Get current queue size"""
        return self.queue.qsize()


class WebhookManager:
    """Manage webhook subscriptions and deliveries"""
    
    def __init__(self):
        self.subscriptions = {}
        self.delivery_queue = WebhookQueue()
        self.delivery_history = []
        self.max_history = 1000
    
    def start(self):
        """Start webhook delivery"""
        self.delivery_queue.start()
    
    def stop(self):
        """Stop webhook delivery"""
        self.delivery_queue.stop()
    
    def subscribe(self, webhook_id, url, events, secret=None):
        """Subscribe to webhook events"""
        self.subscriptions[webhook_id] = {
            'url': url,
            'events': events if isinstance(events, list) else [events],
            'secret': secret,
            'created_at': datetime.utcnow(),
            'active': True
        }
    
    def unsubscribe(self, webhook_id):
        """Unsubscribe from webhooks"""
        if webhook_id in self.subscriptions:
            self.subscriptions[webhook_id]['active'] = False
            return True
        return False
    
    def trigger_event(self, event, payload):
        """Trigger webhook event"""
        # Find subscriptions for this event
        for webhook_id, subscription in self.subscriptions.items():
            if not subscription['active']:
                continue
            
            if event not in subscription['events']:
                continue
            
            # Create delivery
            delivery = WebhookDelivery(
                webhook_id=webhook_id,
                url=subscription['url'],
                event=event,
                payload=payload,
                secret=subscription.get('secret')
            )
            
            # Enqueue delivery
            self.delivery_queue.enqueue(delivery)
            
            # Add to history
            self._add_to_history(delivery)
    
    def _add_to_history(self, delivery):
        """Add delivery to history"""
        self.delivery_history.append(delivery)
        
        # Trim history if too large
        if len(self.delivery_history) > self.max_history:
            self.delivery_history = self.delivery_history[-self.max_history:]
    
    def get_delivery_stats(self):
        """Get webhook delivery statistics"""
        total = len(self.delivery_history)
        
        if total == 0:
            return {
                'total': 0,
                'delivered': 0,
                'failed': 0,
                'pending': 0,
                'success_rate': 0
            }
        
        delivered = sum(1 for d in self.delivery_history if d.status == 'delivered')
        failed = sum(1 for d in self.delivery_history if d.status == 'failed')
        pending = sum(1 for d in self.delivery_history if d.status == 'pending')
        
        return {
            'total': total,
            'delivered': delivered,
            'failed': failed,
            'pending': pending,
            'success_rate': (delivered / total * 100) if total > 0 else 0
        }
    
    def get_subscription_stats(self, webhook_id):
        """Get statistics for a subscription"""
        deliveries = [d for d in self.delivery_history if d.webhook_id == webhook_id]
        
        if not deliveries:
            return {
                'total': 0,
                'delivered': 0,
                'failed': 0,
                'avg_attempts': 0
            }
        
        delivered = sum(1 for d in deliveries if d.status == 'delivered')
        failed = sum(1 for d in deliveries if d.status == 'failed')
        avg_attempts = sum(d.attempts for d in deliveries) / len(deliveries)
        
        return {
            'total': len(deliveries),
            'delivered': delivered,
            'failed': failed,
            'avg_attempts': avg_attempts
        }
    
    def get_recent_deliveries(self, webhook_id=None, limit=100):
        """Get recent webhook deliveries"""
        deliveries = self.delivery_history
        
        if webhook_id:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]
        
        # Sort by created_at descending
        deliveries.sort(key=lambda d: d.created_at, reverse=True)
        
        return deliveries[:limit]


# Global webhook manager
webhook_manager = WebhookManager()


def init_webhooks():
    """Initialize webhook system"""
    webhook_manager.start()
    return webhook_manager


def send_webhook(event, data):
    """Send webhook for event"""
    webhook_manager.trigger_event(event, data)


# Example webhook triggers
def trigger_passport_created(passport_data):
    """Trigger passport created webhook"""
    send_webhook(WebhookEvent.PASSPORT_CREATED, passport_data)


def trigger_nft_minted(nft_data):
    """Trigger NFT minted webhook"""
    send_webhook(WebhookEvent.NFT_MINTED, nft_data)


def trigger_nft_sold(sale_data):
    """Trigger NFT sold webhook"""
    send_webhook(WebhookEvent.NFT_SOLD, sale_data)


def trigger_transaction_confirmed(tx_data):
    """Trigger transaction confirmed webhook"""
    send_webhook(WebhookEvent.TRANSACTION_CONFIRMED, tx_data)
