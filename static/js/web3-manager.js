/**
 * Web3 Manager for PassportApp
 * Handles wallet connections and blockchain interactions
 */

class Web3Manager {
    constructor() {
        this.web3 = null;
        this.account = null;
        this.networkId = null;
    }

    /**
     * Initialize Web3 connection
     */
    async init() {
        if (typeof window.ethereum !== 'undefined') {
            try {
                this.web3 = new Web3(window.ethereum);
                console.log('✓ Web3 initialized');
                return true;
            } catch (error) {
                console.error('Failed to initialize Web3:', error);
                return false;
            }
        } else {
            console.warn('MetaMask not detected');
            return false;
        }
    }

    /**
     * Connect wallet
     */
    async connectWallet() {
        try {
            if (!this.web3) {
                await this.init();
            }

            if (!this.web3) {
                throw new Error('Web3 not available. Please install MetaMask.');
            }

            // Request account access
            const accounts = await window.ethereum.request({ 
                method: 'eth_requestAccounts' 
            });
            
            this.account = accounts[0];
            this.networkId = await this.web3.eth.net.getId();

            console.log('✓ Wallet connected:', this.account);

            // Notify backend
            await this.notifyBackend();

            return true;
        } catch (error) {
            console.error('Failed to connect wallet:', error);
            throw error;
        }
    }

    /**
     * Notify backend about wallet connection
     */
    async notifyBackend() {
        try {
            const response = await fetch('/api/web3/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    wallet_address: this.account
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to connect wallet');
            }

            return data;
        } catch (error) {
            console.error('Backend notification failed:', error);
            throw error;
        }
    }

    /**
     * Disconnect wallet
     */
    async disconnectWallet() {
        try {
            const response = await fetch('/api/web3/disconnect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            this.account = null;
            this.networkId = null;

            console.log('✓ Wallet disconnected');
            return true;
        } catch (error) {
            console.error('Failed to disconnect wallet:', error);
            throw error;
        }
    }

    /**
     * Get wallet balance
     */
    async getBalance() {
        try {
            if (!this.account) {
                throw new Error('Wallet not connected');
            }

            const balance = await this.web3.eth.getBalance(this.account);
            return this.web3.utils.fromWei(balance, 'ether');
        } catch (error) {
            console.error('Failed to get balance:', error);
            throw error;
        }
    }

    /**
     * Get Web3 status from backend
     */
    async getStatus() {
        try {
            const response = await fetch('/api/web3/status');
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to get Web3 status:', error);
            throw error;
        }
    }

    /**
     * Store passport on blockchain
     */
    async storePassport(passportId) {
        try {
            if (!this.account) {
                throw new Error('Wallet not connected');
            }

            const response = await fetch('/api/web3/passport/store', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    passport_id: passportId
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to store passport');
            }

            return data;
        } catch (error) {
            console.error('Failed to store passport:', error);
            throw error;
        }
    }

    /**
     * Get passport from blockchain
     */
    async getPassport(passportNumber) {
        try {
            const response = await fetch(`/api/web3/passport/get/${passportNumber}`);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to get passport');
            }

            return data;
        } catch (error) {
            console.error('Failed to get passport:', error);
            throw error;
        }
    }

    /**
     * Get current gas price
     */
    async getGasPrice() {
        try {
            const response = await fetch('/api/web3/gas-price');
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to get gas price');
            }

            return data;
        } catch (error) {
            console.error('Failed to get gas price:', error);
            throw error;
        }
    }

    /**
     * Format address (shorten)
     */
    formatAddress(address) {
        if (!address) return '';
        return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    }

    /**
     * Check if wallet is connected
     */
    isConnected() {
        return this.account !== null;
    }
}

// Global instance
const web3Manager = new Web3Manager();

// Auto-initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await web3Manager.init();
    
    // Check if already connected
    if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
            web3Manager.account = accounts[0];
            console.log('✓ Wallet auto-connected:', web3Manager.account);
        }
    }

    // Listen for account changes
    if (window.ethereum) {
        window.ethereum.on('accountsChanged', (accounts) => {
            if (accounts.length > 0) {
                web3Manager.account = accounts[0];
                console.log('Account changed:', web3Manager.account);
                location.reload();
            } else {
                web3Manager.account = null;
                console.log('Wallet disconnected');
                location.reload();
            }
        });

        // Listen for network changes
        window.ethereum.on('chainChanged', () => {
            console.log('Network changed, reloading...');
            location.reload();
        });
    }
});
