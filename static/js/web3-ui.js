/**
 * Web3 UI Integration for PassportApp
 * Handles UI updates for Web3 functionality
 */

// Update Web3 status in UI
async function updateWeb3Status() {
    try {
        const status = await web3Manager.getStatus();
        
        const statusElement = document.getElementById('web3Status');
        if (statusElement) {
            if (status.connected && status.wallet_address) {
                statusElement.textContent = 'Connected';
                statusElement.className = 'stat-value text-success';
            } else {
                statusElement.textContent = 'Not Connected';
                statusElement.className = 'stat-value text-warning';
            }
        }

        const walletElement = document.getElementById('walletAddress');
        if (walletElement && status.wallet_address) {
            walletElement.textContent = web3Manager.formatAddress(status.wallet_address);
        }

        const balanceElement = document.getElementById('walletBalance');
        if (balanceElement && status.wallet_address) {
            const balance = await web3Manager.getBalance();
            balanceElement.textContent = parseFloat(balance).toFixed(4) + ' ETH';
        }
    } catch (error) {
        console.error('Failed to update Web3 status:', error);
    }
}

// Handle wallet connection button click
async function handleConnectWallet() {
    const connectBtn = document.getElementById('connectWalletBtn');
    
    try {
        if (connectBtn) {
            connectBtn.disabled = true;
            connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Connecting...';
        }

        await web3Manager.connectWallet();
        
        // Update UI
        await updateWeb3Status();
        
        // Show success message
        showNotification('Wallet connected successfully!', 'success');
        
        // Update button
        if (connectBtn) {
            connectBtn.innerHTML = '<i class="fas fa-check"></i> Connected';
            connectBtn.className = 'btn btn-success';
        }

        // Reload page to update all Web3 elements
        setTimeout(() => location.reload(), 1000);

    } catch (error) {
        console.error('Connection failed:', error);
        showNotification(error.message || 'Failed to connect wallet', 'error');
        
        if (connectBtn) {
            connectBtn.disabled = false;
            connectBtn.innerHTML = '<i class="fas fa-wallet"></i> Connect Wallet';
        }
    }
}

// Handle wallet disconnection
async function handleDisconnectWallet() {
    try {
        await web3Manager.disconnectWallet();
        showNotification('Wallet disconnected', 'info');
        setTimeout(() => location.reload(), 1000);
    } catch (error) {
        console.error('Disconnection failed:', error);
        showNotification('Failed to disconnect wallet', 'error');
    }
}

// Store passport on blockchain
async function storePassportOnBlockchain(passportId) {
    const storeBtn = document.getElementById('storeBlockchainBtn');
    
    try {
        if (!web3Manager.isConnected()) {
            showNotification('Please connect your wallet first', 'warning');
            return;
        }

        if (storeBtn) {
            storeBtn.disabled = true;
            storeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Storing...';
        }

        const result = await web3Manager.storePassport(passportId);
        
        showNotification('Passport stored on blockchain!', 'success');
        
        if (result.tx_hash) {
            console.log('Transaction hash:', result.tx_hash);
        }

        if (storeBtn) {
            storeBtn.innerHTML = '<i class="fas fa-check"></i> Stored on Blockchain';
            storeBtn.className = 'btn btn-success btn-sm';
        }

    } catch (error) {
        console.error('Failed to store passport:', error);
        showNotification(error.message || 'Failed to store on blockchain', 'error');
        
        if (storeBtn) {
            storeBtn.disabled = false;
            storeBtn.innerHTML = '<i class="fas fa-link"></i> Store on Blockchain';
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Initialize Web3 UI on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Update status on load
    await updateWeb3Status();

    // Add event listeners
    const connectBtn = document.getElementById('connectWalletBtn');
    if (connectBtn) {
        connectBtn.addEventListener('click', handleConnectWallet);
    }

    const disconnectBtn = document.getElementById('disconnectWalletBtn');
    if (disconnectBtn) {
        disconnectBtn.addEventListener('click', handleDisconnectWallet);
    }

    // Update status every 30 seconds
    setInterval(updateWeb3Status, 30000);
});

// Export functions for use in other scripts
window.Web3UI = {
    updateWeb3Status,
    handleConnectWallet,
    handleDisconnectWallet,
    storePassportOnBlockchain,
    showNotification
};
