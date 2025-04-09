from flask import Blueprint, request, jsonify
from models import db, Product, Supplier
from utils.helpers import generate_sku
from datetime import datetime

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    return jsonify({'success': True, 'products': [p.to_dict() for p in products]}), 200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404
    return jsonify({'success': True, 'product': product.to_dict()}), 200

@product_bp.route('/', methods=['POST'])
def create_product():
    data = request.json
    supplier = Supplier.query.get(data.get('supplier_id'))
    if not supplier:
        return jsonify({'success': False, 'error': 'Supplier not found'}), 404

    purchase_date = data.get('purchase_date')
    sale_date = data.get('sale_date')

    product = Product(
        sku=data.get('sku') or '',  # Let backend generate if not provided
        name=data.get('name'),
        gender=data.get('gender'),
        size=data.get('size'),
        color_print=data.get('color_print'),
        supplier_id=supplier.id,
        cost_price=data.get('cost_price'),
        retail_price=data.get('retail_price'),
        current_quantity=data.get('current_quantity', 0),
        reorder_threshold=data.get('reorder_threshold', 5),
        purchase_date=datetime.fromisoformat(purchase_date) if purchase_date else None,
        sale_date=datetime.fromisoformat(sale_date) if sale_date else None
    )

    if not product.sku:
        product.sku = generate_sku(product)

    db.session.add(product)
    db.session.commit()

    return jsonify({'success': True, 'product': product.to_dict()}), 201

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

    data = request.json
    for field in ['name', 'gender', 'size', 'color_print', 'supplier_id',
                  'cost_price', 'retail_price', 'current_quantity', 'reorder_threshold',
                  'purchase_date', 'sale_date']:
        if field in data:
            if field in ['purchase_date', 'sale_date']:
                setattr(product, field, datetime.fromisoformat(data[field]) if data[field] else None)
            else:
                setattr(product, field, data[field])

    db.session.commit()
    return jsonify({'success': True, 'product': product.to_dict()}), 200

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True, 'message': f'Product {product_id} deleted successfully'}), 200
