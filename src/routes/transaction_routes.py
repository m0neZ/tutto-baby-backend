# === routes/transaction_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, TransacaoEstoque, Produto # Updated import path
from datetime import datetime

# Rename blueprint
transacao_bp = Blueprint("transacao_bp", __name__)

# GET route to fetch transactions (useful for history/audit)
@transacao_bp.route("/", methods=["GET"])
def get_all_transacoes():
    # Add filtering by product_id, date range, type etc. later if needed
    produto_id = request.args.get("produto_id", type=int)

    query = TransacaoEstoque.query.order_by(TransacaoEstoque.data_transacao.desc())

    if produto_id:
        query = query.filter_by(produto_id=produto_id)

    transacoes = query.all()
    return jsonify({"success": True, "transacoes": [t.to_dict() for t in transacoes]}), 200

# POST route primarily for adjustments and returns (purchases/sales handled elsewhere)
@transacao_bp.route("/", methods=["POST"])
def create_transacao_manual():
    data = request.json
    produto_id = data.get("produto_id")
    tipo_transacao = data.get("tipo_transacao") # Should be 'ajuste' or 'devolucao'
    quantidade_str = data.get("quantidade")
    observacoes = data.get("observacoes")
    data_transacao_str = data.get("data_transacao")

    if tipo_transacao not in ["ajuste", "devolucao"]:
        return jsonify({"success": False, "error": "Tipo de transação inválido para esta rota. Use 'ajuste' ou 'devolucao'."}), 400

    if not produto_id or not quantidade_str:
        return jsonify({"success": False, "error": "ID do produto e quantidade são obrigatórios."}), 400

    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"success": False, "error": "Produto não encontrado"}), 404

    try:
        quantidade = int(quantidade_str)
        if quantidade == 0:
             return jsonify({"success": False, "error": "Quantidade não pode ser zero."}), 400
        # Adjustments can be positive or negative, returns are positive
        if tipo_transacao == "devolucao" and quantidade < 0:
             return jsonify({"success": False, "error": "Quantidade para devolução deve ser positiva."}), 400

        # Corrected the format string for strptime
        data_transacao = datetime.strptime(data_transacao_str, "%Y-%m-%dT%H:%M:%S.%fZ") if data_transacao_str else datetime.utcnow()
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": f"Erro no formato dos dados: {e}"}), 400

    # Create the transaction record
    transacao = TransacaoEstoque(
        produto_id=produto.id,
        tipo_transacao=tipo_transacao,
        quantidade=quantidade,
        data_transacao=data_transacao,
        observacoes=observacoes,
        # Cost for adjustments/returns might be tricky - using current product cost
        custo_unitario_transacao=produto.custo
    )

    # Update product quantity
    produto.quantidade_atual += quantidade # Add quantity (positive for return/increase, negative for decrease adjustment)

    # Ensure quantity doesn't go below zero unintentionally (though adjustments might allow it)
    # if produto.quantidade_atual < 0:
    #     db.session.rollback()
    #     return jsonify({"success": False, "error": "Ajuste resultaria em estoque negativo."}), 400

    try:
        db.session.add(transacao)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao criar transação.", "details": str(e)}), 500

    return jsonify({
        "success": True,
        "transacao": transacao.to_dict(),
        "nova_quantidade_produto": produto.quantidade_atual
    }), 201

