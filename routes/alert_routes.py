from flask import Blueprint, jsonify
from models import Product

alert_bp = Blueprint('alert_bp', __name__)

@alert_bp.route('/low-stock', methods=['GET'])
def get_low_stock_alerts():
    low_stock_products = Product.query.filter(Product.current_quantity <= Product.reorder_threshold).all()
    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in low_stock_products]
    }), 200