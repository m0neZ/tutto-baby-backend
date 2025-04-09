from flask import Blueprint, request, jsonify
from models import db, FieldOption

field_bp = Blueprint('field_bp', __name__)

@field_bp.route('/<field_type>', methods=['GET'])
def get_field_options(field_type):
    active = request.args.get('active')
    query = FieldOption.query.filter_by(type=field_type)
    
    if active != 'false':
        query = query.filter_by(is_active=True)

    options = query.order_by(FieldOption.is_active.desc(), FieldOption.value.asc()).all()
    return jsonify([opt.to_dict() for opt in options])

@field_bp.route('/<field_type>', methods=['POST'])
def add_field_option(field_type):
    data = request.get_json()
    value = data.get('value', '').strip()

    if not value:
        return jsonify({'error': 'Value is required'}), 400

    existing = FieldOption.query.filter_by(type=field_type, value=value).first()
    if existing:
        return jsonify({'error': 'Option already exists'}), 400

    option = FieldOption(type=field_type, value=value)
    db.session.add(option)
    db.session.commit()
    return jsonify(option.to_dict()), 201

@field_bp.route('/<int:option_id>/deactivate', methods=['PATCH'])
def deactivate_option(option_id):
    option = FieldOption.query.get(option_id)
    if not option:
        return jsonify({'error': 'Option not found'}), 404

    option.is_active = False
    db.session.commit()
    return jsonify({'message': 'Option deactivated'}), 200

@field_bp.route('/<int:option_id>/activate', methods=['PATCH'])
def activate_option(option_id):
    option = FieldOption.query.get(option_id)
    if not option:
        return jsonify({'error': 'Option not found'}), 404

    option.is_active = True
    db.session.commit()
    return jsonify({'message': 'Option activated'}), 200
