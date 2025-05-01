# === routes/report_routes.py ===
from flask import Blueprint, jsonify, request
from models import db, Produto, Fornecedor, Venda, ItemVenda, TransacaoEstoque, Cliente
from sqlalchemy import func, case
from datetime import datetime, timedelta

report_bp = Blueprint("report_bp", __name__)

# --- Inventory Reports --- #

@report_bp.route("/relatorios/estoque/niveis", methods=["GET"])
def get_stock_levels():
    """Returns current stock levels for all products."""
    produtos = Produto.query.order_by(Produto.nome).all()
    # Consider adding filters (e.g., by supplier, category if added later)
    return jsonify({"success": True, "niveis_estoque": [p.to_dict() for p in produtos]}), 200

@report_bp.route("/relatorios/estoque/valor", methods=["GET"])
def get_inventory_value():
    """Calculates the total value of the current inventory based on cost and retail price."""
    total_custo = db.session.query(func.sum(Produto.custo * Produto.quantidade_atual)).scalar() or 0
    total_venda = db.session.query(func.sum(Produto.preco_venda * Produto.quantidade_atual)).scalar() or 0
    total_quantidade = db.session.query(func.sum(Produto.quantidade_atual)).scalar() or 0
    total_skus = db.session.query(func.count(Produto.id)).scalar() or 0

    return jsonify({
        "success": True,
        "valor_inventario": {
            "total_skus": total_skus,
            "total_quantidade_itens": int(total_quantidade),
            "valor_total_custo": round(total_custo, 2),
            "valor_total_venda": round(total_venda, 2)
        }
    }), 200

@report_bp.route("/relatorios/estoque/baixo", methods=["GET"])
def get_low_stock_products():
    """Returns products that are at or below their reorder threshold."""
    low_stock = Produto.query.filter(
        Produto.quantidade_atual <= Produto.limite_reabastecimento,
        Produto.quantidade_atual > -99999 # Basic filter to avoid potentially erroneous data
    ).order_by(Produto.nome).all()
    return jsonify({"success": True, "produtos_estoque_baixo": [p.to_dict() for p in low_stock]}), 200

# --- Sales & COGS Reports --- #

@report_bp.route("/relatorios/vendas/sumario", methods=["GET"])
def get_sales_summary():
    """Provides a summary of sales over a specified period (default: last 30 days)."""
    end_date_str = request.args.get("end_date")
    start_date_str = request.args.get("start_date")

    try:
        # Corrected the format strings for strptime
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else datetime.utcnow()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else end_date - timedelta(days=30)
        # Ensure end_date includes the whole day
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        return jsonify({"success": False, "error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    sales_query = Venda.query.filter(
        Venda.data_venda >= start_date,
        Venda.data_venda <= end_date
    )

    total_sales_value = sales_query.with_entities(func.sum(Venda.valor_total)).scalar() or 0
    number_of_sales = sales_query.count()

    # Calculate COGS for the period
    cogs_query = db.session.query(func.sum(ItemVenda.custo_unitario * ItemVenda.quantidade)).join(Venda).filter(
        Venda.data_venda >= start_date,
        Venda.data_venda <= end_date
    )
    total_cogs = cogs_query.scalar() or 0
    gross_profit = total_sales_value - total_cogs

    # Best selling products in the period
    # Added explicit line continuation backslashes
    best_sellers = db.session.query(
        Produto.nome,
        func.sum(ItemVenda.quantidade).label("total_vendido")
    ).join(ItemVenda, ItemVenda.produto_id == Produto.id)\
     .join(Venda, Venda.id == ItemVenda.venda_id)\
     .filter(
        Venda.data_venda >= start_date,
        Venda.data_venda <= end_date
     )\
     .group_by(Produto.nome)\
     .order_by(func.sum(ItemVenda.quantidade).desc())\
     .limit(10)\
     .all()

    return jsonify({
        "success": True,
        "periodo": {
            "inicio": start_date.strftime("%Y-%m-%d"),
            "fim": end_date.strftime("%Y-%m-%d")
        },
        "sumario_vendas": {
            "numero_vendas": number_of_sales,
            "valor_total_vendas": round(total_sales_value, 2),
            "custo_produtos_vendidos_cogs": round(total_cogs, 2),
            "lucro_bruto": round(gross_profit, 2),
            "top_10_produtos_vendidos": [{"nome": nome, "quantidade": int(qtd)} for nome, qtd in best_sellers]
        }
    }), 200

# --- Supplier Reports --- #

@report_bp.route("/relatorios/fornecedores/sumario", methods=["GET"])
def get_supplier_summary():
    """Provides insights about suppliers."""
    # Total spent per supplier (based on product cost * initial quantity or purchase transactions)
    # Using initial product cost * current quantity might not be accurate for total spent.
    # A better approach involves summing purchase transactions if available, or initial cost.
    # For simplicity, let's calculate based on current products associated with the supplier.

    supplier_data = db.session.query(
        Fornecedor.nome,
        func.count(Produto.id).label("num_produtos"),
        func.sum(Produto.custo * Produto.quantidade_atual).label("valor_estoque_atual_custo")
    ).outerjoin(Produto, Fornecedor.id == Produto.fornecedor_id)\
     .group_by(Fornecedor.nome)\
     .order_by(Fornecedor.nome)\
     .all()

    summary = [
        {
            "nome_fornecedor": nome,
            "produtos_associados": num_prod,
            "valor_estoque_atual_custo": round(valor_custo or 0, 2)
        }
        for nome, num_prod, valor_custo in supplier_data
    ]

    return jsonify({"success": True, "sumario_fornecedores": summary}), 200

# --- Client Reports (Bonus) --- #

@report_bp.route("/relatorios/clientes/sumario", methods=["GET"])
def get_client_summary():
    """Provides insights about clients."""
    client_data = db.session.query(
        Cliente.nome,
        func.count(Venda.id).label("num_compras"),
        func.sum(Venda.valor_total).label("total_gasto")
    ).outerjoin(Venda, Cliente.id == Venda.cliente_id)\
     .group_by(Cliente.nome)\
     .order_by(func.sum(Venda.valor_total).desc().nullslast())\
     .all()

    summary = [
        {
            "nome_cliente": nome,
            "numero_compras": num_compras,
            "total_gasto": round(total_gasto or 0, 2)
        }
        for nome, num_compras, total_gasto in client_data
    ]

    return jsonify({"success": True, "sumario_clientes": summary}), 200

