"""
Internationalization (i18n) support for PassportApp
Multi-language support with translation utilities
"""

import json
import os
from functools import wraps
from flask import request, session


class TranslationManager:
    """Manage translations for multiple languages"""
    
    def __init__(self, translations_dir='translations'):
        self.translations_dir = translations_dir
        self.translations = {}
        self.default_language = 'en'
        self.supported_languages = ['en', 'es', 'fr', 'de', 'zh', 'ja', 'ar']
        self.ensure_translations_dir()
        self.load_all_translations()
    
    def ensure_translations_dir(self):
        """Ensure translations directory exists"""
        if not os.path.exists(self.translations_dir):
            os.makedirs(self.translations_dir)
    
    def load_all_translations(self):
        """Load all translation files"""
        for lang in self.supported_languages:
            self.load_language(lang)
    
    def load_language(self, language):
        """Load translations for a specific language"""
        filepath = os.path.join(self.translations_dir, f'{language}.json')
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.translations[language] = json.load(f)
        else:
            # Create default translation file
            self.translations[language] = self.get_default_translations()
            self.save_language(language)
    
    def save_language(self, language):
        """Save translations for a language"""
        filepath = os.path.join(self.translations_dir, f'{language}.json')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.translations.get(language, {}), f, indent=2, ensure_ascii=False)
    
    def get_default_translations(self):
        """Get default English translations"""
        return {
            # Common
            'welcome': 'Welcome',
            'login': 'Login',
            'logout': 'Logout',
            'register': 'Register',
            'submit': 'Submit',
            'cancel': 'Cancel',
            'save': 'Save',
            'delete': 'Delete',
            'edit': 'Edit',
            'search': 'Search',
            'close': 'Close',
            
            # Navigation
            'home': 'Home',
            'dashboard': 'Dashboard',
            'profile': 'Profile',
            'settings': 'Settings',
            
            # Passport
            'passport': 'Passport',
            'passports': 'Passports',
            'create_passport': 'Create Passport',
            'passport_number': 'Passport Number',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'nationality': 'Nationality',
            'issue_date': 'Issue Date',
            'expiry_date': 'Expiry Date',
            
            # NFT
            'nft': 'NFT',
            'mint_nft': 'Mint NFT',
            'token_id': 'Token ID',
            'owner': 'Owner',
            'metadata': 'Metadata',
            
            # Marketplace
            'marketplace': 'Marketplace',
            'list_for_sale': 'List for Sale',
            'buy': 'Buy',
            'price': 'Price',
            'seller': 'Seller',
            'buyer': 'Buyer',
            
            # Blockchain
            'wallet': 'Wallet',
            'connect_wallet': 'Connect Wallet',
            'transaction': 'Transaction',
            'transaction_hash': 'Transaction Hash',
            'block_number': 'Block Number',
            'gas_fee': 'Gas Fee',
            'confirmed': 'Confirmed',
            'pending': 'Pending',
            
            # Messages
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Information',
            'loading': 'Loading...',
            'please_wait': 'Please wait...',
            
            # Errors
            'error_required_field': 'This field is required',
            'error_invalid_email': 'Invalid email address',
            'error_invalid_password': 'Invalid password',
            'error_network': 'Network error occurred',
            'error_not_found': 'Not found',
            
            # Success messages
            'success_login': 'Login successful',
            'success_register': 'Registration successful',
            'success_passport_created': 'Passport created successfully',
            'success_nft_minted': 'NFT minted successfully',
            'success_transaction': 'Transaction completed successfully'
        }
    
    def translate(self, key, language=None, **kwargs):
        """Translate a key to target language"""
        if language is None:
            language = self.default_language
        
        if language not in self.translations:
            language = self.default_language
        
        translation = self.translations[language].get(key, key)
        
        # Replace placeholders
        if kwargs:
            try:
                translation = translation.format(**kwargs)
            except:
                pass
        
        return translation
    
    def add_translation(self, key, translations_dict):
        """Add new translation key"""
        for language, translation in translations_dict.items():
            if language in self.translations:
                self.translations[language][key] = translation
                self.save_language(language)


# Global translation manager
translator = TranslationManager()


def get_language():
    """Get current language from session or request"""
    # Try session first
    language = session.get('language')
    
    if not language:
        # Try accept-language header
        language = request.accept_languages.best_match(translator.supported_languages)
    
    if not language:
        language = translator.default_language
    
    return language


def set_language(language):
    """Set language in session"""
    if language in translator.supported_languages:
        session['language'] = language
        return True
    return False


def t(key, **kwargs):
    """Translate shorthand function"""
    language = get_language()
    return translator.translate(key, language, **kwargs)


def translate_dict(data_dict, language=None):
    """Translate all values in a dictionary"""
    if language is None:
        language = get_language()
    
    translated = {}
    for key, value in data_dict.items():
        if isinstance(value, str):
            translated[key] = translator.translate(value, language)
        else:
            translated[key] = value
    
    return translated


# Template filter for Jinja2
def translate_filter(key, **kwargs):
    """Translation filter for Jinja2 templates"""
    return t(key, **kwargs)


# Create translation files for supported languages
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'zh': '中文',
    'ja': '日本語',
    'ar': 'العربية'
}


def get_supported_languages():
    """Get list of supported languages"""
    return [
        {'code': code, 'name': name}
        for code, name in LANGUAGE_NAMES.items()
    ]


def create_language_switcher_data():
    """Create data for language switcher component"""
    current_language = get_language()
    
    return {
        'current': current_language,
        'current_name': LANGUAGE_NAMES.get(current_language, 'English'),
        'languages': get_supported_languages()
    }


# Spanish translations
SPANISH_TRANSLATIONS = {
    'welcome': 'Bienvenido',
    'login': 'Iniciar sesión',
    'logout': 'Cerrar sesión',
    'register': 'Registrarse',
    'submit': 'Enviar',
    'cancel': 'Cancelar',
    'save': 'Guardar',
    'delete': 'Eliminar',
    'dashboard': 'Panel de control',
    'passport': 'Pasaporte',
    'marketplace': 'Mercado',
    'wallet': 'Billetera',
    'connect_wallet': 'Conectar billetera',
    'success': 'Éxito',
    'error': 'Error'
}


# French translations
FRENCH_TRANSLATIONS = {
    'welcome': 'Bienvenue',
    'login': 'Se connecter',
    'logout': 'Se déconnecter',
    'register': "S'inscrire",
    'submit': 'Soumettre',
    'cancel': 'Annuler',
    'save': 'Enregistrer',
    'delete': 'Supprimer',
    'dashboard': 'Tableau de bord',
    'passport': 'Passeport',
    'marketplace': 'Marché',
    'wallet': 'Portefeuille',
    'connect_wallet': 'Connecter le portefeuille',
    'success': 'Succès',
    'error': 'Erreur'
}


def init_translations():
    """Initialize translation system"""
    translator.load_all_translations()
    return True
