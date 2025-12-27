"""
Web3 Backend for PassportApp
Handles blockchain interactions
"""

from web3 import Web3
from eth_account import Account
import json
import os
from web3_config import WEB3_PROVIDER_URI, PRIVATE_KEY, CONTRACT_ADDRESS, DEFAULT_GAS_LIMIT

class Web3Backend:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))
        self.account = None
        self.contract = None
        
        if PRIVATE_KEY:
            self.account = Account.from_key(PRIVATE_KEY)
    
    def is_connected(self):
        """Check if connected to Web3 provider"""
        return self.w3.is_connected()
    
    def get_balance(self, address):
        """Get ETH balance of address"""
        balance_wei = self.w3.eth.get_balance(address)
        return self.w3.from_wei(balance_wei, 'ether')
    
    def get_transaction_count(self, address):
        """Get transaction count (nonce)"""
        return self.w3.eth.get_transaction_count(address)
    
    def get_gas_price(self):
        """Get current gas price"""
        return self.w3.eth.gas_price
    
    def send_transaction(self, to_address, value_eth):
        """Send ETH transaction"""
        if not self.account:
            return None, "No account configured"
        
        try:
            nonce = self.get_transaction_count(self.account.address)
            
            transaction = {
                'to': to_address,
                'value': self.w3.to_wei(value_eth, 'ether'),
                'gas': DEFAULT_GAS_LIMIT,
                'gasPrice': self.get_gas_price(),
                'nonce': nonce,
                'chainId': self.w3.eth.chain_id
            }
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex(), None
        
        except Exception as e:
            return None, str(e)
    
    def get_transaction_receipt(self, tx_hash):
        """Get transaction receipt"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                'transactionHash': receipt['transactionHash'].hex(),
                'blockNumber': receipt['blockNumber'],
                'gasUsed': receipt['gasUsed'],
                'status': receipt['status']
            }
        except Exception as e:
            return None
    
    def load_contract(self, contract_address, abi):
        """Load smart contract"""
        self.contract = self.w3.eth.contract(address=contract_address, abi=abi)
        return self.contract
    
    def call_contract_function(self, function_name, *args):
        """Call contract function (read-only)"""
        if not self.contract:
            return None, "Contract not loaded"
        
        try:
            function = getattr(self.contract.functions, function_name)
            result = function(*args).call()
            return result, None
        except Exception as e:
            return None, str(e)
    
    def send_contract_transaction(self, function_name, *args):
        """Send contract transaction"""
        if not self.contract or not self.account:
            return None, "Contract or account not configured"
        
        try:
            function = getattr(self.contract.functions, function_name)
            
            nonce = self.get_transaction_count(self.account.address)
            
            transaction = function(*args).build_transaction({
                'from': self.account.address,
                'gas': DEFAULT_GAS_LIMIT,
                'gasPrice': self.get_gas_price(),
                'nonce': nonce,
                'chainId': self.w3.eth.chain_id
            })
            
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            return tx_hash.hex(), None
        
        except Exception as e:
            return None, str(e)
    
    def verify_signature(self, message, signature, address):
        """Verify message signature"""
        try:
            message_hash = self.w3.keccak(text=message)
            recovered_address = self.w3.eth.account.recover_message(
                message_hash,
                signature=signature
            )
            return recovered_address.lower() == address.lower()
        except:
            return False
    
    def create_wallet(self):
        """Create new wallet"""
        account = Account.create()
        return {
            'address': account.address,
            'private_key': account.key.hex()
        }
    
    def get_block_number(self):
        """Get current block number"""
        return self.w3.eth.block_number
    
    def get_block(self, block_number):
        """Get block data"""
        return self.w3.eth.get_block(block_number)

# Global Web3 backend instance
web3_backend = Web3Backend()
