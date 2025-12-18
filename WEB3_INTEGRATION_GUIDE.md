# Web3 Integration Guide

## Overview
Complete guide for integrating Web3 blockchain functionality into PassportApp.

## Table of Contents
1. [Smart Contracts](#smart-contracts)
2. [Frontend Integration](#frontend-integration)
3. [Backend Integration](#backend-integration)
4. [Security](#security)
5. [Testing](#testing)
6. [Deployment](#deployment)

---

## Smart Contracts

### PassportStorage.sol
Core contract for storing passport data on blockchain.

**Key Functions:**
- `storePassport(string passportNumber, string documentHash)` - Store new passport
- `updatePassport(uint256 passportId, string newDocumentHash)` - Update existing passport
- `getPassport(uint256 passportId)` - Retrieve passport data
- `deactivatePassport(uint256 passportId)` - Deactivate passport
- `verifyOwnership(uint256 passportId, address owner)` - Verify ownership

### PassportVerification.sol
Handles verification requests between parties.

**Key Functions:**
- `requestVerification(uint256 passportId, address verifier)` - Request verification
- `approveVerification(uint256 requestId)` - Approve verification request
- `rejectVerification(uint256 requestId)` - Reject verification request

### PassportAccessControl.sol
Advanced access control and delegation system.

**Features:**
- Role-based access (VIEW, EDIT, FULL)
- Time-based delegations
- Granular passport-level permissions

### PassportNFT.sol
ERC-721 compatible NFT representation of passports.

**NFT Features:**
- Mint passport as NFT
- Transfer ownership
- Metadata management
- Expiration tracking

### PassportMarketplace.sol
Decentralized marketplace for verification services.

**Marketplace Features:**
- Service listings
- Order management
- Rating system
- Platform fees

---

## Frontend Integration

### Web3 Manager (`web3-manager.js`)
Core Web3 functionality.

```javascript
const web3Manager = new Web3Manager();

// Connect wallet
await web3Manager.connectWallet();

// Store passport on blockchain
const result = await web3Manager.storePassportOnChain(
    'AB123456',
    'QmDocumentHash123...'
);
```

### NFT Manager (`nft-manager.js`)
NFT operations for passports.

```javascript
const nftManager = new NFTManager(web3Manager);

// Mint passport NFT
const result = await nftManager.mintPassportNFT({
    passportNumber: 'AB123456',
    countryCode: 'US',
    issueDate: '2024-01-01',
    expiryDate: '2034-01-01',
    ipfsHash: 'QmHash...'
});
```

### IPFS Manager (`ipfs-manager.js`)
Decentralized file storage.

```javascript
const ipfsManager = new IPFSManager('YOUR_PINATA_API_KEY', 'YOUR_SECRET');

// Upload encrypted file
const result = await ipfsManager.encryptAndUpload(
    file,
    'encryption-password'
);

// Download and decrypt
const decryptedData = await ipfsManager.retrieveAndDecrypt(
    ipfsHash,
    'encryption-password'
);
```

### Event Listener (`event-listener.js`)
Real-time blockchain event monitoring.

```javascript
const eventListener = new BlockchainEventListener(web3Manager);

// Listen to passport events
eventListener.listenToPassportEvents((event) => {
    console.log('Passport event:', event);
});

// Get event history
const history = eventListener.getHistory(20);
```

### QR Generator (`qr-generator.js`)
Generate QR codes for passport data.

```javascript
const qrGenerator = new PassportQRGenerator();

// Generate passport QR code
qrGenerator.generatePassportQR(passportData, 'qr-container');

// Generate verification link QR
qrGenerator.generateShareQR(passportId, 'share-container');
```

---

## Backend Integration

### Web3 Backend (`web3_backend.py`)
Python backend for blockchain operations.

```python
from web3_backend import init_web3

# Initialize Web3
web3 = init_web3(
    rpc_url='https://sepolia.infura.io/v3/YOUR_KEY',
    contract_address='0x...'
)

# Store passport
result = web3.store_passport(
    passport_number='AB123456',
    document_hash='hash...',
    private_key='0x...'
)
```

### Web3 Routes (`web3_routes.py`)
Flask API endpoints for blockchain operations.

```python
from web3_routes import init_web3_routes

# Initialize routes
init_web3_routes(app)

# Available endpoints:
# POST /api/web3/passport/store
# GET /api/web3/passport/<id>
# PUT /api/web3/passport/<id>/update
# GET /api/web3/wallet/balance/<address>
```

### Blockchain Analytics (`blockchain_analytics.py`)
Analytics and reporting for blockchain data.

```python
from blockchain_analytics import BlockchainAnalytics

analytics = BlockchainAnalytics(web3_backend)

# Get passport statistics
stats = analytics.get_passport_statistics(owner_address)

# Generate report
report = analytics.generate_report(owner_address)
```

### Blockchain Monitor (`blockchain_monitor.py`)
Real-time monitoring service.

```python
from blockchain_monitor import init_monitoring

# Initialize monitoring
monitor = init_monitoring(web3_backend)

# Add event listener
monitor.add_listener('new_block', lambda event: print(event))

# Start monitoring
await monitor.start_monitoring()
```

---

## Security

### Web3 Security (`web3_security.py`)
Security utilities and validation.

**Key Features:**
- Ethereum address validation
- Document hash generation
- Data encryption/decryption
- Rate limiting
- Transaction validation

```python
from web3_security import Web3Security, RateLimiter

# Validate address
is_valid = Web3Security.validate_ethereum_address('0x...')

# Generate document hash
hash = Web3Security.generate_document_hash(document_data)

# Encrypt sensitive data
encrypted = Web3Security.encrypt_sensitive_data(data, password)

# Rate limiting
limiter = RateLimiter(max_requests=10, time_window=60)
allowed = limiter.is_allowed(user_id)
```

### Best Practices

1. **Never expose private keys**
   - Use environment variables
   - Never commit to version control

2. **Validate all inputs**
   - Check address formats
   - Validate transaction parameters

3. **Use rate limiting**
   - Prevent abuse
   - Protect against spam

4. **Encrypt sensitive data**
   - Before uploading to IPFS
   - In transit and at rest

5. **Test thoroughly**
   - Unit tests for contracts
   - Integration tests for Web3 interactions

---

## Testing

### Smart Contract Testing

```bash
# Run all tests
npx hardhat test

# Run specific test file
npx hardhat test test/PassportStorage.test.js

# Run with coverage
npx hardhat coverage
```

### Frontend Testing

```javascript
// Test wallet connection
async function testWalletConnection() {
    const web3Manager = new Web3Manager();
    const connected = await web3Manager.connectWallet();
    console.assert(connected, 'Wallet should connect');
}

// Test passport storage
async function testPassportStorage() {
    const result = await web3Manager.storePassportOnChain(
        'TEST123',
        'QmTestHash'
    );
    console.assert(result.success, 'Passport should be stored');
}
```

---

## Deployment

### 1. Deploy Smart Contracts

```bash
# Compile contracts
npx hardhat compile

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost

# Deploy to testnet
npx hardhat run scripts/deploy.js --network sepolia

# Deploy to mainnet
npx hardhat run scripts/deploy.js --network mainnet
```

### 2. Configure Environment Variables

```bash
# .env file
WEB3_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...
PINATA_API_KEY=...
PINATA_SECRET=...
```

### 3. Update Frontend Configuration

```javascript
// Update contract addresses in web3-manager.js
const CONTRACT_ADDRESS = '0x...';
const NFT_CONTRACT_ADDRESS = '0x...';
const MARKETPLACE_CONTRACT_ADDRESS = '0x...';
```

### 4. Initialize Backend

```python
# In your Flask app
from web3_routes import init_web3_routes
from web3_backend import init_web3

# Initialize Web3 backend
web3 = init_web3()

# Register routes
init_web3_routes(app)
```

---

## Network Configuration

### Supported Networks

1. **Ethereum Mainnet** (Chain ID: 1)
   - RPC: `https://mainnet.infura.io/v3/YOUR_KEY`
   - Explorer: https://etherscan.io

2. **Sepolia Testnet** (Chain ID: 11155111)
   - RPC: `https://sepolia.infura.io/v3/YOUR_KEY`
   - Explorer: https://sepolia.etherscan.io
   - Faucet: https://sepoliafaucet.com

3. **Polygon** (Chain ID: 137)
   - RPC: `https://polygon-rpc.com`
   - Explorer: https://polygonscan.com

4. **BSC** (Chain ID: 56)
   - RPC: `https://bsc-dataseed.binance.org`
   - Explorer: https://bscscan.com

5. **Localhost** (Chain ID: 1337)
   - RPC: `http://127.0.0.1:8545`
   - For testing with Hardhat

---

## Troubleshooting

### Common Issues

**Issue: MetaMask not connecting**
- Solution: Check if MetaMask is installed and unlocked
- Ensure correct network is selected

**Issue: Transaction failing**
- Solution: Check gas price and limit
- Verify sufficient balance
- Check contract address is correct

**Issue: IPFS upload failing**
- Solution: Verify Pinata API credentials
- Check file size limits
- Ensure proper file format

**Issue: Events not being received**
- Solution: Check WebSocket connection
- Verify contract ABI is correct
- Ensure event listeners are properly set up

---

## Resources

- [Hardhat Documentation](https://hardhat.org/docs)
- [Web3.js Documentation](https://web3js.readthedocs.io)
- [OpenZeppelin Contracts](https://docs.openzeppelin.com/contracts)
- [IPFS Documentation](https://docs.ipfs.io)
- [MetaMask Documentation](https://docs.metamask.io)

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/mediapower13/PassportAPP/issues
- Documentation: Check this guide and inline code comments
- Community: Join our Discord server

---

## License

MIT License - See LICENSE file for details
