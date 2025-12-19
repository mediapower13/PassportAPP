"""
Test fixtures and mock data for PassportApp testing
Provides reusable test data and helper functions
"""

from datetime import datetime, timedelta
import random
import string


class MockData:
    """Mock data generator for testing"""
    
    @staticmethod
    def random_string(length=10):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_email():
        """Generate random email"""
        return f"{MockData.random_string(8)}@test.com"
    
    @staticmethod
    def random_passport_number():
        """Generate random passport number"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
    
    @staticmethod
    def random_eth_address():
        """Generate random Ethereum address"""
        return '0x' + ''.join(random.choices('0123456789abcdef', k=40))
    
    @staticmethod
    def random_ipfs_hash():
        """Generate random IPFS hash"""
        return 'Qm' + ''.join(random.choices(string.ascii_letters + string.digits, k=44))
    
    @staticmethod
    def random_tx_hash():
        """Generate random transaction hash"""
        return '0x' + ''.join(random.choices('0123456789abcdef', k=64))
    
    @staticmethod
    def random_date(start_year=2020, end_year=2030):
        """Generate random date"""
        start = datetime(start_year, 1, 1)
        end = datetime(end_year, 12, 31)
        delta = end - start
        random_days = random.randint(0, delta.days)
        return (start + timedelta(days=random_days)).date()


class TestFixtures:
    """Test fixtures for common test scenarios"""
    
    @staticmethod
    def create_test_user():
        """Create test user data"""
        return {
            'username': f'testuser_{MockData.random_string(5)}',
            'email': MockData.random_email(),
            'password': 'TestPassword123!',
            'wallet_address': MockData.random_eth_address()
        }
    
    @staticmethod
    def create_test_passport():
        """Create test passport data"""
        return {
            'passport_number': MockData.random_passport_number(),
            'first_name': 'Test',
            'last_name': 'User',
            'date_of_birth': '1990-01-01',
            'nationality': 'USA',
            'issue_date': str(MockData.random_date(2020, 2023)),
            'expiry_date': str(MockData.random_date(2025, 2033)),
            'issuing_country': 'United States',
            'place_of_birth': 'New York'
        }
    
    @staticmethod
    def create_test_nft():
        """Create test NFT data"""
        return {
            'token_id': random.randint(1, 10000),
            'owner': MockData.random_eth_address(),
            'metadata_uri': f'ipfs://{MockData.random_ipfs_hash()}',
            'passport_id': MockData.random_passport_number(),
            'price': random.uniform(0.01, 1.0),
            'listed': random.choice([True, False])
        }
    
    @staticmethod
    def create_test_transaction():
        """Create test transaction data"""
        return {
            'hash': MockData.random_tx_hash(),
            'from_address': MockData.random_eth_address(),
            'to_address': MockData.random_eth_address(),
            'value': random.uniform(0.001, 1.0),
            'gas': random.randint(21000, 100000),
            'gas_price': random.randint(20, 100),
            'nonce': random.randint(0, 1000),
            'block_number': random.randint(1000000, 2000000),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_test_marketplace_listing():
        """Create test marketplace listing"""
        return {
            'listing_id': random.randint(1, 10000),
            'token_id': random.randint(1, 10000),
            'seller': MockData.random_eth_address(),
            'price': random.uniform(0.1, 10.0),
            'listed_at': datetime.utcnow().isoformat(),
            'status': random.choice(['active', 'sold', 'cancelled'])
        }
    
    @staticmethod
    def create_test_event():
        """Create test blockchain event"""
        return {
            'event': random.choice(['Transfer', 'Approval', 'Mint', 'Burn']),
            'address': MockData.random_eth_address(),
            'block_number': random.randint(1000000, 2000000),
            'transaction_hash': MockData.random_tx_hash(),
            'log_index': random.randint(0, 100),
            'args': {
                'from': MockData.random_eth_address(),
                'to': MockData.random_eth_address(),
                'token_id': random.randint(1, 10000)
            }
        }


class TestHelpers:
    """Helper functions for testing"""
    
    @staticmethod
    def create_test_session():
        """Create test session data"""
        return {
            'user_id': random.randint(1, 1000),
            'session_id': MockData.random_string(32),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
    
    @staticmethod
    def create_multiple_users(count=5):
        """Create multiple test users"""
        return [TestFixtures.create_test_user() for _ in range(count)]
    
    @staticmethod
    def create_multiple_passports(count=5):
        """Create multiple test passports"""
        return [TestFixtures.create_test_passport() for _ in range(count)]
    
    @staticmethod
    def create_multiple_nfts(count=5):
        """Create multiple test NFTs"""
        return [TestFixtures.create_test_nft() for _ in range(count)]
    
    @staticmethod
    def create_blockchain_state():
        """Create mock blockchain state"""
        return {
            'block_number': random.randint(1000000, 2000000),
            'network_id': random.choice([1, 3, 4, 5, 11155111]),
            'gas_price': random.randint(20, 100),
            'accounts': [MockData.random_eth_address() for _ in range(5)]
        }
    
    @staticmethod
    def mock_ipfs_response(success=True):
        """Create mock IPFS response"""
        if success:
            return {
                'success': True,
                'hash': MockData.random_ipfs_hash(),
                'size': random.randint(1000, 100000),
                'url': f'https://ipfs.io/ipfs/{MockData.random_ipfs_hash()}'
            }
        else:
            return {
                'success': False,
                'error': 'Failed to upload to IPFS'
            }
    
    @staticmethod
    def mock_web3_transaction_receipt(success=True):
        """Create mock Web3 transaction receipt"""
        return {
            'transactionHash': MockData.random_tx_hash(),
            'blockNumber': random.randint(1000000, 2000000),
            'gasUsed': random.randint(21000, 100000),
            'status': 1 if success else 0,
            'from': MockData.random_eth_address(),
            'to': MockData.random_eth_address(),
            'logs': []
        }
    
    @staticmethod
    def assert_valid_passport(passport_data):
        """Validate passport data structure"""
        required_fields = [
            'passport_number', 'first_name', 'last_name',
            'date_of_birth', 'nationality', 'issue_date',
            'expiry_date', 'issuing_country'
        ]
        
        for field in required_fields:
            assert field in passport_data, f"Missing field: {field}"
        
        return True
    
    @staticmethod
    def assert_valid_eth_address(address):
        """Validate Ethereum address format"""
        assert isinstance(address, str), "Address must be string"
        assert address.startswith('0x'), "Address must start with 0x"
        assert len(address) == 42, "Address must be 42 characters"
        
        return True
    
    @staticmethod
    def assert_valid_tx_hash(tx_hash):
        """Validate transaction hash format"""
        assert isinstance(tx_hash, str), "Hash must be string"
        assert tx_hash.startswith('0x'), "Hash must start with 0x"
        assert len(tx_hash) == 66, "Hash must be 66 characters"
        
        return True


# Sample test data sets
SAMPLE_USERS = TestHelpers.create_multiple_users(10)
SAMPLE_PASSPORTS = TestHelpers.create_multiple_passports(10)
SAMPLE_NFTS = TestHelpers.create_multiple_nfts(10)


def reset_test_data():
    """Reset all test data to fresh state"""
    global SAMPLE_USERS, SAMPLE_PASSPORTS, SAMPLE_NFTS
    
    SAMPLE_USERS = TestHelpers.create_multiple_users(10)
    SAMPLE_PASSPORTS = TestHelpers.create_multiple_passports(10)
    SAMPLE_NFTS = TestHelpers.create_multiple_nfts(10)
    
    return True


def get_random_sample(data_type='user'):
    """Get random sample from test data"""
    if data_type == 'user':
        return random.choice(SAMPLE_USERS)
    elif data_type == 'passport':
        return random.choice(SAMPLE_PASSPORTS)
    elif data_type == 'nft':
        return random.choice(SAMPLE_NFTS)
    else:
        return None
