"""
Blockchain Monitoring Service
Real-time monitoring and alerting for blockchain operations
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Callable
from collections import deque
import json

logger = logging.getLogger(__name__)


class BlockchainMonitor:
    """Monitor blockchain events and transactions"""
    
    def __init__(self, web3_backend, max_history=1000):
        self.web3 = web3_backend
        self.max_history = max_history
        self.event_history = deque(maxlen=max_history)
        self.listeners = {}
        self.is_running = False
        self.alerts = []
        
    async def start_monitoring(self):
        """Start monitoring blockchain events"""
        self.is_running = True
        logger.info("Blockchain monitoring started")
        
        # Start monitoring tasks
        await asyncio.gather(
            self.monitor_new_blocks(),
            self.monitor_gas_prices(),
            self.monitor_passport_events()
        )
    
    async def monitor_new_blocks(self):
        """Monitor new blocks"""
        logger.info("Monitoring new blocks...")
        
        last_block = 0
        
        while self.is_running:
            try:
                if not self.web3.w3:
                    await asyncio.sleep(5)
                    continue
                
                current_block = self.web3.w3.eth.block_number
                
                if current_block > last_block:
                    block = self.web3.w3.eth.get_block(current_block)
                    
                    event_data = {
                        'type': 'new_block',
                        'block_number': current_block,
                        'timestamp': datetime.fromtimestamp(block.timestamp),
                        'transactions': len(block.transactions),
                        'gas_used': block.gasUsed,
                        'gas_limit': block.gasLimit
                    }
                    
                    self.add_event(event_data)
                    await self.trigger_listeners('new_block', event_data)
                    
                    last_block = current_block
                
                await asyncio.sleep(3)  # Check every 3 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring blocks: {e}")
                await asyncio.sleep(5)
    
    async def monitor_gas_prices(self):
        """Monitor gas price changes"""
        logger.info("Monitoring gas prices...")
        
        last_gas_price = 0
        threshold_change = 0.1  # 10% change threshold
        
        while self.is_running:
            try:
                if not self.web3.w3:
                    await asyncio.sleep(10)
                    continue
                
                gas_price = self.web3.w3.eth.gas_price
                gas_price_gwei = self.web3.w3.from_wei(gas_price, 'gwei')
                
                if last_gas_price > 0:
                    change_percent = abs(gas_price - last_gas_price) / last_gas_price
                    
                    if change_percent > threshold_change:
                        event_data = {
                            'type': 'gas_price_change',
                            'timestamp': datetime.now(),
                            'old_price': float(self.web3.w3.from_wei(last_gas_price, 'gwei')),
                            'new_price': float(gas_price_gwei),
                            'change_percent': change_percent * 100
                        }
                        
                        self.add_event(event_data)
                        await self.trigger_listeners('gas_price_change', event_data)
                        
                        # Create alert if gas price is high
                        if gas_price_gwei > 50:
                            self.create_alert(
                                'high_gas_price',
                                f'Gas price is high: {gas_price_gwei:.2f} Gwei',
                                'warning'
                            )
                
                last_gas_price = gas_price
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring gas prices: {e}")
                await asyncio.sleep(30)
    
    async def monitor_passport_events(self):
        """Monitor passport contract events"""
        logger.info("Monitoring passport events...")
        
        while self.is_running:
            try:
                if not self.web3.contract:
                    await asyncio.sleep(10)
                    continue
                
                # Get recent events
                # This is a simplified version - in production use event filters
                current_block = self.web3.w3.eth.block_number
                from_block = max(0, current_block - 100)
                
                # Monitor PassportStored events
                stored_events = self.web3.contract.events.PassportStored.get_logs(
                    fromBlock=from_block,
                    toBlock='latest'
                )
                
                for event in stored_events:
                    event_data = {
                        'type': 'passport_stored',
                        'timestamp': datetime.now(),
                        'passport_id': event.args.passportId,
                        'owner': event.args.owner,
                        'block_number': event.blockNumber,
                        'transaction_hash': event.transactionHash.hex()
                    }
                    
                    self.add_event(event_data)
                    await self.trigger_listeners('passport_stored', event_data)
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring passport events: {e}")
                await asyncio.sleep(15)
    
    def add_event(self, event_data):
        """Add event to history"""
        self.event_history.append(event_data)
        logger.debug(f"Event recorded: {event_data['type']}")
    
    def add_listener(self, event_type: str, callback: Callable):
        """Add event listener"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(callback)
        logger.info(f"Listener added for: {event_type}")
    
    async def trigger_listeners(self, event_type: str, event_data: Dict):
        """Trigger all listeners for an event type"""
        if event_type in self.listeners:
            for callback in self.listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event_data)
                    else:
                        callback(event_data)
                except Exception as e:
                    logger.error(f"Error in listener callback: {e}")
    
    def create_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Create monitoring alert"""
        alert = {
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(),
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        logger.warning(f"Alert created: {message}")
    
    def get_recent_events(self, limit: int = 100, event_type: str = None):
        """Get recent events"""
        events = list(self.event_history)
        
        if event_type:
            events = [e for e in events if e['type'] == event_type]
        
        return events[-limit:]
    
    def get_statistics(self):
        """Get monitoring statistics"""
        total_events = len(self.event_history)
        event_types = {}
        
        for event in self.event_history:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'total_events': total_events,
            'event_types': event_types,
            'active_listeners': sum(len(listeners) for listeners in self.listeners.values()),
            'total_alerts': len(self.alerts),
            'unacknowledged_alerts': len([a for a in self.alerts if not a['acknowledged']]),
            'is_running': self.is_running
        }
    
    def get_alerts(self, acknowledged: bool = None):
        """Get alerts"""
        if acknowledged is None:
            return self.alerts
        
        return [a for a in self.alerts if a['acknowledged'] == acknowledged]
    
    def acknowledge_alert(self, alert_index: int):
        """Acknowledge alert"""
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index]['acknowledged'] = True
            return True
        return False
    
    def clear_alerts(self):
        """Clear acknowledged alerts"""
        self.alerts = [a for a in self.alerts if not a['acknowledged']]
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_running = False
        logger.info("Blockchain monitoring stopped")
    
    def export_events(self, filename: str, event_type: str = None):
        """Export events to JSON file"""
        events = self.get_recent_events(event_type=event_type)
        
        # Convert datetime objects to strings
        serializable_events = []
        for event in events:
            event_copy = event.copy()
            if 'timestamp' in event_copy:
                event_copy['timestamp'] = event_copy['timestamp'].isoformat()
            serializable_events.append(event_copy)
        
        try:
            with open(filename, 'w') as f:
                json.dump(serializable_events, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error exporting events: {e}")
            return False


class PerformanceMonitor:
    """Monitor blockchain performance metrics"""
    
    def __init__(self, web3_backend):
        self.web3 = web3_backend
        self.metrics = {
            'block_times': deque(maxlen=100),
            'gas_prices': deque(maxlen=100),
            'transaction_counts': deque(maxlen=100)
        }
    
    async def collect_metrics(self):
        """Collect performance metrics"""
        try:
            if not self.web3.w3:
                return
            
            current_block = self.web3.w3.eth.block_number
            block = self.web3.w3.eth.get_block(current_block)
            
            if len(self.metrics['block_times']) > 0:
                last_block = self.web3.w3.eth.get_block(current_block - 1)
                block_time = block.timestamp - last_block.timestamp
                self.metrics['block_times'].append(block_time)
            
            gas_price = self.web3.w3.eth.gas_price
            self.metrics['gas_prices'].append(gas_price)
            
            self.metrics['transaction_counts'].append(len(block.transactions))
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def get_average_block_time(self):
        """Get average block time"""
        if not self.metrics['block_times']:
            return None
        return sum(self.metrics['block_times']) / len(self.metrics['block_times'])
    
    def get_average_gas_price(self):
        """Get average gas price"""
        if not self.metrics['gas_prices']:
            return None
        avg_wei = sum(self.metrics['gas_prices']) / len(self.metrics['gas_prices'])
        return self.web3.w3.from_wei(avg_wei, 'gwei')
    
    def get_average_tx_per_block(self):
        """Get average transactions per block"""
        if not self.metrics['transaction_counts']:
            return None
        return sum(self.metrics['transaction_counts']) / len(self.metrics['transaction_counts'])


# Global monitor instance
blockchain_monitor = None


def init_monitoring(web3_backend):
    """Initialize blockchain monitoring"""
    global blockchain_monitor
    blockchain_monitor = BlockchainMonitor(web3_backend)
    return blockchain_monitor
