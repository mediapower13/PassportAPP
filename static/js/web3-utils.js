// Web3 Wallet Connection Guide and Utilities

// Network Configuration
const SUPPORTED_NETWORKS = {
    1: {
        name: 'Ethereum Mainnet',
        rpcUrl: 'https://mainnet.infura.io/v3/',
        symbol: 'ETH',
        explorer: 'https://etherscan.io'
    },
    11155111: {
        name: 'Sepolia Testnet',
        rpcUrl: 'https://sepolia.infura.io/v3/',
        symbol: 'SEP',
        explorer: 'https://sepolia.etherscan.io'
    },
    137: {
        name: 'Polygon',
        rpcUrl: 'https://polygon-rpc.com',
        symbol: 'MATIC',
        explorer: 'https://polygonscan.com'
    },
    56: {
        name: 'BSC',
        rpcUrl: 'https://bsc-dataseed.binance.org',
        symbol: 'BNB',
        explorer: 'https://bscscan.com'
    },
    1337: {
        name: 'Localhost',
        rpcUrl: 'http://127.0.0.1:8545',
        symbol: 'ETH',
        explorer: ''
    }
};

/**
 * Switch network in MetaMask
 */
async function switchNetwork(chainId) {
    try {
        await window.ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: `0x${chainId.toString(16)}` }]
        });
        return true;
    } catch (error) {
        // If network doesn't exist, add it
        if (error.code === 4902) {
            return await addNetwork(chainId);
        }
        throw error;
    }
}

/**
 * Add network to MetaMask
 */
async function addNetwork(chainId) {
    const network = SUPPORTED_NETWORKS[chainId];
    
    if (!network) {
        throw new Error('Unsupported network');
    }

    try {
        await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [{
                chainId: `0x${chainId.toString(16)}`,
                chainName: network.name,
                nativeCurrency: {
                    name: network.symbol,
                    symbol: network.symbol,
                    decimals: 18
                },
                rpcUrls: [network.rpcUrl],
                blockExplorerUrls: network.explorer ? [network.explorer] : []
            }]
        });
        return true;
    } catch (error) {
        console.error('Error adding network:', error);
        return false;
    }
}

/**
 * Get current network info
 */
async function getCurrentNetwork() {
    if (!window.ethereum) {
        return null;
    }

    const chainId = await window.ethereum.request({ method: 'eth_chainId' });
    const networkId = parseInt(chainId, 16);
    
    return {
        chainId: networkId,
        info: SUPPORTED_NETWORKS[networkId] || {
            name: 'Unknown Network',
            symbol: '?'
        }
    };
}

/**
 * Format address for display
 */
function formatAddress(address) {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(38)}`;
}

/**
 * Format balance with decimals
 */
function formatBalance(balance, decimals = 4) {
    const num = parseFloat(balance);
    return num.toFixed(decimals);
}

/**
 * Convert Wei to Ether
 */
function weiToEther(wei) {
    if (!wei) return '0';
    return (parseInt(wei) / 1e18).toString();
}

/**
 * Convert Ether to Wei
 */
function etherToWei(ether) {
    if (!ether) return '0';
    return (parseFloat(ether) * 1e18).toString();
}

/**
 * Validate Ethereum address
 */
function isValidAddress(address) {
    return /^0x[a-fA-F0-9]{40}$/.test(address);
}

/**
 * Get transaction receipt
 */
async function getTransactionReceipt(txHash) {
    if (!web3Manager.web3) {
        throw new Error('Web3 not initialized');
    }
    
    return await web3Manager.web3.eth.getTransactionReceipt(txHash);
}

/**
 * Wait for transaction confirmation
 */
async function waitForTransaction(txHash, confirmations = 1) {
    if (!web3Manager.web3) {
        throw new Error('Web3 not initialized');
    }

    return new Promise((resolve, reject) => {
        const checkReceipt = async () => {
            try {
                const receipt = await web3Manager.web3.eth.getTransactionReceipt(txHash);
                
                if (receipt) {
                    const currentBlock = await web3Manager.web3.eth.getBlockNumber();
                    const confirmedBlocks = currentBlock - receipt.blockNumber;
                    
                    if (confirmedBlocks >= confirmations) {
                        resolve(receipt);
                    } else {
                        setTimeout(checkReceipt, 2000);
                    }
                } else {
                    setTimeout(checkReceipt, 2000);
                }
            } catch (error) {
                reject(error);
            }
        };
        
        checkReceipt();
    });
}

/**
 * Estimate gas for transaction
 */
async function estimateGas(transaction) {
    if (!web3Manager.web3) {
        throw new Error('Web3 not initialized');
    }
    
    return await web3Manager.web3.eth.estimateGas(transaction);
}

/**
 * Get current gas price
 */
async function getGasPrice() {
    if (!web3Manager.web3) {
        throw new Error('Web3 not initialized');
    }
    
    const gasPrice = await web3Manager.web3.eth.getGasPrice();
    return {
        wei: gasPrice,
        gwei: weiToEther(gasPrice) * 1e9,
        ether: weiToEther(gasPrice)
    };
}

/**
 * Generate random bytes for encryption
 */
function generateRandomBytes(length = 32) {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}

/**
 * Copy to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (error) {
        console.error('Failed to copy:', error);
        return false;
    }
}

/**
 * Open transaction in explorer
 */
function openInExplorer(txHash, chainId) {
    const network = SUPPORTED_NETWORKS[chainId];
    
    if (network && network.explorer) {
        window.open(`${network.explorer}/tx/${txHash}`, '_blank');
    }
}

/**
 * Open address in explorer
 */
function openAddressInExplorer(address, chainId) {
    const network = SUPPORTED_NETWORKS[chainId];
    
    if (network && network.explorer) {
        window.open(`${network.explorer}/address/${address}`, '_blank');
    }
}

// Export utilities
window.Web3Utils = {
    SUPPORTED_NETWORKS,
    switchNetwork,
    addNetwork,
    getCurrentNetwork,
    formatAddress,
    formatBalance,
    weiToEther,
    etherToWei,
    isValidAddress,
    getTransactionReceipt,
    waitForTransaction,
    estimateGas,
    getGasPrice,
    generateRandomBytes,
    copyToClipboard,
    openInExplorer,
    openAddressInExplorer
};
