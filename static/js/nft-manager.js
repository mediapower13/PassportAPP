/**
 * NFT Manager for Passport NFTs
 * Handle minting, transfers, and NFT operations
 */

class NFTManager {
    constructor(web3Manager) {
        this.web3Manager = web3Manager;
        this.nftContract = null;
        this.nftContractAddress = null;
    }

    /**
     * Initialize NFT contract
     */
    async init(contractAddress, contractABI) {
        if (!this.web3Manager.web3) {
            throw new Error('Web3 not initialized');
        }

        this.nftContractAddress = contractAddress;
        this.nftContract = new this.web3Manager.web3.eth.Contract(
            contractABI,
            contractAddress
        );

        console.log('NFT contract initialized at:', contractAddress);
        return true;
    }

    /**
     * Mint new passport NFT
     */
    async mintPassportNFT(passportData) {
        if (!this.nftContract || !this.web3Manager.account) {
            throw new Error('NFT contract or wallet not initialized');
        }

        const {
            passportNumber,
            countryCode,
            issueDate,
            expiryDate,
            ipfsHash
        } = passportData;

        try {
            // Convert dates to timestamps
            const issueDateTimestamp = Math.floor(new Date(issueDate).getTime() / 1000);
            const expiryDateTimestamp = Math.floor(new Date(expiryDate).getTime() / 1000);

            const transaction = this.nftContract.methods.mint(
                this.web3Manager.account,
                passportNumber,
                countryCode,
                issueDateTimestamp,
                expiryDateTimestamp,
                ipfsHash
            );

            const gas = await transaction.estimateGas({ from: this.web3Manager.account });
            const gasPrice = await this.web3Manager.web3.eth.getGasPrice();

            const receipt = await transaction.send({
                from: this.web3Manager.account,
                gas: Math.floor(gas * 1.2),
                gasPrice: gasPrice
            });

            console.log('NFT minted:', receipt);

            // Get token ID from events
            const tokenId = receipt.events.Transfer.returnValues.tokenId;

            return {
                success: true,
                tokenId: tokenId,
                transactionHash: receipt.transactionHash,
                blockNumber: receipt.blockNumber
            };

        } catch (error) {
            console.error('Error minting NFT:', error);
            throw error;
        }
    }

    /**
     * Get NFT metadata
     */
    async getMetadata(tokenId) {
        if (!this.nftContract) {
            throw new Error('NFT contract not initialized');
        }

        try {
            const metadata = await this.nftContract.methods.getPassportMetadata(tokenId).call();

            return {
                passportNumber: metadata[0],
                countryCode: metadata[1],
                issueDate: new Date(metadata[2] * 1000),
                expiryDate: new Date(metadata[3] * 1000),
                ipfsHash: metadata[4],
                isActive: metadata[5]
            };

        } catch (error) {
            console.error('Error getting metadata:', error);
            throw error;
        }
    }

    /**
     * Get user's NFT balance
     */
    async getBalance(address) {
        if (!this.nftContract) {
            throw new Error('NFT contract not initialized');
        }

        const balance = await this.nftContract.methods.balanceOf(address).call();
        return parseInt(balance);
    }

    /**
     * Get NFT owner
     */
    async getOwner(tokenId) {
        if (!this.nftContract) {
            throw new Error('NFT contract not initialized');
        }

        return await this.nftContract.methods.ownerOf(tokenId).call();
    }

    /**
     * Transfer NFT
     */
    async transfer(to, tokenId) {
        if (!this.nftContract || !this.web3Manager.account) {
            throw new Error('NFT contract or wallet not initialized');
        }

        try {
            const transaction = this.nftContract.methods.transferFrom(
                this.web3Manager.account,
                to,
                tokenId
            );

            const gas = await transaction.estimateGas({ from: this.web3Manager.account });
            const gasPrice = await this.web3Manager.web3.eth.getGasPrice();

            const receipt = await transaction.send({
                from: this.web3Manager.account,
                gas: Math.floor(gas * 1.2),
                gasPrice: gasPrice
            });

            return {
                success: true,
                transactionHash: receipt.transactionHash,
                blockNumber: receipt.blockNumber
            };

        } catch (error) {
            console.error('Error transferring NFT:', error);
            throw error;
        }
    }

    /**
     * Approve NFT transfer
     */
    async approve(to, tokenId) {
        if (!this.nftContract || !this.web3Manager.account) {
            throw new Error('NFT contract or wallet not initialized');
        }

        try {
            const transaction = this.nftContract.methods.approve(to, tokenId);

            const gas = await transaction.estimateGas({ from: this.web3Manager.account });
            const gasPrice = await this.web3Manager.web3.eth.getGasPrice();

            const receipt = await transaction.send({
                from: this.web3Manager.account,
                gas: Math.floor(gas * 1.2),
                gasPrice: gasPrice
            });

            return {
                success: true,
                transactionHash: receipt.transactionHash
            };

        } catch (error) {
            console.error('Error approving NFT:', error);
            throw error;
        }
    }

    /**
     * Burn NFT
     */
    async burn(tokenId) {
        if (!this.nftContract || !this.web3Manager.account) {
            throw new Error('NFT contract or wallet not initialized');
        }

        try {
            const transaction = this.nftContract.methods.burn(tokenId);

            const gas = await transaction.estimateGas({ from: this.web3Manager.account });
            const gasPrice = await this.web3Manager.web3.eth.getGasPrice();

            const receipt = await transaction.send({
                from: this.web3Manager.account,
                gas: Math.floor(gas * 1.2),
                gasPrice: gasPrice
            });

            return {
                success: true,
                transactionHash: receipt.transactionHash
            };

        } catch (error) {
            console.error('Error burning NFT:', error);
            throw error;
        }
    }

    /**
     * Update NFT metadata
     */
    async updateMetadata(tokenId, newIpfsHash) {
        if (!this.nftContract || !this.web3Manager.account) {
            throw new Error('NFT contract or wallet not initialized');
        }

        try {
            const transaction = this.nftContract.methods.updateMetadata(
                tokenId,
                newIpfsHash
            );

            const gas = await transaction.estimateGas({ from: this.web3Manager.account });
            const gasPrice = await this.web3Manager.web3.eth.getGasPrice();

            const receipt = await transaction.send({
                from: this.web3Manager.account,
                gas: Math.floor(gas * 1.2),
                gasPrice: gasPrice
            });

            return {
                success: true,
                transactionHash: receipt.transactionHash
            };

        } catch (error) {
            console.error('Error updating metadata:', error);
            throw error;
        }
    }

    /**
     * Deactivate passport NFT
     */
    async deactivatePassport(tokenId) {
        if (!this.nftContract || !this.web3Manager.account) {
            throw new Error('NFT contract or wallet not initialized');
        }

        try {
            const transaction = this.nftContract.methods.deactivatePassport(tokenId);

            const gas = await transaction.estimateGas({ from: this.web3Manager.account });
            const gasPrice = await this.web3Manager.web3.eth.getGasPrice();

            const receipt = await transaction.send({
                from: this.web3Manager.account,
                gas: Math.floor(gas * 1.2),
                gasPrice: gasPrice
            });

            return {
                success: true,
                transactionHash: receipt.transactionHash
            };

        } catch (error) {
            console.error('Error deactivating passport:', error);
            throw error;
        }
    }

    /**
     * Check if passport is expired
     */
    async isExpired(tokenId) {
        if (!this.nftContract) {
            throw new Error('NFT contract not initialized');
        }

        return await this.nftContract.methods.isExpired(tokenId).call();
    }

    /**
     * Get total supply
     */
    async getTotalSupply() {
        if (!this.nftContract) {
            throw new Error('NFT contract not initialized');
        }

        const supply = await this.nftContract.methods.totalSupply().call();
        return parseInt(supply);
    }

    /**
     * Listen to NFT events
     */
    listenToEvents(callback) {
        if (!this.nftContract) {
            throw new Error('NFT contract not initialized');
        }

        // Listen to Transfer events
        this.nftContract.events.Transfer()
            .on('data', (event) => {
                const eventData = {
                    type: 'Transfer',
                    from: event.returnValues.from,
                    to: event.returnValues.to,
                    tokenId: event.returnValues.tokenId,
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                if (callback) callback(eventData);
            })
            .on('error', console.error);

        // Listen to MetadataUpdate events
        this.nftContract.events.MetadataUpdate()
            .on('data', (event) => {
                const eventData = {
                    type: 'MetadataUpdate',
                    tokenId: event.returnValues.tokenId,
                    blockNumber: event.blockNumber,
                    transactionHash: event.transactionHash
                };
                
                if (callback) callback(eventData);
            })
            .on('error', console.error);

        console.log('Listening to NFT events');
    }

    /**
     * Get NFT marketplace link
     */
    getMarketplaceLink(tokenId, marketplace = 'opensea') {
        const chainId = this.web3Manager.chainId;
        const contractAddress = this.nftContractAddress;

        const marketplaces = {
            opensea: {
                1: `https://opensea.io/assets/ethereum/${contractAddress}/${tokenId}`,
                137: `https://opensea.io/assets/matic/${contractAddress}/${tokenId}`,
                11155111: `https://testnets.opensea.io/assets/sepolia/${contractAddress}/${tokenId}`
            },
            rarible: {
                1: `https://rarible.com/token/${contractAddress}:${tokenId}`,
                137: `https://rarible.com/token/polygon/${contractAddress}:${tokenId}`
            }
        };

        return marketplaces[marketplace]?.[chainId] || null;
    }
}

// Export for use in other modules
window.NFTManager = NFTManager;
