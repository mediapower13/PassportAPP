"""
Search indexing utilities for PassportApp
Full-text search with Elasticsearch-like functionality
"""

import re
from datetime import datetime
import json


class SearchIndex:
    """In-memory search index"""
    
    def __init__(self):
        self.documents = {}
        self.inverted_index = {}
        self.doc_counter = 0
    
    def tokenize(self, text):
        """Tokenize text for indexing"""
        if not text:
            return []
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation and split
        tokens = re.findall(r'\b\w+\b', text)
        
        return tokens
    
    def add_document(self, doc_id, document, fields=None):
        """Add document to index"""
        if fields is None:
            fields = document.keys()
        
        self.documents[doc_id] = document
        
        # Index each field
        for field in fields:
            if field not in document:
                continue
            
            value = document[field]
            
            if isinstance(value, str):
                tokens = self.tokenize(value)
                
                for token in tokens:
                    if token not in self.inverted_index:
                        self.inverted_index[token] = {}
                    
                    if doc_id not in self.inverted_index[token]:
                        self.inverted_index[token][doc_id] = []
                    
                    self.inverted_index[token][doc_id].append(field)
        
        self.doc_counter += 1
    
    def remove_document(self, doc_id):
        """Remove document from index"""
        if doc_id not in self.documents:
            return False
        
        del self.documents[doc_id]
        
        # Remove from inverted index
        for token in list(self.inverted_index.keys()):
            if doc_id in self.inverted_index[token]:
                del self.inverted_index[token][doc_id]
                
                # Clean up empty tokens
                if not self.inverted_index[token]:
                    del self.inverted_index[token]
        
        return True
    
    def search(self, query, fields=None, limit=10):
        """Search for documents"""
        tokens = self.tokenize(query)
        
        if not tokens:
            return []
        
        # Find documents containing all tokens
        doc_scores = {}
        
        for token in tokens:
            if token in self.inverted_index:
                for doc_id, doc_fields in self.inverted_index[token].items():
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = 0
                    
                    # Score based on field occurrences
                    doc_scores[doc_id] += len(doc_fields)
        
        # Sort by score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top results
        results = []
        for doc_id, score in sorted_docs[:limit]:
            if doc_id in self.documents:
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'document': self.documents[doc_id]
                })
        
        return results
    
    def search_prefix(self, prefix, limit=10):
        """Search for tokens with prefix"""
        prefix = prefix.lower()
        
        matching_tokens = [
            token for token in self.inverted_index.keys()
            if token.startswith(prefix)
        ]
        
        doc_scores = {}
        
        for token in matching_tokens:
            for doc_id in self.inverted_index[token]:
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = 0
                
                doc_scores[doc_id] += 1
        
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        results = []
        for doc_id, score in sorted_docs[:limit]:
            if doc_id in self.documents:
                results.append({
                    'doc_id': doc_id,
                    'score': score,
                    'document': self.documents[doc_id]
                })
        
        return results
    
    def get_suggestions(self, query, limit=5):
        """Get autocomplete suggestions"""
        tokens = self.tokenize(query)
        
        if not tokens:
            return []
        
        # Get last token for prefix matching
        last_token = tokens[-1]
        
        suggestions = set()
        
        for token in self.inverted_index.keys():
            if token.startswith(last_token):
                suggestions.add(token)
        
        return sorted(list(suggestions))[:limit]
    
    def get_stats(self):
        """Get index statistics"""
        return {
            'total_documents': len(self.documents),
            'total_tokens': len(self.inverted_index),
            'avg_tokens_per_doc': len(self.inverted_index) / max(1, len(self.documents))
        }


class PassportSearchIndex:
    """Search index for passports"""
    
    def __init__(self):
        self.index = SearchIndex()
    
    def index_passport(self, passport):
        """Index a passport"""
        doc_id = f"passport_{passport['id']}"
        
        searchable_doc = {
            'id': passport['id'],
            'passport_number': passport.get('passport_number', ''),
            'first_name': passport.get('first_name', ''),
            'last_name': passport.get('last_name', ''),
            'full_name': f"{passport.get('first_name', '')} {passport.get('last_name', '')}",
            'nationality': passport.get('nationality', ''),
            'status': passport.get('status', '')
        }
        
        self.index.add_document(doc_id, searchable_doc)
    
    def search_passports(self, query, limit=10):
        """Search passports"""
        results = self.index.search(query, limit=limit)
        
        return [r['document'] for r in results]
    
    def remove_passport(self, passport_id):
        """Remove passport from index"""
        doc_id = f"passport_{passport_id}"
        return self.index.remove_document(doc_id)


class NFTSearchIndex:
    """Search index for NFTs"""
    
    def __init__(self):
        self.index = SearchIndex()
    
    def index_nft(self, nft):
        """Index an NFT"""
        doc_id = f"nft_{nft['token_id']}"
        
        searchable_doc = {
            'token_id': nft['token_id'],
            'owner': nft.get('owner', ''),
            'name': nft.get('name', ''),
            'description': nft.get('description', ''),
            'listed': nft.get('listed', False),
            'price': nft.get('price', 0)
        }
        
        self.index.add_document(doc_id, searchable_doc)
    
    def search_nfts(self, query, limit=10):
        """Search NFTs"""
        results = self.index.search(query, limit=limit)
        
        return [r['document'] for r in results]
    
    def search_by_owner(self, owner_address):
        """Search NFTs by owner"""
        matching = []
        
        for doc_id, doc in self.index.documents.items():
            if doc.get('owner', '').lower() == owner_address.lower():
                matching.append(doc)
        
        return matching
    
    def search_listed(self):
        """Get all listed NFTs"""
        matching = []
        
        for doc_id, doc in self.index.documents.items():
            if doc.get('listed'):
                matching.append(doc)
        
        return matching


class UserSearchIndex:
    """Search index for users"""
    
    def __init__(self):
        self.index = SearchIndex()
    
    def index_user(self, user):
        """Index a user"""
        doc_id = f"user_{user['id']}"
        
        searchable_doc = {
            'id': user['id'],
            'username': user.get('username', ''),
            'email': user.get('email', ''),
            'wallet_address': user.get('wallet_address', '')
        }
        
        self.index.add_document(doc_id, searchable_doc)
    
    def search_users(self, query, limit=10):
        """Search users"""
        results = self.index.search(query, limit=limit)
        
        return [r['document'] for r in results]
    
    def find_by_email(self, email):
        """Find user by email"""
        for doc_id, doc in self.index.documents.items():
            if doc.get('email', '').lower() == email.lower():
                return doc
        
        return None
    
    def find_by_wallet(self, wallet_address):
        """Find user by wallet address"""
        for doc_id, doc in self.index.documents.items():
            if doc.get('wallet_address', '').lower() == wallet_address.lower():
                return doc
        
        return None


class SearchManager:
    """Manage all search indexes"""
    
    def __init__(self):
        self.passport_index = PassportSearchIndex()
        self.nft_index = NFTSearchIndex()
        self.user_index = UserSearchIndex()
    
    def index_all_data(self, db):
        """Index all data from database"""
        # This would fetch and index all records
        print("Indexing all data...")
        
        # Example structure (would actually query DB)
        # passports = db.query("SELECT * FROM passports")
        # for passport in passports:
        #     self.passport_index.index_passport(passport)
        
        print("Indexing completed")
    
    def search_all(self, query, limit=10):
        """Search across all indexes"""
        results = {
            'passports': self.passport_index.search_passports(query, limit),
            'nfts': self.nft_index.search_nfts(query, limit),
            'users': self.user_index.search_users(query, limit)
        }
        
        return results
    
    def get_stats(self):
        """Get statistics for all indexes"""
        return {
            'passport_index': self.passport_index.index.get_stats(),
            'nft_index': self.nft_index.index.get_stats(),
            'user_index': self.user_index.index.get_stats()
        }


class SearchFilter:
    """Filter search results"""
    
    @staticmethod
    def filter_by_field(results, field, value):
        """Filter results by field value"""
        return [r for r in results if r.get(field) == value]
    
    @staticmethod
    def filter_by_range(results, field, min_value=None, max_value=None):
        """Filter results by field range"""
        filtered = results
        
        if min_value is not None:
            filtered = [r for r in filtered if r.get(field, 0) >= min_value]
        
        if max_value is not None:
            filtered = [r for r in filtered if r.get(field, 0) <= max_value]
        
        return filtered
    
    @staticmethod
    def filter_by_date_range(results, field, start_date=None, end_date=None):
        """Filter results by date range"""
        filtered = results
        
        if start_date:
            filtered = [
                r for r in filtered
                if datetime.fromisoformat(r.get(field, '')) >= start_date
            ]
        
        if end_date:
            filtered = [
                r for r in filtered
                if datetime.fromisoformat(r.get(field, '')) <= end_date
            ]
        
        return filtered


# Global search manager
search_manager = SearchManager()


def init_search_indexes(db):
    """Initialize search indexes"""
    search_manager.index_all_data(db)
    return search_manager


def search_passports(query, limit=10):
    """Search passports"""
    return search_manager.passport_index.search_passports(query, limit)


def search_nfts(query, limit=10):
    """Search NFTs"""
    return search_manager.nft_index.search_nfts(query, limit)


def search_users(query, limit=10):
    """Search users"""
    return search_manager.user_index.search_users(query, limit)


def search_all(query, limit=10):
    """Search everything"""
    return search_manager.search_all(query, limit)
