"""
Web3 Routes for PassportApp
Blockchain integration endpoints
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from web3_backend import web3_backend
import os

web3_bp = Blueprint('web3', __name__, url_prefix='/api/web3')


@web3_bp.route('/connect', methods=['POST'])
@login_required
def connect_wallet():
    """Connect Web3 wallet"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        
        if not wallet_address:
            return jsonify({'error': 'Wallet address required'}), 400
        
        # Validate wallet address format
        if not wallet_address.startswith('0x') or len(wallet_address) != 42:
            return jsonify({'error': 'Invalid wallet address format'}), 400
        
        # Verify checksum if Web3 is connected
        if web3_backend.is_connected():
            try:
                wallet_address = web3_backend.w3.to_checksum_address(wallet_address)
            except ValueError:
                return jsonify({'error': 'Invalid wallet address checksum'}), 400
        
        session['wallet_address'] = wallet_address
        
        current_user.wallet_address = wallet_address
        from models import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Wallet connected successfully',
            'wallet_address': wallet_address
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect_wallet():
    """Disconnect Web3 wallet"""
    try:
        if 'wallet_address' in session:
            del session['wallet_address']
        
        return jsonify({
            'success': True,
            'message': 'Wallet disconnected successfully'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/status', methods=['GET'])
@login_required
def get_web3_status():
    """Get Web3 connection status"""
    try:
        is_connected = web3_backend.is_connected()
        wallet_address = session.get('wallet_address')
        
        status = {
            'connected': is_connected,
            'wallet_address': wallet_address,
            'network': 'Localhost' if is_connected else None
        }
        
        if is_connected:
            try:
                status['block_number'] = web3_backend.w3.eth.block_number
                status['chain_id'] = web3_backend.w3.eth.chain_id
            except Exception as e:
                status['error'] = f'Failed to get blockchain info: {str(e)}'
        
        return jsonify(status)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/passport/store', methods=['POST'])
@login_required
def store_passport_on_blockchain():
    """Store passport data on blockchain"""
    try:
        # Check if Web3 is connected
        if not web3_backend.is_connected():
            return jsonify({'error': 'Web3 not connected. Please connect to blockchain first.'}), 503
        
        data = request.get_json()
        passport_id = data.get('passport_id')
        
        if not passport_id:
            return jsonify({'error': 'Passport ID required'}), 400
        
        # Get passport from database
        from models import Passport
        passport = Passport.query.get(passport_id)
        
        if not passport or passport.user_id != current_user.id:
            return jsonify({'error': 'Passport not found'}), 404
        
        # Store on blockchain
        wallet_address = session.get('wallet_address')
        if not wallet_address:
            return jsonify({'error': 'Wallet not connected'}), 400
        
        # Get decrypted passport number
        from encryption import get_encryption_service
        encryption = get_encryption_service()
        passport_number = encryption.decrypt(passport.passport_number)
        full_name = encryption.decrypt(passport.full_name)
        
        # Create document hash
        import hashlib
        document_data = f"{passport_number}_{full_name}_{passport.nationality}"
        document_hash = hashlib.sha256(document_data.encode()).hexdigest()
        
        # Store on blockchain using correct parameters
        result = web3_backend.store_passport(
            passport_number,
            document_hash
        )
        
        if not result or 'transaction_hash' not in result:
            return jsonify({'error': 'Failed to store passport on blockchain'}), 500
        
        return jsonify({
            'success': True,
            'message': 'Passport stored on blockchain',
            'transaction_hash': result['transaction_hash'],
            'block_number': result.get('block_number', 'N/A')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/passport/get/<passport_number>', methods=['GET'])
@login_required
def get_passport_from_blockchain(passport_number):
    """Get passport data from blockchain"""
    try:
        passport_data = web3_backend.get_passport(passport_number)
        
        return jsonify({
            'success': True,
            'passport': passport_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/balance', methods=['GET'])
@login_required
def get_wallet_balance():
    """Get wallet balance"""
    try:
        wallet_address = session.get('wallet_address')
        
        if not wallet_address:
            return jsonify({'error': 'Wallet not connected'}), 400
        
        balance = web3_backend.get_balance(wallet_address)
        
        return jsonify({
            'success': True,
            'balance': balance,
            'wallet_address': wallet_address
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/transaction/<tx_hash>', methods=['GET'])
@login_required
def get_transaction(tx_hash):
    """Get transaction details"""
    try:
        if not web3_backend.is_connected():
            return jsonify({'error': 'Web3 not connected'}), 500
        
        # Validate transaction hash format
        if not tx_hash.startswith('0x') or len(tx_hash) != 66:
            return jsonify({'error': 'Invalid transaction hash format'}), 400
        
        tx = web3_backend.w3.eth.get_transaction(tx_hash)
        
        if tx is None:
            return jsonify({'error': 'Transaction not found'}), 404
        
        receipt = web3_backend.w3.eth.get_transaction_receipt(tx_hash)
        
        return jsonify({
            'success': True,
            'transaction': {
                'hash': tx_hash,
                'from': tx['from'],
                'to': tx['to'],
                'value': str(tx['value']),
                'gas': tx['gas'],
                'gasPrice': str(tx['gasPrice']),
                'blockNumber': receipt['blockNumber'] if receipt else None,
                'status': receipt['status'] if receipt else None
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@web3_bp.route('/gas-price', methods=['GET'])
def get_gas_price():
    """Get current gas price"""
    try:
        if not web3_backend.is_connected():
            return jsonify({'error': 'Web3 not connected'}), 500
        
        gas_price = web3_backend.w3.eth.gas_price
        gas_price_gwei = web3_backend.w3.from_wei(gas_price, 'gwei')
        
        return jsonify({
            'success': True,
            'gas_price_wei': str(gas_price),
            'gas_price_gwei': str(gas_price_gwei)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Initialize Web3 when blueprint is registered
def init_web3():
    """Initialize Web3 connection"""
    try:
        rpc_url = os.getenv('WEB3_RPC_URL', 'http://127.0.0.1:8545')
        contract_address = os.getenv('CONTRACT_ADDRESS')
        
        web3_backend.connect(rpc_url)
        
        if contract_address:
            web3_backend.set_contract(contract_address)
        
        print("✓ Web3 backend initialized")
        
    except Exception as e:
        print(f"✗ Web3 initialization failed: {e}")
