"""
API versioning utilities for PassportApp
Support multiple API versions with backward compatibility
"""

from functools import wraps
from flask import request, jsonify
import re


class APIVersion:
    """API version management"""
    
    def __init__(self, major, minor, patch=0):
        self.major = major
        self.minor = minor
        self.patch = patch
    
    def __str__(self):
        return f'v{self.major}.{self.minor}.{self.patch}'
    
    def __repr__(self):
        return f'APIVersion({self.major}, {self.minor}, {self.patch})'
    
    def __eq__(self, other):
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch)
    
    def __lt__(self, other):
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch
    
    def __le__(self, other):
        return self == other or self < other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other
    
    @staticmethod
    def parse(version_string):
        """Parse version string like 'v1.0.0' or '1.0'"""
        match = re.match(r'v?(\d+)\.(\d+)(?:\.(\d+))?', version_string)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3)) if match.group(3) else 0
            return APIVersion(major, minor, patch)
        return None


class APIVersionManager:
    """Manage API versions and routes"""
    
    def __init__(self):
        self.versions = {}
        self.current_version = APIVersion(1, 0, 0)
        self.deprecated_versions = []
        self.supported_versions = [
            APIVersion(1, 0, 0),
            APIVersion(1, 1, 0),
            APIVersion(2, 0, 0)
        ]
    
    def register_version(self, version, routes):
        """Register routes for a specific API version"""
        if isinstance(version, str):
            version = APIVersion.parse(version)
        
        self.versions[str(version)] = routes
    
    def deprecate_version(self, version):
        """Mark version as deprecated"""
        if isinstance(version, str):
            version = APIVersion.parse(version)
        
        if version not in self.deprecated_versions:
            self.deprecated_versions.append(version)
    
    def is_supported(self, version):
        """Check if version is supported"""
        if isinstance(version, str):
            version = APIVersion.parse(version)
        
        return version in self.supported_versions
    
    def is_deprecated(self, version):
        """Check if version is deprecated"""
        if isinstance(version, str):
            version = APIVersion.parse(version)
        
        return version in self.deprecated_versions
    
    def get_version_from_request(self):
        """Extract API version from request"""
        # Check URL path
        path_match = re.match(r'/api/(v\d+\.\d+(?:\.\d+)?)', request.path)
        if path_match:
            return APIVersion.parse(path_match.group(1))
        
        # Check header
        version_header = request.headers.get('API-Version')
        if version_header:
            return APIVersion.parse(version_header)
        
        # Check query parameter
        version_param = request.args.get('version')
        if version_param:
            return APIVersion.parse(version_param)
        
        # Default to current version
        return self.current_version
    
    def get_latest_version(self):
        """Get latest API version"""
        return max(self.supported_versions)


# Global version manager
version_manager = APIVersionManager()


def api_version(min_version=None, max_version=None):
    """Decorator to specify supported API versions for endpoint"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            requested_version = version_manager.get_version_from_request()
            
            # Check if version is supported
            if not version_manager.is_supported(requested_version):
                return jsonify({
                    'error': 'Unsupported API version',
                    'requested': str(requested_version),
                    'supported': [str(v) for v in version_manager.supported_versions]
                }), 400
            
            # Check version range
            if min_version:
                min_ver = APIVersion.parse(min_version) if isinstance(min_version, str) else min_version
                if requested_version < min_ver:
                    return jsonify({
                        'error': f'API version too old. Minimum: {min_ver}'
                    }), 400
            
            if max_version:
                max_ver = APIVersion.parse(max_version) if isinstance(max_version, str) else max_version
                if requested_version > max_ver:
                    return jsonify({
                        'error': f'API version too new. Maximum: {max_ver}'
                    }), 400
            
            # Check if deprecated
            if version_manager.is_deprecated(requested_version):
                # Add deprecation warning header
                response = func(*args, **kwargs)
                if hasattr(response, 'headers'):
                    response.headers['X-API-Deprecated'] = 'true'
                    response.headers['X-API-Sunset'] = '2026-12-31'
                return response
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def deprecated_endpoint(sunset_date=None):
    """Mark endpoint as deprecated"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers['X-Endpoint-Deprecated'] = 'true'
                if sunset_date:
                    response.headers['X-Endpoint-Sunset'] = sunset_date
            
            return response
        return wrapper
    return decorator


class ResponseTransformer:
    """Transform responses based on API version"""
    
    @staticmethod
    def transform_v1_to_v2(data):
        """Transform v1 response to v2 format"""
        # Example transformation
        if isinstance(data, dict):
            transformed = data.copy()
            
            # Rename fields
            if 'passport_number' in transformed:
                transformed['documentNumber'] = transformed.pop('passport_number')
            
            if 'first_name' in transformed:
                transformed['firstName'] = transformed.pop('first_name')
            
            if 'last_name' in transformed:
                transformed['lastName'] = transformed.pop('last_name')
            
            return transformed
        
        return data
    
    @staticmethod
    def transform_v2_to_v1(data):
        """Transform v2 response to v1 format"""
        if isinstance(data, dict):
            transformed = data.copy()
            
            # Rename fields back
            if 'documentNumber' in transformed:
                transformed['passport_number'] = transformed.pop('documentNumber')
            
            if 'firstName' in transformed:
                transformed['first_name'] = transformed.pop('firstName')
            
            if 'lastName' in transformed:
                transformed['last_name'] = transformed.pop('lastName')
            
            return transformed
        
        return data


def version_aware_response(data, source_version='2.0.0'):
    """Transform response based on requested API version"""
    requested_version = version_manager.get_version_from_request()
    source_ver = APIVersion.parse(source_version)
    
    # If requesting v1 and source is v2, transform
    if requested_version.major == 1 and source_ver.major == 2:
        data = ResponseTransformer.transform_v2_to_v1(data)
    
    # If requesting v2 and source is v1, transform
    elif requested_version.major == 2 and source_ver.major == 1:
        data = ResponseTransformer.transform_v1_to_v2(data)
    
    return data


def get_api_info():
    """Get API version information"""
    return {
        'current_version': str(version_manager.current_version),
        'latest_version': str(version_manager.get_latest_version()),
        'supported_versions': [str(v) for v in version_manager.supported_versions],
        'deprecated_versions': [str(v) for v in version_manager.deprecated_versions],
        'endpoints': {
            'v1': {
                'base_url': '/api/v1',
                'documentation': '/api/v1/docs'
            },
            'v2': {
                'base_url': '/api/v2',
                'documentation': '/api/v2/docs'
            }
        }
    }


# API changelog
API_CHANGELOG = {
    'v2.0.0': {
        'date': '2025-12-01',
        'changes': [
            'Changed field names to camelCase',
            'Added new NFT marketplace endpoints',
            'Enhanced error responses',
            'Added WebSocket support'
        ],
        'breaking_changes': [
            'Field name changes (snake_case to camelCase)',
            'Updated response structure'
        ]
    },
    'v1.1.0': {
        'date': '2025-06-01',
        'changes': [
            'Added IPFS support',
            'Added analytics endpoints',
            'Performance improvements'
        ],
        'breaking_changes': []
    },
    'v1.0.0': {
        'date': '2025-01-01',
        'changes': [
            'Initial release',
            'Basic passport management',
            'NFT minting',
            'Blockchain integration'
        ],
        'breaking_changes': []
    }
}


def get_changelog(version=None):
    """Get API changelog"""
    if version:
        version_str = str(version) if isinstance(version, APIVersion) else version
        return API_CHANGELOG.get(version_str)
    
    return API_CHANGELOG
