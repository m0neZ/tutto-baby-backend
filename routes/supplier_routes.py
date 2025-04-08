from flask import Blueprint, request, jsonify
from models import db, Supplier

supplier_bp = Blueprint('supplier_bp', __name__)

@supplier_bp.route('/', methods=['GET'])
def get_all_suppliers():
    suppliers = Supplier.query.all()
    return jsonify({'success': True, 'suppliers': [s.to_dict() for s in suppliers]}), 200

@supplier_bp.route('/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    supplier = Supplier.query.get(supplier_id)
    if not supplier:
        return jsonify({'success': False, 'error': 'Supplier not found'}), 404
    return jsonify({'success': True, 'supplier': supplier.to_dict()}), 200

@supplier_bp.route('/', methods=['POST'])
def create_supplier():
    data = request.json
    supplier = Supplier(name=data.get('name'), contact_info=data.get('contact_info'))
    db.session.add(supplier)
    db.session.commit()
    return jsonify({'success': True, 'supplier': supplier.to_dict()}), 201