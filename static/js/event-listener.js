/**
 * Blockchain Event Listener
 * Real-time monitoring of smart contract events
 */

class BlockchainEventListener {
    constructor(web3Manager) {
        this.web3Manager = web3Manager;
        this.activeListeners = new Map();
        this.eventHistory = [];
        this.maxHistorySize = 100;
    }

    /**
     * Start listening to passport storage events
     */
    async listenToPassportEvents(callback) {
        if (!this.web3Manager.contract) {
            throw new Error('Contract not initialized');
        }

        const contract = this.web3Manager.contract;

        // Listen to PassportStored events
        const storedListener = contract.events.PassportStored()
            .on('data', (event) => {
                const eventData = {
                    type: 'PassportStored',
                    passportId: event.returnValues.passportId,
                    passportNumber: event.returnValues.passportNumber,
                    owner: event.returnValues.owner,
                    timestamp: new Date(event.returnValues.timestamp * 1000),
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                this.addToHistory(eventData);
                if (callback) callback(eventData);
                this.showNotification('New passport stored on blockchain', 'success');
            })
            .on('error', (error) => {
                console.error('PassportStored event error:', error);
                this.showNotification('Event listener error', 'error');
            });

        this.activeListeners.set('PassportStored', storedListener);

        // Listen to PassportUpdated events
        const updatedListener = contract.events.PassportUpdated()
            .on('data', (event) => {
                const eventData = {
                    type: 'PassportUpdated',
                    passportId: event.returnValues.passportId,
                    newDocumentHash: event.returnValues.newDocumentHash,
                    timestamp: new Date(event.returnValues.timestamp * 1000),
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                this.addToHistory(eventData);
                if (callback) callback(eventData);
                this.showNotification('Passport updated on blockchain', 'info');
            })
            .on('error', (error) => {
                console.error('PassportUpdated event error:', error);
            });

        this.activeListeners.set('PassportUpdated', updatedListener);

        // Listen to PassportDeactivated events
        const deactivatedListener = contract.events.PassportDeactivated()
            .on('data', (event) => {
                const eventData = {
                    type: 'PassportDeactivated',
                    passportId: event.returnValues.passportId,
                    timestamp: new Date(event.returnValues.timestamp * 1000),
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                this.addToHistory(eventData);
                if (callback) callback(eventData);
                this.showNotification('Passport deactivated', 'warning');
            })
            .on('error', (error) => {
                console.error('PassportDeactivated event error:', error);
            });

        this.activeListeners.set('PassportDeactivated', deactivatedListener);

        console.log('Started listening to blockchain events');
        return true;
    }

    /**
     * Listen to verification events
     */
    async listenToVerificationEvents(callback) {
        if (!this.web3Manager.verificationContract) {
            console.warn('Verification contract not initialized');
            return false;
        }

        const contract = this.web3Manager.verificationContract;

        // Listen to VerificationRequested events
        const requestedListener = contract.events.VerificationRequested()
            .on('data', (event) => {
                const eventData = {
                    type: 'VerificationRequested',
                    requestId: event.returnValues.requestId,
                    passportId: event.returnValues.passportId,
                    requester: event.returnValues.requester,
                    verifier: event.returnValues.verifier,
                    timestamp: new Date(event.returnValues.timestamp * 1000),
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                this.addToHistory(eventData);
                if (callback) callback(eventData);
                this.showNotification('Verification requested', 'info');
            })
            .on('error', (error) => {
                console.error('VerificationRequested event error:', error);
            });

        this.activeListeners.set('VerificationRequested', requestedListener);

        // Listen to VerificationApproved events
        const approvedListener = contract.events.VerificationApproved()
            .on('data', (event) => {
                const eventData = {
                    type: 'VerificationApproved',
                    requestId: event.returnValues.requestId,
                    timestamp: new Date(event.returnValues.timestamp * 1000),
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                this.addToHistory(eventData);
                if (callback) callback(eventData);
                this.showNotification('Verification approved', 'success');
            })
            .on('error', (error) => {
                console.error('VerificationApproved event error:', error);
            });

        this.activeListeners.set('VerificationApproved', approvedListener);

        console.log('Started listening to verification events');
        return true;
    }

    /**
     * Get past events from blockchain
     */
    async getPastEvents(eventName, fromBlock = 0, toBlock = 'latest') {
        if (!this.web3Manager.contract) {
            throw new Error('Contract not initialized');
        }

        try {
            const events = await this.web3Manager.contract.getPastEvents(eventName, {
                fromBlock: fromBlock,
                toBlock: toBlock
            });

            return events.map(event => ({
                type: event.event,
                ...event.returnValues,
                blockNumber: event.blockNumber,
                transactionHash: event.transactionHash,
                timestamp: new Date(event.returnValues.timestamp * 1000)
            }));
        } catch (error) {
            console.error('Error fetching past events:', error);
            throw error;
        }
    }

    /**
     * Stop listening to specific event
     */
    stopListening(eventName) {
        const listener = this.activeListeners.get(eventName);
        if (listener) {
            listener.unsubscribe();
            this.activeListeners.delete(eventName);
            console.log(`Stopped listening to ${eventName}`);
        }
    }

    /**
     * Stop all event listeners
     */
    stopAllListeners() {
        this.activeListeners.forEach((listener, eventName) => {
            listener.unsubscribe();
            console.log(`Stopped listening to ${eventName}`);
        });
        this.activeListeners.clear();
    }

    /**
     * Add event to history
     */
    addToHistory(eventData) {
        this.eventHistory.unshift(eventData);
        
        // Limit history size
        if (this.eventHistory.length > this.maxHistorySize) {
            this.eventHistory.pop();
        }

        // Store in localStorage
        this.saveHistoryToStorage();
    }

    /**
     * Get event history
     */
    getHistory(limit = 20) {
        return this.eventHistory.slice(0, limit);
    }

    /**
     * Clear event history
     */
    clearHistory() {
        this.eventHistory = [];
        localStorage.removeItem('blockchain_event_history');
    }

    /**
     * Save history to localStorage
     */
    saveHistoryToStorage() {
        try {
            localStorage.setItem(
                'blockchain_event_history',
                JSON.stringify(this.eventHistory)
            );
        } catch (error) {
            console.error('Error saving event history:', error);
        }
    }

    /**
     * Load history from localStorage
     */
    loadHistoryFromStorage() {
        try {
            const saved = localStorage.getItem('blockchain_event_history');
            if (saved) {
                this.eventHistory = JSON.parse(saved);
            }
        } catch (error) {
            console.error('Error loading event history:', error);
        }
    }

    /**
     * Show notification for events
     */
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show blockchain-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            <i class="fas fa-cube me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }

    /**
     * Display event history in UI
     */
    displayEventHistory(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const events = this.getHistory();
        
        if (events.length === 0) {
            container.innerHTML = '<p class="text-muted">No events recorded yet</p>';
            return;
        }

        const html = events.map(event => `
            <div class="event-item mb-2 p-3 border rounded">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">
                            <i class="fas fa-circle text-primary" style="font-size: 8px;"></i>
                            ${event.type}
                        </h6>
                        <small class="text-muted">
                            ${event.timestamp.toLocaleString()}
                        </small>
                    </div>
                    <span class="badge bg-secondary">Block ${event.blockNumber}</span>
                </div>
                <div class="mt-2">
                    <small class="text-muted font-monospace">
                        ${event.transactionHash.substring(0, 20)}...
                    </small>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// Add animation CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .blockchain-notification {
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .event-item {
        transition: all 0.2s;
    }
    
    .event-item:hover {
        background-color: #f8f9fa;
        transform: translateX(5px);
    }
`;
document.head.appendChild(style);

// Export for use in other modules
window.BlockchainEventListener = BlockchainEventListener;
