"""
API client SDK for PassportApp
Python SDK for interacting with PassportApp API
"""

import requests
from typing import Optional, Dict, List, Any
from datetime import datetime
import json


class PassportAppClient:
    """Client for PassportApp API"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the API (e.g., 'https://api.passportapp.com')
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'PassportApp-Python-SDK/1.0'
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.status_code == 204:
                return {}
            
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            error_data = {}
            
            try:
                error_data = e.response.json()
            except:
                error_data = {'error': str(e)}
            
            raise APIError(
                message=error_data.get('error', 'API request failed'),
                status_code=e.response.status_code,
                response=error_data
            )
        
        except requests.exceptions.RequestException as e:
            raise APIError(message=str(e))
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return self._request('POST', endpoint, json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return self._request('PUT', endpoint, json=data)
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return self._request('DELETE', endpoint)
    
    # Passport endpoints
    def create_passport(self, passport_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new passport"""
        return self.post('/api/passport/create', passport_data)
    
    def get_passport(self, passport_id: int) -> Dict[str, Any]:
        """Get passport by ID"""
        return self.get(f'/api/passport/{passport_id}')
    
    def update_passport(self, passport_id: int, passport_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update passport"""
        return self.put(f'/api/passport/{passport_id}', passport_data)
    
    def delete_passport(self, passport_id: int) -> Dict[str, Any]:
        """Delete passport"""
        return self.delete(f'/api/passport/{passport_id}')
    
    def list_passports(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """List passports"""
        return self.get('/api/passport/list', {'page': page, 'per_page': per_page})
    
    def search_passports(self, query: str) -> Dict[str, Any]:
        """Search passports"""
        return self.get('/api/passport/search', {'q': query})
    
    # NFT endpoints
    def mint_nft(self, passport_id: int) -> Dict[str, Any]:
        """Mint NFT for passport"""
        return self.post('/api/nft/mint', {'passport_id': passport_id})
    
    def get_nft(self, token_id: int) -> Dict[str, Any]:
        """Get NFT by token ID"""
        return self.get(f'/api/nft/{token_id}')
    
    def transfer_nft(self, token_id: int, to_address: str) -> Dict[str, Any]:
        """Transfer NFT to another address"""
        return self.post(f'/api/nft/{token_id}/transfer', {'to_address': to_address})
    
    def list_nfts(self, owner_address: Optional[str] = None) -> Dict[str, Any]:
        """List NFTs"""
        params = {}
        if owner_address:
            params['owner'] = owner_address
        
        return self.get('/api/nft/list', params)
    
    # Marketplace endpoints
    def list_nft_for_sale(self, token_id: int, price: float) -> Dict[str, Any]:
        """List NFT for sale"""
        return self.post('/api/marketplace/list', {
            'token_id': token_id,
            'price': price
        })
    
    def unlist_nft(self, token_id: int) -> Dict[str, Any]:
        """Remove NFT from marketplace"""
        return self.post(f'/api/marketplace/unlist/{token_id}')
    
    def purchase_nft(self, token_id: int) -> Dict[str, Any]:
        """Purchase NFT from marketplace"""
        return self.post('/api/marketplace/purchase', {'token_id': token_id})
    
    def get_marketplace_listings(self) -> Dict[str, Any]:
        """Get all marketplace listings"""
        return self.get('/api/marketplace/listings')
    
    # User endpoints
    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register new user"""
        return self.post('/api/auth/register', {
            'username': username,
            'email': email,
            'password': password
        })
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login user"""
        response = self.post('/api/auth/login', {
            'email': email,
            'password': password
        })
        
        # Store token for future requests
        if 'token' in response:
            self.api_key = response['token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
        
        return response
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get current user profile"""
        return self.get('/api/user/profile')
    
    def update_user_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        return self.put('/api/user/profile', profile_data)
    
    # Transaction endpoints
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction by hash"""
        return self.get(f'/api/transaction/{tx_hash}')
    
    def list_transactions(self, address: Optional[str] = None) -> Dict[str, Any]:
        """List transactions"""
        params = {}
        if address:
            params['address'] = address
        
        return self.get('/api/transaction/list', params)
    
    # Analytics endpoints
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics data"""
        return self.get('/api/analytics')
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        return self.get(f'/api/analytics/user/{user_id}')


class APIError(Exception):
    """API error exception"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"APIError({self.status_code}): {self.message}"
        return f"APIError: {self.message}"


class PassportResource:
    """Passport resource helper"""
    
    def __init__(self, client: PassportAppClient):
        self.client = client
    
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create passport"""
        return self.client.create_passport(kwargs)
    
    def get(self, passport_id: int) -> Dict[str, Any]:
        """Get passport"""
        return self.client.get_passport(passport_id)
    
    def update(self, passport_id: int, **kwargs) -> Dict[str, Any]:
        """Update passport"""
        return self.client.update_passport(passport_id, kwargs)
    
    def delete(self, passport_id: int) -> Dict[str, Any]:
        """Delete passport"""
        return self.client.delete_passport(passport_id)
    
    def list(self, page: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """List passports"""
        response = self.client.list_passports(page, per_page)
        return response.get('passports', [])
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search passports"""
        response = self.client.search_passports(query)
        return response.get('results', [])


class NFTResource:
    """NFT resource helper"""
    
    def __init__(self, client: PassportAppClient):
        self.client = client
    
    def mint(self, passport_id: int) -> Dict[str, Any]:
        """Mint NFT"""
        return self.client.mint_nft(passport_id)
    
    def get(self, token_id: int) -> Dict[str, Any]:
        """Get NFT"""
        return self.client.get_nft(token_id)
    
    def transfer(self, token_id: int, to_address: str) -> Dict[str, Any]:
        """Transfer NFT"""
        return self.client.transfer_nft(token_id, to_address)
    
    def list(self, owner_address: Optional[str] = None) -> List[Dict[str, Any]]:
        """List NFTs"""
        response = self.client.list_nfts(owner_address)
        return response.get('nfts', [])


class MarketplaceResource:
    """Marketplace resource helper"""
    
    def __init__(self, client: PassportAppClient):
        self.client = client
    
    def list_for_sale(self, token_id: int, price: float) -> Dict[str, Any]:
        """List NFT for sale"""
        return self.client.list_nft_for_sale(token_id, price)
    
    def unlist(self, token_id: int) -> Dict[str, Any]:
        """Unlist NFT"""
        return self.client.unlist_nft(token_id)
    
    def purchase(self, token_id: int) -> Dict[str, Any]:
        """Purchase NFT"""
        return self.client.purchase_nft(token_id)
    
    def get_listings(self) -> List[Dict[str, Any]]:
        """Get marketplace listings"""
        response = self.client.get_marketplace_listings()
        return response.get('listings', [])


# Enhanced client with resource helpers
class PassportApp:
    """Enhanced PassportApp client"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.client = PassportAppClient(base_url, api_key)
        self.passports = PassportResource(self.client)
        self.nfts = NFTResource(self.client)
        self.marketplace = MarketplaceResource(self.client)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and authenticate"""
        return self.client.login(email, password)
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Register new user"""
        return self.client.register_user(username, email, password)


# Example usage
if __name__ == '__main__':
    # Initialize client
    app = PassportApp('https://api.passportapp.com', api_key='your-api-key')
    
    # Login
    # app.login('user@example.com', 'password')
    
    # Create passport
    passport = app.passports.create(
        passport_number='AB123456',
        first_name='John',
        last_name='Doe',
        date_of_birth='1990-01-01',
        nationality='US',
        issue_date='2020-01-01',
        expiry_date='2030-01-01'
    )
    
    print(f"Created passport: {passport}")
    
    # List passports
    passports = app.passports.list()
    print(f"Total passports: {len(passports)}")
    
    # Mint NFT
    nft = app.nfts.mint(passport['id'])
    print(f"Minted NFT: {nft}")
    
    # List for sale
    listing = app.marketplace.list_for_sale(nft['token_id'], 0.5)
    print(f"Listed NFT: {listing}")
