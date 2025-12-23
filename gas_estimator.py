"""
Blockchain gas estimator for PassportApp
Estimate and optimize gas costs for transactions
"""

from datetime import datetime
import statistics


class GasEstimator:
    """Estimate gas costs for blockchain transactions"""
    
    def __init__(self):
        self.gas_history = []
        self.base_costs = {
            'transfer': 21000,
            'erc20_transfer': 65000,
            'erc721_transfer': 85000,
            'erc721_mint': 120000,
            'contract_deploy': 200000,
            'marketplace_list': 100000,
            'marketplace_buy': 150000
        }
        
        self.priority_multipliers = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.2,
            'urgent': 1.5
        }
    
    def estimate_gas(self, transaction_type, priority='medium'):
        """Estimate gas for transaction type"""
        base_gas = self.base_costs.get(transaction_type, 21000)
        multiplier = self.priority_multipliers.get(priority, 1.0)
        
        estimated_gas = int(base_gas * multiplier)
        
        return {
            'transaction_type': transaction_type,
            'base_gas': base_gas,
            'priority': priority,
            'estimated_gas': estimated_gas,
            'estimated_gwei': self.get_current_gas_price(priority),
            'estimated_cost_eth': self.calculate_cost_eth(estimated_gas, priority)
        }
    
    def get_current_gas_price(self, priority='medium'):
        """Get current gas price in Gwei"""
        # In production, fetch from network
        # This is a simplified version
        
        base_price = self._get_network_gas_price()
        
        multiplier = self.priority_multipliers.get(priority, 1.0)
        
        return int(base_price * multiplier)
    
    def calculate_cost_eth(self, gas_limit, priority='medium'):
        """Calculate cost in ETH"""
        gas_price_gwei = self.get_current_gas_price(priority)
        
        # Convert Gwei to ETH
        gas_price_eth = gas_price_gwei / 1e9
        
        cost_eth = gas_limit * gas_price_eth
        
        return cost_eth
    
    def calculate_cost_usd(self, gas_limit, priority='medium', eth_price_usd=2000):
        """Calculate cost in USD"""
        cost_eth = self.calculate_cost_eth(gas_limit, priority)
        cost_usd = cost_eth * eth_price_usd
        
        return cost_usd
    
    def optimize_gas(self, transaction_type):
        """Get gas optimization suggestions"""
        suggestions = []
        
        if transaction_type == 'erc721_mint':
            suggestions.extend([
                'Batch mint multiple NFTs in one transaction',
                'Use lazy minting to defer gas costs',
                'Optimize metadata storage on IPFS',
                'Consider using ERC721A for batch minting'
            ])
        
        elif transaction_type == 'marketplace_buy':
            suggestions.extend([
                'Bundle multiple purchases in one transaction',
                'Use off-chain signatures for approvals',
                'Optimize contract storage reads'
            ])
        
        elif transaction_type == 'contract_deploy':
            suggestions.extend([
                'Optimize contract code',
                'Remove unused functions',
                'Use proxy patterns for upgradeability',
                'Deploy on L2 networks for lower costs'
            ])
        
        return suggestions
    
    def record_transaction(self, tx_hash, gas_used, gas_price, tx_type):
        """Record transaction for gas analytics"""
        record = {
            'tx_hash': tx_hash,
            'gas_used': gas_used,
            'gas_price': gas_price,
            'tx_type': tx_type,
            'timestamp': datetime.utcnow().isoformat(),
            'cost_eth': (gas_used * gas_price) / 1e18
        }
        
        self.gas_history.append(record)
        
        # Keep only last 1000 records
        if len(self.gas_history) > 1000:
            self.gas_history = self.gas_history[-1000:]
        
        return record
    
    def get_gas_analytics(self, tx_type=None):
        """Get gas usage analytics"""
        if tx_type:
            records = [r for r in self.gas_history if r['tx_type'] == tx_type]
        else:
            records = self.gas_history
        
        if not records:
            return None
        
        gas_used_values = [r['gas_used'] for r in records]
        cost_values = [r['cost_eth'] for r in records]
        
        return {
            'transaction_type': tx_type or 'all',
            'count': len(records),
            'gas_used': {
                'min': min(gas_used_values),
                'max': max(gas_used_values),
                'avg': statistics.mean(gas_used_values),
                'median': statistics.median(gas_used_values)
            },
            'cost_eth': {
                'min': min(cost_values),
                'max': max(cost_values),
                'avg': statistics.mean(cost_values),
                'median': statistics.median(cost_values),
                'total': sum(cost_values)
            }
        }
    
    def compare_networks(self, transaction_type, gas_limit):
        """Compare gas costs across different networks"""
        networks = {
            'ethereum': {'name': 'Ethereum Mainnet', 'base_gwei': 50, 'eth_price': 2000},
            'polygon': {'name': 'Polygon', 'base_gwei': 30, 'eth_price': 0.5},
            'optimism': {'name': 'Optimism', 'base_gwei': 0.001, 'eth_price': 2000},
            'arbitrum': {'name': 'Arbitrum', 'base_gwei': 0.1, 'eth_price': 2000},
            'bsc': {'name': 'BSC', 'base_gwei': 5, 'eth_price': 300}
        }
        
        comparisons = []
        
        for network_id, network_info in networks.items():
            gas_price_gwei = network_info['base_gwei']
            eth_price = network_info['eth_price']
            
            cost_eth = (gas_limit * gas_price_gwei) / 1e9
            cost_usd = cost_eth * eth_price
            
            comparisons.append({
                'network': network_info['name'],
                'network_id': network_id,
                'gas_price_gwei': gas_price_gwei,
                'cost_eth': cost_eth,
                'cost_usd': cost_usd
            })
        
        # Sort by cost USD
        comparisons.sort(key=lambda x: x['cost_usd'])
        
        return {
            'transaction_type': transaction_type,
            'gas_limit': gas_limit,
            'networks': comparisons
        }
    
    def estimate_eip1559_fee(self, priority='medium'):
        """Estimate EIP-1559 gas fee"""
        base_fee = self._get_base_fee()
        
        priority_fees = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'urgent': 5
        }
        
        priority_fee = priority_fees.get(priority, 2)
        max_fee = base_fee + (priority_fee * 2)
        
        return {
            'base_fee': base_fee,
            'priority_fee': priority_fee,
            'max_fee_per_gas': max_fee,
            'max_priority_fee_per_gas': priority_fee
        }
    
    def _get_network_gas_price(self):
        """Get current network gas price (mock)"""
        # In production, fetch from Web3 provider
        # This is a simplified version
        
        if self.gas_history:
            recent_prices = [r['gas_price'] for r in self.gas_history[-10:]]
            return int(statistics.mean(recent_prices))
        
        return 50  # Default 50 Gwei
    
    def _get_base_fee(self):
        """Get EIP-1559 base fee (mock)"""
        # In production, fetch from Web3 provider
        return 30  # Default 30 Gwei


# Global gas estimator
gas_estimator = GasEstimator()


def estimate_transaction_cost(tx_type, priority='medium'):
    """Estimate transaction cost"""
    return gas_estimator.estimate_gas(tx_type, priority)


def get_gas_recommendations(tx_type):
    """Get gas optimization recommendations"""
    estimate = gas_estimator.estimate_gas(tx_type, 'medium')
    suggestions = gas_estimator.optimize_gas(tx_type)
    
    return {
        'estimate': estimate,
        'optimization_suggestions': suggestions,
        'network_comparison': gas_estimator.compare_networks(
            tx_type,
            estimate['estimated_gas']
        )
    }


class GasTracker:
    """Track gas prices over time"""
    
    def __init__(self):
        self.price_history = []
    
    def record_gas_price(self, gas_price_gwei):
        """Record current gas price"""
        record = {
            'price_gwei': gas_price_gwei,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.price_history.append(record)
        
        # Keep only last 1000 records
        if len(self.price_history) > 1000:
            self.price_history = self.price_history[-1000:]
    
    def get_price_trend(self, hours=24):
        """Get gas price trend"""
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent = [
            r for r in self.price_history
            if datetime.fromisoformat(r['timestamp']) > cutoff
        ]
        
        if not recent:
            return None
        
        prices = [r['price_gwei'] for r in recent]
        
        return {
            'period_hours': hours,
            'samples': len(recent),
            'min': min(prices),
            'max': max(prices),
            'avg': statistics.mean(prices),
            'median': statistics.median(prices),
            'current': prices[-1] if prices else None
        }
    
    def get_best_time(self):
        """Get recommended time for transaction"""
        trend = self.get_price_trend(24)
        
        if not trend:
            return 'Insufficient data'
        
        current = trend['current']
        avg = trend['avg']
        
        if current < avg * 0.8:
            return 'Now - gas prices are low'
        elif current > avg * 1.2:
            return 'Wait - gas prices are high'
        else:
            return 'Moderate - acceptable time to transact'


# Global gas tracker
gas_tracker = GasTracker()
