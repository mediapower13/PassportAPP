# PassportApp Web3 Integration Guide

## Overview
PassportApp now includes Web3 blockchain integration for secure, decentralized passport data storage.

## Features
- **Wallet Connection**: Connect MetaMask or other Web3 wallets
- **Blockchain Storage**: Store passport data on Ethereum-compatible networks
- **Smart Contract**: Secure data management using Solidity smart contracts
- **IPFS Integration**: Decentralized document storage
- **Data Verification**: Cryptographic proof of ownership

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure Web3

Copy the Web3 environment file:
```bash
cp .env.web3.example .env.web3
```

Edit `.env.web3` with your configuration:
- Add your Infura/Alchemy RPC URLs
- Add your wallet private key (for deployment only)
- Configure IPFS settings

### 3. Compile Smart Contracts

```bash
npm run compile
```

### 4. Deploy Smart Contract

For local development:
```bash
# Start local Hardhat node
npm run hardhat-node

# Deploy to localhost (in another terminal)
npm run deploy
```

For testnet (Sepolia):
```bash
npx hardhat run scripts/deploy.js --network sepolia
```

### 5. Update Frontend

After deployment, update the contract address in:
- `static/js/web3-ui.js` - Update the `contractAddress` variable
- Or set it in the dashboard UI

## Smart Contract Functions

### Store Passport
```solidity
function storePassport(string passportNumber, string documentHash) 
    returns (uint256 passportId)
```

### Update Passport
```solidity
function updatePassport(uint256 passportId, string newDocumentHash)
```

### Get Passport
```solidity
function getPassport(uint256 passportId) 
    returns (string passportNumber, string documentHash, uint256 timestamp, address owner, bool isActive)
```

### Get Owner Passports
```solidity
function getOwnerPassports(address owner) 
    returns (uint256[] passportIds)
```

## Usage

### Connect Wallet
1. Open the PassportApp dashboard
2. Click "Connect Wallet" button
3. Approve the connection in MetaMask

### Store Passport on Blockchain
1. Add a new passport or view existing passport
2. Click "Store on Blockchain" button
3. Confirm the transaction in MetaMask
4. Wait for transaction confirmation

### Sync from Blockchain
1. Click "Sync from Blockchain" on dashboard
2. View all passports stored on blockchain
3. Verify ownership and status

## Security Considerations

- **Private Keys**: Never commit your private key to version control
- **Encryption**: Passport data is encrypted before blockchain storage
- **IPFS**: Sensitive documents stored on IPFS should be encrypted
- **Gas Fees**: Be aware of network gas fees for transactions

## Supported Networks

- Ethereum Mainnet
- Sepolia Testnet
- Polygon
- Binance Smart Chain
- Local Hardhat Network

## Contract ABI

The contract ABI is automatically generated in `artifacts/contracts/PassportStorage.sol/PassportStorage.json` after compilation.

## Troubleshooting

### MetaMask Not Detected
- Ensure MetaMask extension is installed
- Refresh the page after installation

### Transaction Failed
- Check wallet has sufficient ETH for gas
- Verify network is correct
- Check contract address is set correctly

### Contract Not Found
- Ensure contract is deployed to current network
- Verify contract address in configuration

## Gas Optimization

The smart contract is optimized for minimal gas usage:
- Store only passport number and document hash
- Use events for transaction logging
- Efficient data structures

## Future Enhancements

- Multi-signature wallet support
- Layer 2 integration (Arbitrum, Optimism)
- NFT passport certificates
- Decentralized identity integration
- Cross-chain bridge support

## Support

For issues or questions:
- Check the contract on block explorer
- Review transaction logs
- Contact support with transaction hash

## License

MIT License - See LICENSE file for details
