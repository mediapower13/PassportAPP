"""
Email notification system for PassportApp
Send email notifications for important events
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime


class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None):
        self.smtp_server = smtp_server or os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', '587'))
        self.username = username or os.environ.get('SMTP_USERNAME')
        self.password = password or os.environ.get('SMTP_PASSWORD')
        self.from_email = os.environ.get('FROM_EMAIL', self.username)
    
    def send_email(self, to_email, subject, body, html=False, attachments=None):
        """Send email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Attach body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Attach files
            if attachments:
                for filepath in attachments:
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    
                    encoders.encode_base64(part)
                    filename = os.path.basename(filepath)
                    part.add_header('Content-Disposition', f'attachment; filename={filename}')
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True, 'Email sent successfully'
        
        except Exception as e:
            return False, f'Failed to send email: {str(e)}'
    
    def send_welcome_email(self, to_email, username):
        """Send welcome email to new user"""
        subject = 'Welcome to PassportApp!'
        body = f"""
        <html>
        <body>
            <h2>Welcome to PassportApp, {username}!</h2>
            <p>Thank you for registering with our blockchain-based passport management system.</p>
            <p>You can now:</p>
            <ul>
                <li>Create and manage digital passports</li>
                <li>Mint NFTs for your passports</li>
                <li>Trade on our secure marketplace</li>
                <li>Track all blockchain transactions</li>
            </ul>
            <p>Get started by logging in to your account!</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_passport_created_email(self, to_email, passport_number):
        """Send email when passport is created"""
        subject = 'Passport Created Successfully'
        body = f"""
        <html>
        <body>
            <h2>Passport Created</h2>
            <p>Your passport has been successfully created!</p>
            <p><strong>Passport Number:</strong> {passport_number}</p>
            <p>You can now mint an NFT for this passport to secure it on the blockchain.</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_nft_minted_email(self, to_email, token_id, passport_number, tx_hash):
        """Send email when NFT is minted"""
        subject = 'NFT Minted Successfully'
        body = f"""
        <html>
        <body>
            <h2>NFT Minted</h2>
            <p>Your passport NFT has been successfully minted on the blockchain!</p>
            <p><strong>Token ID:</strong> {token_id}</p>
            <p><strong>Passport Number:</strong> {passport_number}</p>
            <p><strong>Transaction Hash:</strong> {tx_hash}</p>
            <p>Your NFT is now secured on the blockchain and can be traded on the marketplace.</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_nft_sold_email(self, to_email, token_id, price, buyer_address):
        """Send email when NFT is sold"""
        subject = 'Your NFT Has Been Sold'
        body = f"""
        <html>
        <body>
            <h2>NFT Sold</h2>
            <p>Congratulations! Your NFT has been sold on the marketplace.</p>
            <p><strong>Token ID:</strong> {token_id}</p>
            <p><strong>Sale Price:</strong> {price} ETH</p>
            <p><strong>Buyer Address:</strong> {buyer_address}</p>
            <p>The funds have been transferred to your wallet.</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_nft_purchased_email(self, to_email, token_id, price, seller_address):
        """Send email when NFT is purchased"""
        subject = 'NFT Purchase Successful'
        body = f"""
        <html>
        <body>
            <h2>NFT Purchased</h2>
            <p>Congratulations! You have successfully purchased an NFT.</p>
            <p><strong>Token ID:</strong> {token_id}</p>
            <p><strong>Purchase Price:</strong> {price} ETH</p>
            <p><strong>Seller Address:</strong> {seller_address}</p>
            <p>The NFT has been transferred to your wallet.</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_security_alert_email(self, to_email, alert_type, details):
        """Send security alert email"""
        subject = f'Security Alert: {alert_type}'
        body = f"""
        <html>
        <body>
            <h2 style="color: red;">Security Alert</h2>
            <p>A security event has been detected on your account.</p>
            <p><strong>Alert Type:</strong> {alert_type}</p>
            <p><strong>Details:</strong> {details}</p>
            <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            <p>If this was not you, please secure your account immediately.</p>
            <br>
            <p>Best regards,<br>The PassportApp Security Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_password_reset_email(self, to_email, reset_token):
        """Send password reset email"""
        reset_link = f"https://passportapp.com/reset-password?token={reset_token}"
        
        subject = 'Password Reset Request'
        body = f"""
        <html>
        <body>
            <h2>Password Reset</h2>
            <p>You requested to reset your password.</p>
            <p>Click the link below to reset your password:</p>
            <p><a href="{reset_link}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <p>If you did not request this, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)
    
    def send_transaction_confirmation_email(self, to_email, tx_type, tx_hash, status):
        """Send transaction confirmation email"""
        subject = f'Transaction {status.title()}: {tx_type}'
        
        status_color = 'green' if status == 'confirmed' else 'orange'
        
        body = f"""
        <html>
        <body>
            <h2>Transaction {status.title()}</h2>
            <p style="color: {status_color};">Your blockchain transaction has been {status}.</p>
            <p><strong>Transaction Type:</strong> {tx_type}</p>
            <p><strong>Transaction Hash:</strong> {tx_hash}</p>
            <p><strong>Status:</strong> {status.title()}</p>
            <p>You can view the transaction on the blockchain explorer.</p>
            <br>
            <p>Best regards,<br>The PassportApp Team</p>
        </body>
        </html>
        """
        
        return self.send_email(to_email, subject, body, html=True)


# Global email service instance
email_service = EmailService()


def send_notification_email(to_email, notification_type, **kwargs):
    """Send notification email based on type"""
    if notification_type == 'welcome':
        return email_service.send_welcome_email(to_email, kwargs.get('username'))
    elif notification_type == 'passport_created':
        return email_service.send_passport_created_email(to_email, kwargs.get('passport_number'))
    elif notification_type == 'nft_minted':
        return email_service.send_nft_minted_email(
            to_email, kwargs.get('token_id'), 
            kwargs.get('passport_number'), kwargs.get('tx_hash')
        )
    elif notification_type == 'nft_sold':
        return email_service.send_nft_sold_email(
            to_email, kwargs.get('token_id'),
            kwargs.get('price'), kwargs.get('buyer_address')
        )
    elif notification_type == 'nft_purchased':
        return email_service.send_nft_purchased_email(
            to_email, kwargs.get('token_id'),
            kwargs.get('price'), kwargs.get('seller_address')
        )
    elif notification_type == 'security_alert':
        return email_service.send_security_alert_email(
            to_email, kwargs.get('alert_type'), kwargs.get('details')
        )
    elif notification_type == 'password_reset':
        return email_service.send_password_reset_email(to_email, kwargs.get('reset_token'))
    elif notification_type == 'transaction':
        return email_service.send_transaction_confirmation_email(
            to_email, kwargs.get('tx_type'),
            kwargs.get('tx_hash'), kwargs.get('status')
        )
    else:
        return False, f'Unknown notification type: {notification_type}'
