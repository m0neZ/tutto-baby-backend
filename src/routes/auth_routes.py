# src/routes/auth_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from src.models import db
from src.models.user import User

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify(msg='E-mail ou senha inválidos'), 401

    identity = {'id': user.id, 'role': user.role}
    access = create_access_token(identity=identity)
    refresh = create_refresh_token(identity=identity)
    return jsonify(access_token=access, refresh_token=refresh), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity)
    new_refresh = create_refresh_token(identity=identity)
    return jsonify(access_token=new_access, refresh_token=new_refresh), 200
