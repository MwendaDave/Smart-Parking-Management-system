"""Authentication routes"""
from flask import Blueprint, request, jsonify
import bcrypt
from flask_jwt_extended import create_access_token, get_jwt_identity
from utils.db import db
from utils.logger import system_logger
from middleware.auth_middleware import require_auth

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    query = "SELECT * FROM users WHERE email = %s"
    users = db.execute_query(query, (email,))
    
    if not users or not verify_password(password, users[0]['password_hash']):
        system_logger.warning('AUTH', f"Failed login attempt for {email}")
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user = users[0]
    token = create_access_token(identity={
        'user_id': user['user_id'],
        'email': user['email'],
        'role': user['role']
    })
    
    system_logger.info('AUTH', f"User {email} logged in", user['user_id'])
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'full_name': user['full_name'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    try:
        password_hash = hash_password(data.get('password'))
        query = """
            INSERT INTO users (full_name, email, phone, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
        """
        user_id = db.execute_query(query, (
            data.get('full_name'),
            data.get('email'),
            data.get('phone'),
            password_hash,
            data.get('role', 'driver')
        ), fetch=False)
        
        system_logger.info('AUTH', f"New user registered: {data.get('email')}", user_id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user_id': user_id
        }), 201
        
    except Exception as e:
        system_logger.error('AUTH', f"Registration failed: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 400

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def profile():
    current_user = get_jwt_identity()
    return jsonify({'success': True, 'data': current_user}), 200