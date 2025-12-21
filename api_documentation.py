"""
API Documentation Generator for PassportApp
Auto-generate API documentation from route decorators
"""

from functools import wraps
from flask import jsonify, request
import json


class APIDocumentation:
    """API Documentation manager"""
    
    def __init__(self):
        self.endpoints = {}
        self.categories = {}
    
    def document(self, category='general', description='', method='GET', 
                 params=None, responses=None, auth_required=False):
        """Decorator to document API endpoints"""
        def decorator(func):
            endpoint_name = func.__name__
            
            # Store endpoint documentation
            self.endpoints[endpoint_name] = {
                'name': endpoint_name,
                'category': category,
                'description': description,
                'method': method,
                'parameters': params or [],
                'responses': responses or {},
                'auth_required': auth_required,
                'function': func.__name__
            }
            
            # Add to category
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(endpoint_name)
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def get_all_endpoints(self):
        """Get all documented endpoints"""
        return self.endpoints
    
    def get_by_category(self, category):
        """Get endpoints by category"""
        if category not in self.categories:
            return []
        
        return [
            self.endpoints[endpoint]
            for endpoint in self.categories[category]
        ]
    
    def generate_openapi_spec(self, title='PassportApp API', version='1.0.0'):
        """Generate OpenAPI 3.0 specification"""
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': title,
                'version': version,
                'description': 'Blockchain-based passport management system'
            },
            'servers': [
                {'url': 'http://localhost:5000', 'description': 'Development server'},
                {'url': 'https://api.passportapp.com', 'description': 'Production server'}
            ],
            'paths': {},
            'components': {
                'securitySchemes': {
                    'bearerAuth': {
                        'type': 'http',
                        'scheme': 'bearer'
                    }
                }
            }
        }
        
        for endpoint_name, endpoint_data in self.endpoints.items():
            path = f'/api/{endpoint_data["category"]}/{endpoint_name}'
            method = endpoint_data['method'].lower()
            
            if path not in spec['paths']:
                spec['paths'][path] = {}
            
            operation = {
                'summary': endpoint_data['description'],
                'operationId': endpoint_name,
                'tags': [endpoint_data['category']],
                'responses': {}
            }
            
            # Add parameters
            if endpoint_data['parameters']:
                operation['parameters'] = endpoint_data['parameters']
            
            # Add responses
            for status_code, response_desc in endpoint_data['responses'].items():
                operation['responses'][str(status_code)] = {
                    'description': response_desc
                }
            
            # Add security if required
            if endpoint_data['auth_required']:
                operation['security'] = [{'bearerAuth': []}]
            
            spec['paths'][path][method] = operation
        
        return spec
    
    def generate_markdown_docs(self):
        """Generate Markdown documentation"""
        docs = "# PassportApp API Documentation\n\n"
        docs += "## Overview\n\n"
        docs += "This document describes the API endpoints for PassportApp.\n\n"
        
        for category, endpoints in self.categories.items():
            docs += f"## {category.title()}\n\n"
            
            for endpoint_name in endpoints:
                endpoint = self.endpoints[endpoint_name]
                
                docs += f"### {endpoint['name']}\n\n"
                docs += f"**Description:** {endpoint['description']}\n\n"
                docs += f"**Method:** `{endpoint['method']}`\n\n"
                
                if endpoint['auth_required']:
                    docs += "**Authentication:** Required 🔒\n\n"
                
                if endpoint['parameters']:
                    docs += "**Parameters:**\n\n"
                    for param in endpoint['parameters']:
                        param_name = param.get('name', 'unknown')
                        param_type = param.get('type', 'string')
                        param_desc = param.get('description', '')
                        required = '(required)' if param.get('required') else '(optional)'
                        docs += f"- `{param_name}` ({param_type}) {required}: {param_desc}\n"
                    docs += "\n"
                
                if endpoint['responses']:
                    docs += "**Responses:**\n\n"
                    for status, desc in endpoint['responses'].items():
                        docs += f"- `{status}`: {desc}\n"
                    docs += "\n"
                
                docs += "---\n\n"
        
        return docs


# Global API documentation instance
api_docs = APIDocumentation()


# API endpoint examples
EXAMPLE_ENDPOINTS = {
    'passport': {
        'create': {
            'method': 'POST',
            'description': 'Create a new passport',
            'parameters': [
                {'name': 'passport_number', 'type': 'string', 'required': True},
                {'name': 'first_name', 'type': 'string', 'required': True},
                {'name': 'last_name', 'type': 'string', 'required': True}
            ],
            'responses': {
                201: 'Passport created successfully',
                400: 'Invalid input',
                401: 'Unauthorized'
            }
        },
        'get': {
            'method': 'GET',
            'description': 'Get passport by ID',
            'parameters': [
                {'name': 'id', 'type': 'integer', 'required': True}
            ],
            'responses': {
                200: 'Passport data',
                404: 'Passport not found'
            }
        }
    },
    'nft': {
        'mint': {
            'method': 'POST',
            'description': 'Mint NFT for passport',
            'parameters': [
                {'name': 'passport_id', 'type': 'integer', 'required': True},
                {'name': 'metadata_uri', 'type': 'string', 'required': True}
            ],
            'responses': {
                201: 'NFT minted successfully',
                400: 'Invalid input',
                500: 'Blockchain error'
            }
        }
    },
    'marketplace': {
        'list': {
            'method': 'POST',
            'description': 'List NFT on marketplace',
            'parameters': [
                {'name': 'token_id', 'type': 'integer', 'required': True},
                {'name': 'price', 'type': 'number', 'required': True}
            ],
            'responses': {
                201: 'NFT listed successfully',
                400: 'Invalid price',
                404: 'NFT not found'
            }
        },
        'buy': {
            'method': 'POST',
            'description': 'Buy NFT from marketplace',
            'parameters': [
                {'name': 'listing_id', 'type': 'integer', 'required': True}
            ],
            'responses': {
                200: 'NFT purchased successfully',
                400: 'Insufficient funds',
                404: 'Listing not found'
            }
        }
    }
}


def generate_api_docs_route():
    """Generate route handler for API documentation"""
    @api_docs.document(
        category='documentation',
        description='Get API documentation in JSON format',
        method='GET',
        responses={200: 'API documentation'}
    )
    def api_documentation():
        return jsonify(api_docs.get_all_endpoints())
    
    return api_documentation


def generate_openapi_route():
    """Generate route handler for OpenAPI spec"""
    @api_docs.document(
        category='documentation',
        description='Get OpenAPI specification',
        method='GET',
        responses={200: 'OpenAPI 3.0 specification'}
    )
    def openapi_spec():
        return jsonify(api_docs.generate_openapi_spec())
    
    return openapi_spec


def save_documentation_to_file(filename='API_DOCS.md'):
    """Save API documentation to markdown file"""
    docs = api_docs.generate_markdown_docs()
    
    with open(filename, 'w') as f:
        f.write(docs)
    
    return True


def save_openapi_spec(filename='openapi.json'):
    """Save OpenAPI specification to JSON file"""
    spec = api_docs.generate_openapi_spec()
    
    with open(filename, 'w') as f:
        json.dump(spec, f, indent=2)
    
    return True
