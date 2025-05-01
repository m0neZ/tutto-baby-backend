# === routes/sale_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, Venda, ItemVenda, Produto, Cliente, TransacaoEstoque # Updated import path
from datetime import datetime

venda_bp = Blueprint("venda_bp", __name__)

@venda_bp.route("/", methods=["GET"])
def get_all_vendas():
    # Add filtering/pagination later if needed
    vendas = Venda.query.order_by(Venda.data_venda.desc()).all()
    return jsonify({"success": True, "vendas": [v.to_dict() for v in vendas]}), 200

@venda_bp.route("/<int:venda_id>", methods=["GET"])
def get_venda(venda_id):
    venda = Venda.query.get(venda_id)
    if not venda:
        return jsonify({"success": False, "error": "Venda não encontrada"}), 404
    return jsonify({"success": True, "venda": venda.to_dict()}), 200

@venda_bp.route("/", methods=["POST"])
def create_venda():
    data = request.json
    cliente_id = data.get("cliente_id")
    itens_data = data.get("itens") # Expecting a list of { "produto_id": id, "quantidade": qty }
    observacoes = data.get("observacoes")
    data_venda_str = data.get("data_venda") # Optional, defaults to now

    if not itens_data or not isinstance(itens_data, list) or len(itens_data) == 0:
        return jsonify({"success": False, "error": "A venda deve conter pelo menos um item."}), 400

    cliente = None
    if cliente_id:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({"success": False, "error": f"Cliente com ID {cliente_id} não encontrado."}), 404

    try:
        # Corrected the format string for strptime
        data_venda = datetime.strptime(data_venda_str, "%Y-%m-%dT%H:%M:%S.%fZ") if data_venda_str else datetime.utcnow()
        # Alternative format if only date is sent: datetime.strptime(data_venda_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        data_venda = datetime.utcnow() # Default to now if format is wrong or missing

    nova_venda = Venda(
        cliente_id=cliente.id if cliente else None,
        data_venda=data_venda,
        observacoes=observacoes,
        valor_total=0 # Will be calculated after adding items
    )
    db.session.add(nova_venda)

    # Process items and create inventory transactions
    total_venda = 0
    transacoes_para_adicionar = []
    itens_para_adicionar = []

    for item_data in itens_data:
        produto_id = item_data.get("produto_id")
        quantidade = item_data.get("quantidade")

        if not produto_id or not isinstance(quantidade, int) or quantidade <= 0:
            db.session.rollback() # Rollback if any item is invalid
            return jsonify({"success": False, "error": f"Dados inválidos para o item: {item_data}"}), 400

        produto = Produto.query.get(produto_id)
        if not produto:
            db.session.rollback()
            return jsonify({"success": False, "error": f"Produto com ID {produto_id} não encontrado."}), 404

        if produto.quantidade_atual < quantidade:
            db.session.rollback()
            # Corrected the f-string to remove the problematic newline
            error_message = f"Estoque insuficiente para {produto.nome}. Disponível: {produto.quantidade_atual}, Solicitado: {quantidade}."
            return jsonify({"success": False, "error": error_message}), 400

        # Decrease stock
        produto.quantidade_atual -= quantidade

        # Create SaleItem
        item_venda = ItemVenda(
            venda=nova_venda, # Associate with the sale being created
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco_venda, # Price at time of sale
            custo_unitario=produto.custo # Cost at time of sale (for COGS)
        )
        itens_para_adicionar.append(item_venda)
        total_venda += item_venda.preco_unitario * item_venda.quantidade

        # Create Inventory Transaction
        transacao = TransacaoEstoque(
            produto_id=produto.id,
            tipo_transacao="venda",
            quantidade=-quantidade, # Negative quantity for sale
            data_transacao=data_venda,
            observacoes=f"Venda ID: {nova_venda.id}", # Will be updated after commit
            custo_unitario_transacao=produto.custo, # Record cost for COGS
            venda=nova_venda # Link transaction to sale
        )
        transacoes_para_adicionar.append(transacao)

    # Update total sale amount
    nova_venda.valor_total = total_venda

    # Add all items and transactions
    db.session.add_all(itens_para_adicionar)
    db.session.add_all(transacoes_para_adicionar)

    try:
        db.session.flush() # Flush to get nova_venda.id
        # Update transaction notes with Sale ID
        for t in transacoes_para_adicionar:
            t.observacoes = f"Venda ID: {nova_venda.id}"
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao registrar venda.", "details": str(e)}), 500

    return jsonify({"success": True, "venda": nova_venda.to_dict()}), 201

# PUT/DELETE for Sales might be complex due to inventory implications.
# Usually, sales are adjusted via Returns or Credit Notes rather than direct modification/deletion.
# For now, only GET and POST are implemented.

