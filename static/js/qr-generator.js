/**
 * QR Code Generator for Passport Data
 * Generate QR codes for passport verification and sharing
 */

class PassportQRGenerator {
    constructor() {
        this.qrCodeLib = null;
        this.loadQRLibrary();
    }

    /**
     * Load QR code library
     */
    loadQRLibrary() {
        if (typeof QRCode === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
            script.onload = () => {
                this.qrCodeLib = QRCode;
                console.log('QR Code library loaded');
            };
            document.head.appendChild(script);
        } else {
            this.qrCodeLib = QRCode;
        }
    }

    /**
     * Generate QR code for passport data
     */
    generatePassportQR(passportData, containerId, options = {}) {
        if (!this.qrCodeLib) {
            console.error('QR Code library not loaded');
            return null;
        }

        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return null;
        }

        // Clear existing QR code
        container.innerHTML = '';

        // Prepare data
        const qrData = {
            type: 'passport',
            passportNumber: passportData.passportNumber,
            owner: passportData.owner,
            documentHash: passportData.documentHash,
            timestamp: passportData.timestamp,
            blockchainId: passportData.blockchainId
        };

        const dataString = JSON.stringify(qrData);

        // Default options
        const qrOptions = {
            width: options.width || 256,
            height: options.height || 256,
            colorDark: options.colorDark || '#000000',
            colorLight: options.colorLight || '#ffffff',
            correctLevel: QRCode.CorrectLevel.H
        };

        // Generate QR code
        new QRCode(container, {
            text: dataString,
            ...qrOptions
        });

        return qrData;
    }

    /**
     * Generate verification QR code
     */
    generateVerificationQR(verificationUrl, containerId, options = {}) {
        if (!this.qrCodeLib) {
            console.error('QR Code library not loaded');
            return null;
        }

        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return null;
        }

        container.innerHTML = '';

        const qrOptions = {
            width: options.width || 200,
            height: options.height || 200,
            colorDark: options.colorDark || '#667eea',
            colorLight: options.colorLight || '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        };

        new QRCode(container, {
            text: verificationUrl,
            ...qrOptions
        });

        return verificationUrl;
    }

    /**
     * Generate blockchain transaction QR code
     */
    generateTransactionQR(transactionHash, network, containerId) {
        const explorerUrls = {
            1: `https://etherscan.io/tx/${transactionHash}`,
            11155111: `https://sepolia.etherscan.io/tx/${transactionHash}`,
            137: `https://polygonscan.com/tx/${transactionHash}`,
            56: `https://bscscan.com/tx/${transactionHash}`
        };

        const url = explorerUrls[network] || transactionHash;

        return this.generateVerificationQR(url, containerId, {
            colorDark: '#28a745'
        });
    }

    /**
     * Generate wallet connect QR code
     */
    generateWalletConnectQR(wcUri, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        container.innerHTML = '';

        new QRCode(container, {
            text: wcUri,
            width: 300,
            height: 300,
            colorDark: '#3396FF',
            colorLight: '#ffffff',
            correctLevel: QRCode.CorrectLevel.M
        });

        return wcUri;
    }

    /**
     * Create downloadable QR code
     */
    createDownloadableQR(qrData, filename = 'passport_qr.png') {
        const tempContainer = document.createElement('div');
        tempContainer.style.display = 'none';
        document.body.appendChild(tempContainer);

        new QRCode(tempContainer, {
            text: JSON.stringify(qrData),
            width: 512,
            height: 512,
            correctLevel: QRCode.CorrectLevel.H
        });

        setTimeout(() => {
            const canvas = tempContainer.querySelector('canvas');
            if (canvas) {
                const link = document.createElement('a');
                link.download = filename;
                link.href = canvas.toDataURL('image/png');
                link.click();
            }
            document.body.removeChild(tempContainer);
        }, 100);
    }

    /**
     * Parse QR code data
     */
    parseQRData(qrDataString) {
        try {
            const data = JSON.parse(qrDataString);
            
            if (data.type === 'passport') {
                return {
                    valid: true,
                    type: 'passport',
                    data: data
                };
            }

            return {
                valid: false,
                error: 'Invalid QR code format'
            };

        } catch (error) {
            return {
                valid: false,
                error: 'Failed to parse QR code data'
            };
        }
    }

    /**
     * Create QR code with logo
     */
    createQRWithLogo(data, containerId, logoUrl) {
        const container = document.getElementById(containerId);
        if (!container) return null;

        container.innerHTML = '';

        // Create QR code
        new QRCode(container, {
            text: data,
            width: 300,
            height: 300,
            correctLevel: QRCode.CorrectLevel.H
        });

        // Add logo overlay
        setTimeout(() => {
            const canvas = container.querySelector('canvas');
            if (canvas) {
                const ctx = canvas.getContext('2d');
                const img = new Image();
                img.onload = () => {
                    const logoSize = 60;
                    const x = (canvas.width - logoSize) / 2;
                    const y = (canvas.height - logoSize) / 2;

                    // White background for logo
                    ctx.fillStyle = 'white';
                    ctx.fillRect(x - 5, y - 5, logoSize + 10, logoSize + 10);

                    // Draw logo
                    ctx.drawImage(img, x, y, logoSize, logoSize);
                };
                img.src = logoUrl;
            }
        }, 100);
    }

    /**
     * Generate shareable verification link QR
     */
    generateShareQR(passportId, containerId) {
        const baseUrl = window.location.origin;
        const verificationUrl = `${baseUrl}/verify/${passportId}`;

        const container = document.getElementById(containerId);
        if (!container) return null;

        container.innerHTML = `
            <div class="text-center">
                <div id="qr-code-canvas"></div>
                <p class="mt-3 small text-muted font-monospace">${verificationUrl}</p>
                <button class="btn btn-sm btn-outline-primary mt-2" onclick="copyToClipboard('${verificationUrl}')">
                    <i class="fas fa-copy me-1"></i>Copy Link
                </button>
            </div>
        `;

        this.generateVerificationQR(verificationUrl, 'qr-code-canvas');

        return verificationUrl;
    }

    /**
     * Scan QR code from camera
     */
    async scanQRFromCamera(videoElementId, resultCallback) {
        try {
            const video = document.getElementById(videoElementId);
            if (!video) {
                throw new Error('Video element not found');
            }

            // Request camera access
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' }
            });

            video.srcObject = stream;
            video.play();

            // Note: Actual QR scanning would require a library like jsQR
            console.log('Camera started for QR scanning');

            return stream;

        } catch (error) {
            console.error('Error accessing camera:', error);
            throw error;
        }
    }

    /**
     * Stop camera stream
     */
    stopCamera(stream) {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    }
}

// Helper function for copying to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Link copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 250px;
    `;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Export for use in other modules
window.PassportQRGenerator = PassportQRGenerator;
