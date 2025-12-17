"""
Blockchain Analytics for PassportApp
Track and analyze blockchain transactions and passport data
"""

from datetime import datetime, timedelta
from collections import defaultdict
import json


class BlockchainAnalytics:
    """Analytics for blockchain passport operations"""
    
    def __init__(self, web3_backend):
        self.web3 = web3_backend
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
    
    def get_passport_statistics(self, owner_address):
        """Get statistics for a passport owner"""
        cache_key = f"stats_{owner_address}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        stats = {
            'total_passports': 0,
            'active_passports': 0,
            'inactive_passports': 0,
            'total_gas_used': 0,
            'total_transactions': 0,
            'first_passport_date': None,
            'last_activity_date': None,
            'passports': []
        }
        
        try:
            passport_ids = self.web3.get_owner_passports(owner_address)
            stats['total_passports'] = len(passport_ids)
            
            for pid in passport_ids:
                passport = self.web3.get_passport(pid)
                
                if passport['is_active']:
                    stats['active_passports'] += 1
                else:
                    stats['inactive_passports'] += 1
                
                passport_date = datetime.fromtimestamp(passport['timestamp'])
                
                if not stats['first_passport_date'] or passport_date < stats['first_passport_date']:
                    stats['first_passport_date'] = passport_date
                
                if not stats['last_activity_date'] or passport_date > stats['last_activity_date']:
                    stats['last_activity_date'] = passport_date
                
                stats['passports'].append({
                    'id': pid,
                    'passport_number': passport['passport_number'],
                    'created_at': passport_date.isoformat(),
                    'is_active': passport['is_active']
                })
            
            # Convert datetime to string for JSON serialization
            if stats['first_passport_date']:
                stats['first_passport_date'] = stats['first_passport_date'].isoformat()
            if stats['last_activity_date']:
                stats['last_activity_date'] = stats['last_activity_date'].isoformat()
            
            # Cache the results
            self.cache[cache_key] = (stats, datetime.now())
            
            return stats
        
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return stats
    
    def get_network_statistics(self):
        """Get overall network statistics"""
        if not self.web3.w3:
            return None
        
        cache_key = "network_stats"
        
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        stats = {
            'block_number': self.web3.w3.eth.block_number,
            'chain_id': self.web3.w3.eth.chain_id,
            'gas_price': str(self.web3.w3.eth.gas_price),
            'gas_price_gwei': self.web3.w3.from_wei(self.web3.w3.eth.gas_price, 'gwei'),
            'is_syncing': self.web3.w3.eth.syncing,
            'peer_count': self.web3.w3.net.peer_count if hasattr(self.web3.w3.net, 'peer_count') else 0
        }
        
        self.cache[cache_key] = (stats, datetime.now())
        return stats
    
    def get_transaction_history(self, address, limit=20):
        """Get transaction history for an address"""
        # This is a simplified version
        # In production, you'd use an indexer or query events
        
        history = {
            'address': address,
            'transactions': [],
            'total_sent': 0,
            'total_received': 0
        }
        
        try:
            # Get recent blocks to scan for transactions
            current_block = self.web3.w3.eth.block_number
            start_block = max(0, current_block - 1000)  # Last 1000 blocks
            
            for block_num in range(current_block, start_block, -1):
                if len(history['transactions']) >= limit:
                    break
                
                block = self.web3.w3.eth.get_block(block_num, full_transactions=True)
                
                for tx in block.transactions:
                    if tx['from'] == address or tx['to'] == address:
                        tx_data = {
                            'hash': tx['hash'].hex(),
                            'from': tx['from'],
                            'to': tx['to'],
                            'value': str(tx['value']),
                            'value_ether': float(self.web3.w3.from_wei(tx['value'], 'ether')),
                            'block_number': block_num,
                            'timestamp': datetime.fromtimestamp(block['timestamp']).isoformat(),
                            'gas_used': tx.get('gas', 0),
                            'type': 'sent' if tx['from'] == address else 'received'
                        }
                        
                        history['transactions'].append(tx_data)
                        
                        if tx['from'] == address:
                            history['total_sent'] += tx_data['value_ether']
                        else:
                            history['total_received'] += tx_data['value_ether']
                        
                        if len(history['transactions']) >= limit:
                            break
            
            return history
        
        except Exception as e:
            print(f"Error getting transaction history: {e}")
            return history
    
    def analyze_gas_usage(self, owner_address):
        """Analyze gas usage patterns"""
        analysis = {
            'total_gas_used': 0,
            'average_gas_per_tx': 0,
            'total_cost_ether': 0,
            'transactions_by_type': defaultdict(int),
            'gas_by_type': defaultdict(int)
        }
        
        # This would require event logs or transaction history
        # Simplified version
        
        return analysis
    
    def get_passport_timeline(self, passport_id):
        """Get timeline of events for a passport"""
        timeline = []
        
        try:
            passport = self.web3.get_passport(passport_id)
            
            timeline.append({
                'event': 'Created',
                'timestamp': datetime.fromtimestamp(passport['timestamp']).isoformat(),
                'details': f"Passport {passport['passport_number']} created"
            })
            
            # In production, query blockchain events for updates
            
            return {
                'passport_id': passport_id,
                'timeline': timeline
            }
        
        except Exception as e:
            print(f"Error getting timeline: {e}")
            return {'passport_id': passport_id, 'timeline': []}
    
    def generate_report(self, owner_address):
        """Generate comprehensive analytics report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'owner': owner_address,
            'passport_stats': self.get_passport_statistics(owner_address),
            'network_stats': self.get_network_statistics(),
            'balance': self.web3.get_balance(owner_address) if self.web3.w3 else None
        }
        
        return report
    
    def export_to_json(self, data, filename):
        """Export analytics data to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def get_performance_metrics(self):
        """Get blockchain performance metrics"""
        metrics = {
            'cache_size': len(self.cache),
            'cached_items': list(self.cache.keys()),
            'web3_connected': self.web3.w3.is_connected() if self.web3.w3 else False,
            'contract_loaded': self.web3.contract is not None
        }
        
        return metrics
    
    def clear_cache(self):
        """Clear analytics cache"""
        self.cache.clear()
        return True


def create_analytics_dashboard_data(web3_backend, owner_address):
    """Create data structure for analytics dashboard"""
    analytics = BlockchainAnalytics(web3_backend)
    
    dashboard_data = {
        'summary': analytics.get_passport_statistics(owner_address),
        'network': analytics.get_network_statistics(),
        'performance': analytics.get_performance_metrics()
    }
    
    return dashboard_data
