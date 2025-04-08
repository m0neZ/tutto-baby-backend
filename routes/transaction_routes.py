# === NEW: routes/transaction_routes.py ===
from flask import Blueprint, request, jsonify
from models import db, InventoryTransaction, Product
from datetime import datetime

transaction_bp = Blueprint('transaction_bp', __name__)

@transaction_bp.route('/', methods=['POST'])
def create_transaction():
    data = request.json
    product = Product.query.get(data.get('product_id'))
    if not product:
        return jsonify({'success': False, 'error': 'Product not found'}), 404

    transaction = InventoryTransaction(
        product_id=product.id,
        transaction_type=data.get('transaction_type'),
        quantity=data.get('quantity'),
        transaction_date=datetime.fromisoformat(data.get('transaction_date')) if data.get('transaction_date') else datetime.utcnow(),
        notes=data.get('notes')
    )

    if transaction.transaction_type == 'purchase':
        product.current_quantity += transaction.quantity
    elif transaction.transaction_type == 'sale':
        if transaction.quantity > product.current_quantity:
            return jsonify({'success': False, 'error': 'Not enough stock'}), 400
        product.current_quantity -= transaction.quantity
    elif transaction.transaction_type == 'return':
        product.current_quantity += transaction.quantity
    elif transaction.transaction_type == 'adjustment':
        product.current_quantity = transaction.quantity

    db.session.add(transaction)
    db.session.commit()

    return jsonify({'success': True, 'transaction': transaction.to_dict(), 'new_quantity': product.current_quantity}), 201