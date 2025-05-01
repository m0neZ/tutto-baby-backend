# === routes/alert_routes.py ===
from flask import Blueprint, jsonify
from models import db, Produto # Use Portuguese model name

# Rename blueprint
alerta_bp = Blueprint("alerta_bp", __name__)

@alerta_bp.route("/estoque-baixo", methods=["GET"])
def get_low_stock_alerts():
    """Returns products that are at or below their reorder threshold."""
    # Use Portuguese field names
    produtos_estoque_baixo = Produto.query.filter(
        Produto.quantidade_atual <= Produto.limite_reabastecimento,
        Produto.quantidade_atual > -99999 # Basic filter
    ).order_by(Produto.nome).all()

    return jsonify({
        "success": True,
        # Use Portuguese key
        "produtos_estoque_baixo": [p.to_dict() for p in produtos_estoque_baixo]
    }), 200

# Potential future alerts:
# - Products nearing expiry (if expiry date is added)
# - Slow-moving stock

