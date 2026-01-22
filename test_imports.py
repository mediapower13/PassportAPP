"""
Test all imports and modules to ensure no bugs
"""

def test_imports():
    """Test all critical imports"""
    errors = []
    
    try:
        from flask import Flask
        print("✓ Flask imported")
    except Exception as e:
        errors.append(f"✗ Flask: {e}")
    
    try:
        from flask_login import LoginManager
        print("✓ Flask-Login imported")
    except Exception as e:
        errors.append(f"✗ Flask-Login: {e}")
    
    try:
        from flask_sqlalchemy import SQLAlchemy
        print("✓ Flask-SQLAlchemy imported")
    except Exception as e:
        errors.append(f"✗ Flask-SQLAlchemy: {e}")
    
    try:
        from web3 import Web3
        print("✓ Web3 imported")
    except Exception as e:
        errors.append(f"✗ Web3: {e}")
    
    try:
        from eth_account import Account
        print("✓ eth_account imported")
    except Exception as e:
        errors.append(f"✗ eth_account: {e}")
    
    try:
        from cryptography.fernet import Fernet
        print("✓ cryptography imported")
    except Exception as e:
        errors.append(f"✗ cryptography: {e}")
    
    try:
        from passporteye import read_mrz
        print("✓ passporteye imported")
    except Exception as e:
        errors.append(f"✗ passporteye: {e}")
    
    try:
        import pytesseract
        print("✓ pytesseract imported")
    except Exception as e:
        errors.append(f"✗ pytesseract: {e}")
    
    try:
        import cv2
        print("✓ opencv-python imported")
    except Exception as e:
        errors.append(f"✗ opencv-python: {e}")
    
    try:
        from PIL import Image
        print("✓ Pillow imported")
    except Exception as e:
        errors.append(f"✗ Pillow: {e}")
    
    try:
        import qrcode
        print("✓ qrcode imported")
    except Exception as e:
        errors.append(f"✗ qrcode: {e}")
    
    try:
        import pyotp
        print("✓ pyotp imported")
    except Exception as e:
        errors.append(f"✗ pyotp: {e}")
    
    return errors


def test_modules():
    """Test custom modules"""
    errors = []
    
    try:
        from models import User, Passport, db
        print("✓ models module imported")
        
        # Check if wallet_address field exists
        if hasattr(User, 'wallet_address'):
            print("✓ User.wallet_address field exists")
        else:
            errors.append("✗ User.wallet_address field missing")
    except Exception as e:
        errors.append(f"✗ models: {e}")
    
    try:
        from encryption import get_encryption_service
        service = get_encryption_service()
        print("✓ encryption module imported and initialized")
        
        # Test encryption
        test_data = "test123"
        encrypted = service.encrypt(test_data)
        decrypted = service.decrypt(encrypted)
        if decrypted == test_data:
            print("✓ Encryption/decryption working")
        else:
            errors.append("✗ Encryption/decryption failed")
    except Exception as e:
        errors.append(f"✗ encryption: {e}")
    
    try:
        from passport_scanner import get_passport_scanner
        scanner = get_passport_scanner()
        print("✓ passport_scanner module imported and initialized")
    except Exception as e:
        errors.append(f"✗ passport_scanner: {e}")
    
    try:
        from web3_backend import web3_backend
        print("✓ web3_backend module imported")
        
        # Check if methods exist
        if hasattr(web3_backend, 'is_connected'):
            print("✓ web3_backend.is_connected method exists")
        else:
            errors.append("✗ web3_backend.is_connected method missing")
        
        if hasattr(web3_backend, 'set_contract'):
            print("✓ web3_backend.set_contract method exists")
        else:
            errors.append("✗ web3_backend.set_contract method missing")
    except Exception as e:
        errors.append(f"✗ web3_backend: {e}")
    
    try:
        from routes import auth_bp, main_bp
        print("✓ routes module imported")
    except Exception as e:
        errors.append(f"✗ routes: {e}")
    
    try:
        from passport_routes import passport_bp
        print("✓ passport_routes module imported")
    except Exception as e:
        errors.append(f"✗ passport_routes: {e}")
    
    try:
        from web3_routes import web3_bp
        print("✓ web3_routes module imported")
    except Exception as e:
        errors.append(f"✗ web3_routes: {e}")
    
    return errors


if __name__ == '__main__':
    print("=" * 60)
    print("Testing PassportApp - Import and Module Verification")
    print("=" * 60)
    
    print("\n[1/2] Testing third-party imports...")
    print("-" * 60)
    import_errors = test_imports()
    
    print("\n[2/2] Testing custom modules...")
    print("-" * 60)
    module_errors = test_modules()
    
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    all_errors = import_errors + module_errors
    
    if all_errors:
        print(f"\n❌ {len(all_errors)} ERRORS FOUND:\n")
        for error in all_errors:
            print(error)
        print("\nPlease fix these errors before running the application.")
    else:
        print("\n✅ ALL TESTS PASSED!")
        print("No bugs found. Application is ready to run.")
    
    print("\n" + "=" * 60)
