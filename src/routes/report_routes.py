# File: src/routes/report_routes.py

# === routes/report_routes.py ===
from flask import Blueprint, jsonify, request
from src.models import db, Produto, Fornecedor, Venda, ItemVenda, TransacaoEstoque, Cliente
from sqlalchemy import func, case
from datetime import datetime, timedelta

report_bp = Blueprint("report_bp", __name__)

# --- Inventory Reports --- #

@report_bp.route("/relatorios/estoque/niveis", methods=["GET"])
def get_stock_levels():
    """Returns current stock levels for all products."""
    produtos = Produto.query.order_by(Produto.nome).all()
    return jsonify({"success": True, "niveis_estoque": [p.to_dict() for p in produtos]}), 200

@report_bp.route("/relatorios/estoque/baixo", methods=["GET"])
def get_low_stock_products():
    """Returns products that are at or below their reorder threshold."""
    low_stock = Produto.query.filter(
        Produto.quantidade_atual <= Produto.limite_reabastecimento,
        Produto.quantidade_atual > -99999  # Basic filter to avoid erroneous data
    ).order_by(Produto.nome).all()
    return jsonify({"success": True, "produtos_estoque_baixo": [p.to_dict() for p in low_stock]}), 200

# --- Sales & COGS Reports --- #

@report_bp.route("/relatorios/vendas/sumario", methods=["GET"])
def get_sales_summary():
    """Provides a summary of sales over a specified period (default: last 30 days)."""
    end_date_str = request.args.get("end_date")
    start_date_str = request.args.get("start_date")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else datetime.utcnow()
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else end_date - timedelta(days=30)

    # Aggregate sales data
    summary_data = (
        db.session.query(
            Venda.cliente_sobrenome,
            func.count(ItemVenda.id).label("quantidade_itens"),
            func.sum(ItemVenda.preco_venda).label("total_vendas")
        )
        .join(ItemVenda, Venda.id == ItemVenda.venda_id)
        .filter(Venda.data_venda.between(start_date.date(), end_date.date()))
        .group_by(Venda.cliente_sobrenome)
        .all()
    )

    summary = [
        {
            "cliente": cliente,
            "quantidade_itens": int(qtd),
            "total_vendas": float(total or 0)
        }
        for cliente, qtd, total in summary_data
    ]
    return jsonify({"success": True, "sumario_vendas": summary}), 200

# --- Client Reports --- #

@report_bp.route("/relatorios/clientes/sumario", methods=["GET"])
def get_customer_summary():
    """Returns summary of client purchases (name, purchase count, total spent)."""
    client_data = (
        db.session.query(
            func.concat(Cliente.nome, " ", Cliente.sobrenome),
            func.count(Venda.id),
            func.sum(Venda.valor_total)
        )
        .join(Venda, Cliente.id == Venda.cliente_id)
        .group_by(Cliente.id)
        .all()
    )

    summary = [
        {
            "nome_cliente": nome,
            "numero_compras": int(num),
            "total_gasto": float(total or 0)
        }
        for nome, num, total in client_data
    ]
    return jsonify({"success": True, "sumario_clientes": summary}), 200

# (Continue pasting any other endpoints exactly as they were, unchanged below this line)
# …
