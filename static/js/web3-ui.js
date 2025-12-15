// Web3 UI Integration for Passport App

document.addEventListener('DOMContentLoaded', function() {
    initializeWeb3UI();
});

/**
 * Initialize Web3 UI components
 */
function initializeWeb3UI() {
    const connectWalletBtn = document.getElementById('connectWalletBtn');
    const storeOnBlockchainBtn = document.getElementById('storeOnBlockchainBtn');
    const syncFromBlockchainBtn = document.getElementById('syncFromBlockchainBtn');
    
    if (connectWalletBtn) {
        connectWalletBtn.addEventListener('click', handleWalletConnection);
    }
    
    if (storeOnBlockchainBtn) {
        storeOnBlockchainBtn.addEventListener('click', handleStoreOnBlockchain);
    }
    
    if (syncFromBlockchainBtn) {
        syncFromBlockchainBtn.addEventListener('click', handleSyncFromBlockchain);
    }
    
    // Check if wallet is already connected
    checkWalletConnection();
}

/**
 * Handle wallet connection toggle
 */
async function handleWalletConnection() {
    try {
        if (web3Manager.account) {
            // Disconnect
            web3Manager.disconnectWallet();
            showNotification('Wallet disconnected', 'info');
        } else {
            // Connect
            showLoadingSpinner('Connecting to wallet...');
            const account = await web3Manager.connectWallet();
            hideLoadingSpinner();
            
            showNotification(`Connected: ${account.substring(0, 10)}...`, 'success');
            
            // Initialize contract if not already done
            await initializeContract();
            
            // Update UI elements
            updateWeb3Features(true);
        }
    } catch (error) {
        hideLoadingSpinner();
        showNotification(error.message, 'error');
    }
}

/**
 * Initialize smart contract
 */
async function initializeContract() {
    try {
        // Contract ABI and address would be loaded from config
        const contractAddress = document.getElementById('contractAddress')?.value || 
                              '0x0000000000000000000000000000000000000000';
        
        // Simplified ABI - in production, load from file
        const contractABI = [
            {
                "inputs": [{"type": "string"}, {"type": "string"}],
                "name": "storePassport",
                "outputs": [{"type": "uint256"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"type": "uint256"}],
                "name": "getPassport",
                "outputs": [
                    {"type": "string"},
                    {"type": "string"},
                    {"type": "uint256"},
                    {"type": "address"},
                    {"type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"type": "address"}],
                "name": "getOwnerPassports",
                "outputs": [{"type": "uint256[]"}],
                "stateMutability": "view",
                "type": "function"
            }
        ];
        
        await web3Manager.initContract(contractAddress, contractABI);
        console.log('Contract initialized');
        
    } catch (error) {
        console.error('Error initializing contract:', error);
    }
}

/**
 * Handle storing passport on blockchain
 */
async function handleStoreOnBlockchain() {
    try {
        if (!web3Manager.account) {
            showNotification('Please connect your wallet first', 'warning');
            return;
        }
        
        const passportNumber = document.getElementById('passportNumber')?.value;
        const passportId = document.getElementById('passportId')?.value;
        
        if (!passportNumber) {
            showNotification('No passport data to store', 'warning');
            return;
        }
        
        showLoadingSpinner('Storing on blockchain...');
        
        // Generate document hash (in production, this would be IPFS hash)
        const documentHash = await generateDocumentHash(passportNumber, passportId);
        
        // Store on blockchain
        const tx = await web3Manager.storePassportOnChain(passportNumber, documentHash);
        
        hideLoadingSpinner();
        showNotification('Passport stored on blockchain successfully!', 'success');
        
        // Update UI with transaction hash
        displayTransactionInfo(tx);
        
    } catch (error) {
        hideLoadingSpinner();
        showNotification(`Error: ${error.message}`, 'error');
    }
}

/**
 * Handle syncing from blockchain
 */
async function handleSyncFromBlockchain() {
    try {
        if (!web3Manager.account) {
            showNotification('Please connect your wallet first', 'warning');
            return;
        }
        
        showLoadingSpinner('Syncing from blockchain...');
        
        // Get all passport IDs for current account
        const passportIds = await web3Manager.getMyPassports();
        
        if (passportIds.length === 0) {
            hideLoadingSpinner();
            showNotification('No passports found on blockchain', 'info');
            return;
        }
        
        // Fetch details for each passport
        const passports = [];
        for (const id of passportIds) {
            const passport = await web3Manager.getPassportFromChain(id);
            passports.push({ id, ...passport });
        }
        
        hideLoadingSpinner();
        displayBlockchainPassports(passports);
        showNotification(`Synced ${passports.length} passport(s)`, 'success');
        
    } catch (error) {
        hideLoadingSpinner();
        showNotification(`Error: ${error.message}`, 'error');
    }
}

/**
 * Generate document hash
 */
async function generateDocumentHash(passportNumber, passportId) {
    const data = `${passportNumber}-${passportId}-${Date.now()}`;
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return `0x${hashHex}`;
}

/**
 * Display transaction info
 */
function displayTransactionInfo(tx) {
    const txInfoDiv = document.getElementById('transactionInfo');
    if (txInfoDiv) {
        txInfoDiv.innerHTML = `
            <div class="alert alert-info">
                <strong>Transaction Hash:</strong><br>
                <code>${tx.transactionHash}</code><br>
                <strong>Block Number:</strong> ${tx.blockNumber}<br>
                <strong>Gas Used:</strong> ${tx.gasUsed}
            </div>
        `;
        txInfoDiv.style.display = 'block';
    }
}

/**
 * Display blockchain passports
 */
function displayBlockchainPassports(passports) {
    const container = document.getElementById('blockchainPassports');
    if (!container) return;
    
    let html = '<div class="blockchain-passports-list">';
    
    passports.forEach(passport => {
        const date = new Date(passport.timestamp * 1000);
        html += `
            <div class="blockchain-passport-card">
                <h5><i class="fas fa-passport"></i> ${passport.passportNumber}</h5>
                <p><strong>Document Hash:</strong> ${passport.documentHash.substring(0, 20)}...</p>
                <p><strong>Stored:</strong> ${date.toLocaleDateString()}</p>
                <p><strong>Status:</strong> <span class="badge ${passport.isActive ? 'bg-success' : 'bg-danger'}">
                    ${passport.isActive ? 'Active' : 'Inactive'}
                </span></p>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

/**
 * Check if wallet is already connected
 */
async function checkWalletConnection() {
    if (typeof window.ethereum !== 'undefined') {
        try {
            const accounts = await window.ethereum.request({ 
                method: 'eth_accounts' 
            });
            
            if (accounts.length > 0) {
                await web3Manager.connectWallet();
                await initializeContract();
                updateWeb3Features(true);
            }
        } catch (error) {
            console.error('Error checking wallet connection:', error);
        }
    }
}

/**
 * Update Web3 features visibility
 */
function updateWeb3Features(connected) {
    const web3Features = document.querySelectorAll('.web3-feature');
    web3Features.forEach(feature => {
        feature.style.display = connected ? 'block' : 'none';
    });
    
    const web3Warnings = document.querySelectorAll('.web3-warning');
    web3Warnings.forEach(warning => {
        warning.style.display = connected ? 'none' : 'block';
    });
}

/**
 * Show loading spinner
 */
function showLoadingSpinner(message) {
    const spinner = document.getElementById('loadingSpinner');
    const spinnerMessage = document.getElementById('spinnerMessage');
    
    if (spinner) {
        spinner.style.display = 'flex';
        if (spinnerMessage) {
            spinnerMessage.textContent = message;
        }
    }
}

/**
 * Hide loading spinner
 */
function hideLoadingSpinner() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-popup`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(notification, container.firstChild);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}
