# src/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from src.models.user import User

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401

    # Use string identity to satisfy JWT subject claim requirements
    identity = str(user.id)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify({
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_identity = get_jwt_identity()
    # Issue new access token
    new_access_token = create_access_token(identity=current_identity)
    return jsonify({'success': True, 'access_token': new_access_token}), 200

@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Example protected endpoint
    current_identity = get_jwt_identity()
    return jsonify({'success': True, 'logged_in_as': current_identity}), 200
