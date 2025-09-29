// payment-gateway/auth_middleware.py
"""
Authentication middleware for API key validation
"""

from flask import request, jsonify
from functools import wraps
import hashlib
import logging

logger = logging.getLogger(__name__)

# In production, these would be in environment variables or a database
VALID_API_KEYS = {
    'test_key_12345': {'client': 'test_client', 'tier': 'free'},
    'prod_key_67890': {'client': 'production_client', 'tier': 'premium'},
}


def hash_api_key(api_key: str) -> str:
    """Hash API key for secure comparison"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            logger.warning("Request without API key")
            return jsonify({
                'error': 'Missing API key',
                'message': 'Include X-API-Key header'
            }), 401
        
        if api_key not in VALID_API_KEYS:
            logger.warning(f"Invalid API key attempt: {api_key[:8]}...")
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403
        
        # Attach client info to request for logging
        request.client_info = VALID_API_KEYS[api_key]
        logger.info(f"Authenticated request from {request.client_info['client']}")
        
        return f(*args, **kwargs)
    
    return decorated_function
