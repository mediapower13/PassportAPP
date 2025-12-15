// Web3 Wallet Connection and Blockchain Integration

class Web3Manager {
    constructor() {
        this.web3 = null;
        this.account = null;
        this.contract = null;
        this.contractAddress = null;
        this.contractABI = null;
    }

    /**
     * Initialize Web3 and connect to MetaMask
     */
    async connectWallet() {
        try {
            if (typeof window.ethereum === 'undefined') {
                throw new Error('MetaMask is not installed. Please install MetaMask to use Web3 features.');
            }

            // Request account access
            const accounts = await window.ethereum.request({ 
                method: 'eth_requestAccounts' 
            });
            
            this.account = accounts[0];
            
            // Initialize Web3
            this.web3 = new Web3(window.ethereum);
            
            // Get network ID
            const networkId = await this.web3.eth.net.getId();
            console.log('Connected to network:', networkId);
            
            // Listen for account changes
            window.ethereum.on('accountsChanged', (accounts) => {
                this.account = accounts[0];
                this.updateUIWithAccount();
            });
            
            // Listen for chain changes
            window.ethereum.on('chainChanged', () => {
                window.location.reload();
            });
            
            this.updateUIWithAccount();
            return this.account;
            
        } catch (error) {
            console.error('Error connecting wallet:', error);
            throw error;
        }
    }

    /**
     * Disconnect wallet
     */
    disconnectWallet() {
        this.account = null;
        this.web3 = null;
        this.updateUIWithAccount();
    }

    /**
     * Update UI with connected account
     */
    updateUIWithAccount() {
        const walletBtn = document.getElementById('connectWalletBtn');
        const walletAddress = document.getElementById('walletAddress');
        
        if (this.account) {
            if (walletBtn) {
                walletBtn.textContent = 'Disconnect Wallet';
                walletBtn.classList.add('connected');
            }
            if (walletAddress) {
                walletAddress.textContent = `${this.account.substring(0, 6)}...${this.account.substring(38)}`;
                walletAddress.style.display = 'block';
            }
        } else {
            if (walletBtn) {
                walletBtn.textContent = 'Connect Wallet';
                walletBtn.classList.remove('connected');
            }
            if (walletAddress) {
                walletAddress.style.display = 'none';
            }
        }
    }

    /**
     * Initialize smart contract
     */
    async initContract(contractAddress, contractABI) {
        if (!this.web3) {
            throw new Error('Web3 not initialized. Please connect wallet first.');
        }
        
        this.contractAddress = contractAddress;
        this.contractABI = contractABI;
        this.contract = new this.web3.eth.Contract(contractABI, contractAddress);
        
        return this.contract;
    }

    /**
     * Store passport data on blockchain
     */
    async storePassportOnChain(passportNumber, documentHash) {
        try {
            if (!this.contract) {
                throw new Error('Contract not initialized');
            }
            
            const tx = await this.contract.methods
                .storePassport(passportNumber, documentHash)
                .send({ 
                    from: this.account,
                    gas: 300000
                });
            
            console.log('Passport stored on blockchain:', tx);
            return tx;
            
        } catch (error) {
            console.error('Error storing passport:', error);
            throw error;
        }
    }

    /**
     * Update passport on blockchain
     */
    async updatePassportOnChain(passportId, newDocumentHash) {
        try {
            if (!this.contract) {
                throw new Error('Contract not initialized');
            }
            
            const tx = await this.contract.methods
                .updatePassport(passportId, newDocumentHash)
                .send({ 
                    from: this.account,
                    gas: 200000
                });
            
            console.log('Passport updated on blockchain:', tx);
            return tx;
            
        } catch (error) {
            console.error('Error updating passport:', error);
            throw error;
        }
    }

    /**
     * Get passport from blockchain
     */
    async getPassportFromChain(passportId) {
        try {
            if (!this.contract) {
                throw new Error('Contract not initialized');
            }
            
            const passport = await this.contract.methods
                .getPassport(passportId)
                .call();
            
            return {
                passportNumber: passport.passportNumber,
                documentHash: passport.documentHash,
                timestamp: passport.timestamp,
                owner: passport.owner,
                isActive: passport.isActive
            };
            
        } catch (error) {
            console.error('Error getting passport:', error);
            throw error;
        }
    }

    /**
     * Get all passports for current account
     */
    async getMyPassports() {
        try {
            if (!this.contract || !this.account) {
                throw new Error('Contract or account not initialized');
            }
            
            const passportIds = await this.contract.methods
                .getOwnerPassports(this.account)
                .call();
            
            return passportIds;
            
        } catch (error) {
            console.error('Error getting passports:', error);
            throw error;
        }
    }

    /**
     * Deactivate passport on blockchain
     */
    async deactivatePassportOnChain(passportId) {
        try {
            if (!this.contract) {
                throw new Error('Contract not initialized');
            }
            
            const tx = await this.contract.methods
                .deactivatePassport(passportId)
                .send({ 
                    from: this.account,
                    gas: 150000
                });
            
            console.log('Passport deactivated on blockchain:', tx);
            return tx;
            
        } catch (error) {
            console.error('Error deactivating passport:', error);
            throw error;
        }
    }

    /**
     * Verify passport ownership
     */
    async verifyOwnership(passportId, ownerAddress) {
        try {
            if (!this.contract) {
                throw new Error('Contract not initialized');
            }
            
            const isOwner = await this.contract.methods
                .verifyOwnership(passportId, ownerAddress)
                .call();
            
            return isOwner;
            
        } catch (error) {
            console.error('Error verifying ownership:', error);
            throw error;
        }
    }

    /**
     * Get account balance
     */
    async getBalance() {
        try {
            if (!this.web3 || !this.account) {
                throw new Error('Web3 or account not initialized');
            }
            
            const balance = await this.web3.eth.getBalance(this.account);
            return this.web3.utils.fromWei(balance, 'ether');
            
        } catch (error) {
            console.error('Error getting balance:', error);
            throw error;
        }
    }

    /**
     * Sign message with wallet
     */
    async signMessage(message) {
        try {
            if (!this.web3 || !this.account) {
                throw new Error('Web3 or account not initialized');
            }
            
            const signature = await this.web3.eth.personal.sign(
                message,
                this.account
            );
            
            return signature;
            
        } catch (error) {
            console.error('Error signing message:', error);
            throw error;
        }
    }
}

// Initialize Web3Manager
const web3Manager = new Web3Manager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Web3Manager;
}
