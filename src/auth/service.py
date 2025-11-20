"""
Authentication Service
JWT token generation and validation
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash


class AuthService:
    """Authentication service"""

    def __init__(self, secret_key: str = None):
        """Initialize auth service"""
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'your-secret-key-change-in-prod')
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def hash_password(self, password: str) -> str:
        """Hash password"""
        return generate_password_hash(password, method='pbkdf2:sha256')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password"""
        return check_password_hash(password_hash, password)

    def create_access_token(self, user_id: str, username: str, role: str = "customer") -> str:
        """Create JWT access token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            'token_type': 'access'
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str, username: str) -> str:
        """Create JWT refresh token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            'token_type': 'refresh'
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_token_from_request(self) -> Optional[str]:
        """Extract token from request header"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() == 'bearer':
                return token
        except ValueError:
            pass
        
        return None

    def require_auth(self, roles: list = None):
        """Decorator to require authentication"""
        def decorator(fn):
            @wraps(fn)
            def decorated_function(*args, **kwargs):
                token = self.get_token_from_request()
                
                if not token:
                    return jsonify({
                        'error': 'Missing authorization token',
                        'error_code': 'AUTH_MISSING'
                    }), 401
                
                payload = self.verify_token(token)
                
                if not payload:
                    return jsonify({
                        'error': 'Invalid or expired token',
                        'error_code': 'AUTH_INVALID'
                    }), 401
                
                if roles and payload.get('role') not in roles:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'error_code': 'AUTH_FORBIDDEN'
                    }), 403
                
                # Store user info in g for access in the route
                g.user_id = payload.get('user_id')
                g.username = payload.get('username')
                g.role = payload.get('role')
                
                return fn(*args, **kwargs)
            
            return decorated_function
        return decorator


# Global auth service instance
_auth_service = None


def get_auth_service() -> AuthService:
    """Get or create auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
