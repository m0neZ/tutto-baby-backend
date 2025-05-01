from flask import Blueprint, jsonify
from models import Product

summary_bp = Blueprint('summary_bp', __name__)

@summary_bp.route('/summary', methods=['GET'])
def get_inventory_summary():
    products = Product.query.all()
    total_products = len(products)
    total_cost_value = sum(p.cost_price * p.current_quantity for p in products)
    total_retail_value = sum(p.retail_price * p.current_quantity for p in products)
    low_stock_count = sum(1 for p in products if p.current_quantity <= p.reorder_threshold)

    return jsonify({
        'success': True,
        'summary': {
            'total_products': total_products,
            'total_cost_value': round(total_cost_value, 2),
            'total_retail_value': round(total_retail_value, 2),
            'low_stock_count': low_stock_count
        }
    }), 200