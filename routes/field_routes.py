from flask import Blueprint, request, jsonify
from models import db, FieldOption

field_bp = Blueprint('field_bp', __name__)

@field_bp.route('/<string:type>', methods=['GET'])
def get_options_by_type(type):
    active_only = request.args.get('active', 'true').lower() == 'true'
    query = FieldOption.query.filter_by(type=type)
    if active_only:
        query = query.filter_by(is_active=True)
    options = query.order_by(FieldOption.is_active.desc(), FieldOption.value.asc()).all()
    return jsonify([opt.to_dict() for opt in options]), 200

@field_bp.route('/<string:type>', methods=['POST'])
def add_option(type):
    data = request.json
    value = data.get('value')
    if not value:
        return jsonify({'error': 'Value is required'}), 400

    exists = FieldOption.query.filter_by(type=type, value=value).first()
    if exists:
        return jsonify({'error': 'Option already exists'}), 400

    option = FieldOption(type=type, value=value)
    db.session.add(option)
    db.session.commit()
    return jsonify(option.to_dict()), 201

@field_bp.route('/<int:id>/deactivate', methods=['PATCH'])
def deactivate_option(id):
    option = FieldOption.query.get_or_404(id)
    option.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'Option deactivated'}), 200

@field_bp.route('/<int:id>/activate', methods=['PATCH'])
def activate_option(id):
    option = FieldOption.query.get_or_404(id)
    option.is_active = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Option reactivated'}), 200
