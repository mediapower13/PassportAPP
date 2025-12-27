"""
Web3 Configuration for PassportApp
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Web3 Configuration
WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI', 'https://sepolia.infura.io/v3/your-project-id')
PRIVATE_KEY = os.getenv('PRIVATE_KEY', '')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS', '')

# Network configurations
NETWORKS = {
    'sepolia': {
        'name': 'Sepolia Testnet',
        'chain_id': 11155111,
        'rpc_url': 'https://sepolia.infura.io/v3/',
        'explorer': 'https://sepolia.etherscan.io'
    },
    'mainnet': {
        'name': 'Ethereum Mainnet',
        'chain_id': 1,
        'rpc_url': 'https://mainnet.infura.io/v3/',
        'explorer': 'https://etherscan.io'
    },
    'polygon': {
        'name': 'Polygon',
        'chain_id': 137,
        'rpc_url': 'https://polygon-rpc.com',
        'explorer': 'https://polygonscan.com'
    }
}

# Gas settings
DEFAULT_GAS_LIMIT = 3000000
GAS_PRICE_MULTIPLIER = 1.1

# IPFS Configuration
IPFS_GATEWAY = os.getenv('IPFS_GATEWAY', 'https://ipfs.io/ipfs/')
PINATA_API_KEY = os.getenv('PINATA_API_KEY', '')
PINATA_SECRET_KEY = os.getenv('PINATA_SECRET_KEY', '')
