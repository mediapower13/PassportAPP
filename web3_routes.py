"""
Web3 Integration Routes for PassportApp
Flask API endpoints for blockchain operations
"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from web3_backend import web3_backend
import os

web3_bp = Blueprint('web3', __name__, url_prefix='/api/web3')


@web3_bp.route('/connect', methods=['POST'])
@login_required
def connect_network():
    """Connect to blockchain network"""
    try:
        data = request.get_json()
        rpc_url = data.get('rpc_url')
        
        success = web3_backend.connect(rpc_url)
        
        return jsonify({
            'success': True,
            'message': 'Connected to blockchain network',
            'connected': web3_backend.w3.is_connected()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/contract/load', methods=['POST'])
@login_required
def load_contract():
    """Load smart contract"""
    try:
        data = request.get_json()
        address = data.get('contract_address')
        abi_path = data.get('abi_path')
        
        web3_backend.load_contract(address, abi_path)
        
        return jsonify({
            'success': True,
            'message': 'Smart contract loaded',
            'contract_address': web3_backend.contract_address
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/passport/store', methods=['POST'])
@login_required
def store_passport():
    """Store passport on blockchain"""
    try:
        data = request.get_json()
        passport_number = data.get('passport_number')
        document_hash = data.get('document_hash')
        private_key = data.get('private_key')
        
        if not passport_number or not document_hash:
            return jsonify({
                'success': False,
                'error': 'Passport number and document hash required'
            }), 400
        
        result = web3_backend.store_passport(
            passport_number,
            document_hash,
            private_key
        )
        
        return jsonify({
            'success': True,
            'message': 'Passport stored on blockchain',
            'transaction': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/passport/<int:passport_id>', methods=['GET'])
@login_required
def get_passport(passport_id):
    """Get passport from blockchain"""
    try:
        passport = web3_backend.get_passport(passport_id)
        
        return jsonify({
            'success': True,
            'passport': passport
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/passport/owner/<address>', methods=['GET'])
@login_required
def get_owner_passports(address):
    """Get all passports for an owner"""
    try:
        passport_ids = web3_backend.get_owner_passports(address)
        
        passports = []
        for pid in passport_ids:
            passport = web3_backend.get_passport(pid)
            passport['id'] = pid
            passports.append(passport)
        
        return jsonify({
            'success': True,
            'passports': passports,
            'count': len(passports)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/passport/<int:passport_id>/update', methods=['PUT'])
@login_required
def update_passport(passport_id):
    """Update passport on blockchain"""
    try:
        data = request.get_json()
        new_document_hash = data.get('document_hash')
        private_key = data.get('private_key')
        
        if not new_document_hash:
            return jsonify({
                'success': False,
                'error': 'Document hash required'
            }), 400
        
        result = web3_backend.update_passport(
            passport_id,
            new_document_hash,
            private_key
        )
        
        return jsonify({
            'success': True,
            'message': 'Passport updated on blockchain',
            'transaction': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/passport/<int:passport_id>/verify/<address>', methods=['GET'])
@login_required
def verify_ownership(passport_id, address):
    """Verify passport ownership"""
    try:
        is_owner = web3_backend.verify_ownership(passport_id, address)
        
        return jsonify({
            'success': True,
            'is_owner': is_owner,
            'passport_id': passport_id,
            'address': address
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/wallet/balance/<address>', methods=['GET'])
@login_required
def get_balance(address):
    """Get wallet balance"""
    try:
        balance = web3_backend.get_balance(address)
        
        return jsonify({
            'success': True,
            'address': address,
            'balance': balance
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/message/sign', methods=['POST'])
@login_required
def sign_message():
    """Sign a message"""
    try:
        data = request.get_json()
        message = data.get('message')
        private_key = data.get('private_key')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message required'
            }), 400
        
        result = web3_backend.sign_message(message, private_key)
        
        return jsonify({
            'success': True,
            'signed_message': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@web3_bp.route('/status', methods=['GET'])
@login_required
def get_status():
    """Get Web3 connection status"""
    try:
        is_connected = web3_backend.w3.is_connected() if web3_backend.w3 else False
        has_contract = web3_backend.contract is not None
        
        status = {
            'connected': is_connected,
            'contract_loaded': has_contract
        }
        
        if is_connected:
            status['block_number'] = web3_backend.w3.eth.block_number
            status['chain_id'] = web3_backend.w3.eth.chain_id
        
        if has_contract:
            status['contract_address'] = web3_backend.contract_address
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def init_web3_routes(app):
    """Initialize Web3 routes"""
    app.register_blueprint(web3_bp)
    
    # Initialize Web3 backend on app startup
    try:
        from web3_backend import init_web3
        init_web3()
        app.logger.info('Web3 backend initialized')
    except Exception as e:
        app.logger.warning(f'Web3 backend initialization failed: {e}')
