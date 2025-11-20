"""
Authentication Routes
Login, logout, token refresh endpoints
"""
from flask import Blueprint, jsonify, request, g
from src.auth.service import get_auth_service
from src.database.service import get_db_service

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
auth_service = get_auth_service()
db_service = get_db_service()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user
    
    Expected JSON:
    {
        "username": "john_doe",
        "email": "john@example.com",
        "password": "secure_password",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if user already exists
        existing_user = db_service.get_user_by_username(data['username'])
        if existing_user:
            return jsonify({'error': 'Username already exists'}), 409
        
        existing_email = db_service.get_user_by_email(data['email'])
        if existing_email:
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create user
        password_hash = auth_service.hash_password(data['password'])
        user = db_service.create_user(
            username=data['username'],
            email=data['email'],
            password_hash=password_hash,
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user
        }), 201
    except Exception as e:
        return jsonify({
            'error': f'Registration failed: {str(e)}',
            'error_code': 'REGISTER_FAILED'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user
    
    Expected JSON:
    {
        "username": "john_doe",
        "password": "secure_password"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Get user
        user = db_service.get_user_by_username(username)
        
        if not user or not auth_service.verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'User account is inactive'}), 403
        
        # Generate tokens
        access_token = auth_service.create_access_token(user.id, user.username, user.role.value)
        refresh_token = auth_service.create_refresh_token(user.id, user.username)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value
            }
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Login failed: {str(e)}',
            'error_code': 'LOGIN_FAILED'
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token
    
    Expected JSON or Header:
    {
        "refresh_token": "..."
    }
    OR
    Header: Authorization: Bearer {refresh_token}
    """
    try:
        # Get refresh token
        refresh_token = None
        data = request.get_json() or {}
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    scheme, token = auth_header.split()
                    if scheme.lower() == 'bearer':
                        refresh_token = token
                except ValueError:
                    pass
        
        if not refresh_token:
            return jsonify({'error': 'No refresh token provided'}), 400
        
        # Verify refresh token
        payload = auth_service.verify_token(refresh_token)
        
        if not payload or payload.get('token_type') != 'refresh':
            return jsonify({'error': 'Invalid refresh token'}), 401
        
        # Get user
        user = db_service.get_user_by_id(payload['user_id'])
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        # Generate new access token
        access_token = auth_service.create_access_token(user.id, user.username, user.role.value)
        
        return jsonify({
            'success': True,
            'access_token': access_token,
            'token_type': 'Bearer'
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Token refresh failed: {str(e)}',
            'error_code': 'REFRESH_FAILED'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@auth_service.require_auth()
def logout():
    """Logout user
    
    Note: JWT tokens cannot be revoked server-side without a blacklist.
    Client should delete the token locally.
    """
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@auth_service.require_auth()
def get_current_user():
    """Get current user info"""
    try:
        user_id = g.user_id
        user = db_service.get_user_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's accounts
        accounts = db_service.get_user_accounts(user_id)
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'accounts': accounts
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve user: {str(e)}',
            'error_code': 'USER_FETCH_FAILED'
        }), 500
