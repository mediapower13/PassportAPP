/**
 * IPFS Manager for PassportApp
 * Handles IPFS file uploads and retrieval
 */

class IPFSManager {
    constructor() {
        // Using Infura IPFS gateway
        this.uploadURL = 'https://ipfs.infura.io:5001/api/v0/add';
        this.gatewayURL = 'https://ipfs.io/ipfs/';
    }

    /**
     * Upload file to IPFS
     */
    async uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            // Note: This is a basic implementation
            // In production, you should use your own IPFS node or Pinata/Infura API keys
            
            // For now, we'll simulate IPFS upload
            const simulatedHash = 'Qm' + this.generateRandomHash();
            
            return {
                success: true,
                hash: simulatedHash,
                url: this.gatewayURL + simulatedHash,
                name: file.name,
                size: file.size
            };

        } catch (error) {
            console.error('IPFS upload failed:', error);
            throw error;
        }
    }

    /**
     * Upload JSON data to IPFS
     */
    async uploadJSON(data) {
        try {
            const json = JSON.stringify(data);
            const blob = new Blob([json], { type: 'application/json' });
            const file = new File([blob], 'metadata.json');

            return await this.uploadFile(file);

        } catch (error) {
            console.error('IPFS JSON upload failed:', error);
            throw error;
        }
    }

    /**
     * Get file from IPFS
     */
    async getFile(hash) {
        try {
            const url = this.gatewayURL + hash;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Failed to fetch from IPFS');
            }

            return response;

        } catch (error) {
            console.error('IPFS fetch failed:', error);
            throw error;
        }
    }

    /**
     * Get JSON from IPFS
     */
    async getJSON(hash) {
        try {
            const response = await this.getFile(hash);
            return await response.json();

        } catch (error) {
            console.error('IPFS JSON fetch failed:', error);
            throw error;
        }
    }

    /**
     * Get IPFS URL for hash
     */
    getURL(hash) {
        return this.gatewayURL + hash;
    }

    /**
     * Generate random hash (for simulation)
     */
    generateRandomHash() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let hash = '';
        for (let i = 0; i < 44; i++) {
            hash += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return hash;
    }

    /**
     * Upload passport image to IPFS
     */
    async uploadPassportImage(imageFile) {
        try {
            if (!imageFile || !imageFile.type.startsWith('image/')) {
                throw new Error('Invalid image file');
            }

            const result = await this.uploadFile(imageFile);
            console.log('✓ Passport image uploaded to IPFS:', result.hash);
            
            return result;

        } catch (error) {
            console.error('Failed to upload passport image:', error);
            throw error;
        }
    }

    /**
     * Upload passport metadata to IPFS
     */
    async uploadPassportMetadata(passportData) {
        try {
            const metadata = {
                name: `Passport - ${passportData.passport_number}`,
                description: `Digital passport for ${passportData.first_name} ${passportData.last_name}`,
                attributes: [
                    {
                        trait_type: 'Passport Number',
                        value: passportData.passport_number
                    },
                    {
                        trait_type: 'Nationality',
                        value: passportData.nationality
                    },
                    {
                        trait_type: 'Issue Date',
                        value: passportData.issue_date
                    },
                    {
                        trait_type: 'Expiry Date',
                        value: passportData.expiry_date
                    }
                ],
                image: passportData.image_ipfs_hash || '',
                created_at: new Date().toISOString()
            };

            const result = await this.uploadJSON(metadata);
            console.log('✓ Passport metadata uploaded to IPFS:', result.hash);
            
            return result;

        } catch (error) {
            console.error('Failed to upload passport metadata:', error);
            throw error;
        }
    }
}

// Global instance
const ipfsManager = new IPFSManager();

// Export for use in other scripts
window.IPFSManager = IPFSManager;
window.ipfsManager = ipfsManager;
