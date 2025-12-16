// IPFS Integration for Document Storage

class IPFSManager {
    constructor() {
        this.pinataApiKey = null;
        this.pinataSecretKey = null;
        this.ipfsGateway = 'https://ipfs.io/ipfs/';
    }

    /**
     * Initialize IPFS with Pinata credentials
     */
    init(apiKey, secretKey) {
        this.pinataApiKey = apiKey;
        this.pinataSecretKey = secretKey;
    }

    /**
     * Upload file to IPFS via Pinata
     */
    async uploadFile(file) {
        try {
            const formData = new FormData();
            formData.append('file', file);

            const metadata = JSON.stringify({
                name: file.name,
                keyvalues: {
                    app: 'PassportApp',
                    timestamp: Date.now()
                }
            });
            formData.append('pinataMetadata', metadata);

            const options = JSON.stringify({
                cidVersion: 1
            });
            formData.append('pinataOptions', options);

            const response = await fetch('https://api.pinata.cloud/pinning/pinFileToIPFS', {
                method: 'POST',
                headers: {
                    'pinata_api_key': this.pinataApiKey,
                    'pinata_secret_api_key': this.pinataSecretKey
                },
                body: formData
            });

            const result = await response.json();
            
            if (result.IpfsHash) {
                return {
                    success: true,
                    hash: result.IpfsHash,
                    url: `${this.ipfsGateway}${result.IpfsHash}`
                };
            } else {
                throw new Error('Failed to upload to IPFS');
            }

        } catch (error) {
            console.error('IPFS upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Upload JSON data to IPFS
     */
    async uploadJSON(data) {
        try {
            const response = await fetch('https://api.pinata.cloud/pinning/pinJSONToIPFS', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'pinata_api_key': this.pinataApiKey,
                    'pinata_secret_api_key': this.pinataSecretKey
                },
                body: JSON.stringify({
                    pinataContent: data,
                    pinataMetadata: {
                        name: 'passport-metadata.json',
                        keyvalues: {
                            app: 'PassportApp',
                            timestamp: Date.now()
                        }
                    }
                })
            });

            const result = await response.json();

            if (result.IpfsHash) {
                return {
                    success: true,
                    hash: result.IpfsHash,
                    url: `${this.ipfsGateway}${result.IpfsHash}`
                };
            } else {
                throw new Error('Failed to upload JSON to IPFS');
            }

        } catch (error) {
            console.error('IPFS JSON upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Retrieve file from IPFS
     */
    async retrieveFile(ipfsHash) {
        try {
            const url = `${this.ipfsGateway}${ipfsHash}`;
            const response = await fetch(url);

            if (response.ok) {
                return {
                    success: true,
                    data: await response.blob()
                };
            } else {
                throw new Error('Failed to retrieve from IPFS');
            }

        } catch (error) {
            console.error('IPFS retrieve error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Retrieve JSON from IPFS
     */
    async retrieveJSON(ipfsHash) {
        try {
            const url = `${this.ipfsGateway}${ipfsHash}`;
            const response = await fetch(url);

            if (response.ok) {
                return {
                    success: true,
                    data: await response.json()
                };
            } else {
                throw new Error('Failed to retrieve JSON from IPFS');
            }

        } catch (error) {
            console.error('IPFS retrieve error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Unpin file from IPFS (remove from Pinata)
     */
    async unpinFile(ipfsHash) {
        try {
            const response = await fetch(`https://api.pinata.cloud/pinning/unpin/${ipfsHash}`, {
                method: 'DELETE',
                headers: {
                    'pinata_api_key': this.pinataApiKey,
                    'pinata_secret_api_key': this.pinataSecretKey
                }
            });

            if (response.ok) {
                return {
                    success: true,
                    message: 'File unpinned successfully'
                };
            } else {
                throw new Error('Failed to unpin file');
            }

        } catch (error) {
            console.error('IPFS unpin error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Encrypt file before uploading to IPFS
     */
    async encryptAndUpload(file, encryptionKey) {
        try {
            // Read file as ArrayBuffer
            const fileBuffer = await file.arrayBuffer();

            // Import encryption key
            const key = await crypto.subtle.importKey(
                'raw',
                new TextEncoder().encode(encryptionKey.padEnd(32, '0').slice(0, 32)),
                { name: 'AES-GCM' },
                false,
                ['encrypt']
            );

            // Generate IV
            const iv = crypto.getRandomValues(new Uint8Array(12));

            // Encrypt data
            const encryptedData = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv: iv },
                key,
                fileBuffer
            );

            // Combine IV and encrypted data
            const combinedData = new Uint8Array(iv.length + encryptedData.byteLength);
            combinedData.set(iv, 0);
            combinedData.set(new Uint8Array(encryptedData), iv.length);

            // Create encrypted file
            const encryptedFile = new File(
                [combinedData],
                `encrypted_${file.name}`,
                { type: 'application/octet-stream' }
            );

            // Upload to IPFS
            return await this.uploadFile(encryptedFile);

        } catch (error) {
            console.error('Encrypt and upload error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Retrieve and decrypt file from IPFS
     */
    async retrieveAndDecrypt(ipfsHash, encryptionKey) {
        try {
            // Retrieve encrypted file
            const result = await this.retrieveFile(ipfsHash);
            
            if (!result.success) {
                throw new Error(result.error);
            }

            // Read as ArrayBuffer
            const encryptedBuffer = await result.data.arrayBuffer();
            const encryptedData = new Uint8Array(encryptedBuffer);

            // Extract IV and ciphertext
            const iv = encryptedData.slice(0, 12);
            const ciphertext = encryptedData.slice(12);

            // Import decryption key
            const key = await crypto.subtle.importKey(
                'raw',
                new TextEncoder().encode(encryptionKey.padEnd(32, '0').slice(0, 32)),
                { name: 'AES-GCM' },
                false,
                ['decrypt']
            );

            // Decrypt data
            const decryptedData = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv: iv },
                key,
                ciphertext
            );

            return {
                success: true,
                data: new Blob([decryptedData])
            };

        } catch (error) {
            console.error('Retrieve and decrypt error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Initialize IPFS Manager
const ipfsManager = new IPFSManager();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IPFSManager;
}
