"""
Web3 Integration Backend for PassportApp
Handles blockchain interactions from Python backend
"""

from web3 import Web3
from eth_account import Account
import json
import os
from dotenv import load_dotenv

load_dotenv()


class Web3Backend:
    """Backend Web3 integration for passport blockchain operations"""
    
    def __init__(self):
        self.w3 = None
        self.contract = None
        self.contract_address = None
        self.contract_abi = None
        self.account = None
        
    def connect(self, rpc_url=None, private_key=None):
        """Connect to blockchain network"""
        if not rpc_url:
            rpc_url = os.getenv('WEB3_RPC_URL', 'http://127.0.0.1:8545')
            
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise Exception(f"Failed to connect to {rpc_url}")
        
        # Set account if private key provided
        if private_key:
            self.account = Account.from_key(private_key)
        elif os.getenv('PRIVATE_KEY'):
            self.account = Account.from_key(os.getenv('PRIVATE_KEY'))
            
        return True
    
    def is_connected(self):
        """Check if Web3 is connected"""
        return self.w3 is not None and self.w3.is_connected()
    
    def load_contract(self, address=None, abi_path=None):
        """Load smart contract"""
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # Load contract address
        if not address:
            address = os.getenv('CONTRACT_ADDRESS')
        
        if not address:
            raise Exception("Contract address not provided")
            
        self.contract_address = self.w3.to_checksum_address(address)
        
        # Load ABI
        if not abi_path:
            abi_path = 'artifacts/contracts/PassportStorage.sol/PassportStorage.json'
        
        if os.path.exists(abi_path):
            with open(abi_path, 'r') as f:
                contract_json = json.load(f)
                self.contract_abi = contract_json['abi']
        else:
            raise Exception(f"ABI file not found: {abi_path}")
        
        # Create contract instance
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        return True
    
    def set_contract(self, address, abi_path=None):
        """Alias for load_contract for compatibility"""
        return self.load_contract(address, abi_path)
    
    def store_passport(self, passport_number, document_hash, private_key=None):
        """Store passport on blockchain"""
        if not self.contract:
            raise Exception("Contract not loaded")
        
        account = self.account if not private_key else Account.from_key(private_key)
        
        if not account:
            raise Exception("No account available for signing")
        
        # Build transaction
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.storePassport(
            passport_number,
            document_hash
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign transaction
        signed_txn = account.sign_transaction(transaction)
        
        # Send transaction
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt['blockNumber'],
            'gas_used': tx_receipt['gasUsed'],
            'status': tx_receipt['status']
        }
    
    def get_passport(self, passport_id):
        """Get passport from blockchain"""
        if not self.contract:
            raise Exception("Contract not loaded")
        
        passport = self.contract.functions.getPassport(passport_id).call()
        
        return {
            'passport_number': passport[0],
            'document_hash': passport[1],
            'timestamp': passport[2],
            'owner': passport[3],
            'is_active': passport[4]
        }
    
    def get_owner_passports(self, owner_address):
        """Get all passports for an owner"""
        if not self.contract:
            raise Exception("Contract not loaded")
        
        passport_ids = self.contract.functions.getOwnerPassports(
            self.w3.to_checksum_address(owner_address)
        ).call()
        
        return passport_ids
    
    def update_passport(self, passport_id, new_document_hash, private_key=None):
        """Update passport on blockchain"""
        if not self.contract:
            raise Exception("Contract not loaded")
        
        account = self.account if not private_key else Account.from_key(private_key)
        
        if not account:
            raise Exception("No account available for signing")
        
        nonce = self.w3.eth.get_transaction_count(account.address)
        
        transaction = self.contract.functions.updatePassport(
            passport_id,
            new_document_hash
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_txn = account.sign_transaction(transaction)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt['blockNumber'],
            'status': tx_receipt['status']
        }
    
    def verify_ownership(self, passport_id, owner_address):
        """Verify passport ownership"""
        if not self.contract:
            raise Exception("Contract not loaded")
        
        is_owner = self.contract.functions.verifyOwnership(
            passport_id,
            self.w3.to_checksum_address(owner_address)
        ).call()
        
        return is_owner
    
    def get_balance(self, address):
        """Get wallet balance"""
        if not self.w3:
            raise Exception("Web3 not connected")
        
        balance_wei = self.w3.eth.get_balance(
            self.w3.to_checksum_address(address)
        )
        balance_ether = self.w3.from_wei(balance_wei, 'ether')
        
        return {
            'wei': balance_wei,
            'ether': float(balance_ether)
        }
    
    def sign_message(self, message, private_key=None):
        """Sign a message with private key"""
        account = self.account if not private_key else Account.from_key(private_key)
        
        if not account:
            raise Exception("No account available for signing")
        
        message_hash = self.w3.keccak(text=message)
        signed_message = account.sign_message_hash(message_hash)
        
        return {
            'message': message,
            'signature': signed_message.signature.hex(),
            'signer': account.address
        }


# Initialize global instance
web3_backend = Web3Backend()


def init_web3(rpc_url=None, contract_address=None):
    """Initialize Web3 backend"""
    web3_backend.connect(rpc_url)
    
    if contract_address or os.getenv('CONTRACT_ADDRESS'):
        web3_backend.load_contract(contract_address)
    
    return web3_backend
