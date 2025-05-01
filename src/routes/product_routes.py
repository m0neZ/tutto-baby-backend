# === routes/product_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, Produto, Fornecedor, TransacaoEstoque # Updated import path
from src.utils.helpers import generate_sku # Updated import path
from datetime import datetime

# Rename blueprint for consistency
produto_bp = Blueprint("produto_bp", __name__)

@produto_bp.route("/", methods=["GET"])
def get_all_produtos():
    # Query the Produto model
    produtos = Produto.query.order_by(Produto.nome).all()
    return jsonify({"success": True, "produtos": [p.to_dict() for p in produtos]}), 200

@produto_bp.route("/<int:produto_id>", methods=["GET"])
def get_produto(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"success": False, "error": "Produto não encontrado"}), 404
    return jsonify({"success": True, "produto": produto.to_dict()}), 200

@produto_bp.route("/", methods=["POST"])
def create_produto():
    data = request.json
    # Use Portuguese field names from request
    fornecedor_id = data.get("fornecedor_id")
    nome = data.get("nome")
    sexo = data.get("sexo")
    tamanho = data.get("tamanho")
    cor_estampa = data.get("cor_estampa")
    custo = data.get("custo")
    preco_venda = data.get("preco_venda")
    quantidade_inicial = data.get("quantidade_atual", 0) # Use quantidade_atual for initial quantity
    limite_reabastecimento = data.get("limite_reabastecimento", 5)
    data_compra_str = data.get("data_compra")

    # Basic validation
    if not all([nome, sexo, tamanho, cor_estampa, fornecedor_id, custo is not None, preco_venda is not None]):
        return jsonify({"success": False, "error": "Campos obrigatórios ausentes"}), 400

    fornecedor = Fornecedor.query.get(fornecedor_id)
    if not fornecedor:
        return jsonify({"success": False, "error": "Fornecedor não encontrado"}), 404
    if not fornecedor.is_active:
         return jsonify({"success": False, "error": "Fornecedor inativo"}), 400

    try:
        custo = float(custo)
        preco_venda = float(preco_venda)
        quantidade_inicial = int(quantidade_inicial)
        limite_reabastecimento = int(limite_reabastecimento)
        # Corrected the format string for strptime
        data_compra = datetime.strptime(data_compra_str, "%Y-%m-%d").date() if data_compra_str else None
    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": f"Erro de tipo de dado: {e}"}), 400

    # Create Produto instance
    novo_produto = Produto(
        nome=nome,
        sexo=sexo,
        tamanho=tamanho,
        cor_estampa=cor_estampa,
        fornecedor_id=fornecedor.id,
        custo=custo,
        preco_venda=preco_venda,
        quantidade_atual=quantidade_inicial,
        limite_reabastecimento=limite_reabastecimento,
        data_compra=data_compra
        # SKU is generated below
    )

    # Generate SKU before adding to session to ensure uniqueness check works
    novo_produto.sku = generate_sku(novo_produto)

    db.session.add(novo_produto)

    # Create initial inventory transaction if quantity > 0
    if quantidade_inicial > 0:
        transacao = TransacaoEstoque(
            produto=novo_produto,
            tipo_transacao="compra", # Initial stock entry
            quantidade=quantidade_inicial,
            observacoes="Estoque inicial",
            custo_unitario_transacao=custo # Record cost at time of entry
        )
        db.session.add(transacao)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Check for unique constraint violation (e.g., SKU)
        if "UNIQUE constraint failed" in str(e):
             return jsonify({"success": False, "error": "Falha ao criar produto: SKU duplicado ou outro erro de restrição.", "details": str(e)}), 409
        return jsonify({"success": False, "error": "Erro interno do servidor ao salvar.", "details": str(e)}), 500

    return jsonify({"success": True, "produto": novo_produto.to_dict()}), 201

@produto_bp.route("/<int:produto_id>", methods=["PUT"])
def update_produto(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"success": False, "error": "Produto não encontrado"}), 404

    data = request.json
    updated = False

    # Fields allowed to update (excluding quantity, handled via transactions)
    allowed_fields = {
        "nome": str,
        "sexo": str,
        "tamanho": str,
        "cor_estampa": str,
        "fornecedor_id": int,
        "custo": float,
        "preco_venda": float,
        "limite_reabastecimento": int,
        "data_compra": "date" # Special handling for date
    }

    for field, field_type in allowed_fields.items():
        if field in data:
            new_value = data[field]
            try:
                if field_type == "date":
                    # Corrected the format string for strptime
                    new_value = datetime.strptime(new_value, "%Y-%m-%d").date() if new_value else None
                elif field_type == int:
                    new_value = int(new_value)
                elif field_type == float:
                    new_value = float(new_value)
                # Add validation for foreign keys if needed (e.g., check if fornecedor_id exists)
                if field == "fornecedor_id":
                    fornecedor = Fornecedor.query.get(new_value)
                    if not fornecedor:
                         return jsonify({"success": False, "error": f"Fornecedor com ID {new_value} não encontrado"}), 404
                    if not fornecedor.is_active:
                         return jsonify({"success": False, "error": f"Fornecedor {fornecedor.nome} está inativo"}), 400

                if getattr(produto, field) != new_value:
                    setattr(produto, field, new_value)
                    updated = True
            except (ValueError, TypeError):
                 return jsonify({"success": False, "error": f"Valor inválido para o campo {field}"}), 400

    if updated:
        # Note: SKU regeneration might be needed if key attributes change, depends on requirements.
        # For now, SKU is not regenerated on update.
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "Erro interno do servidor ao atualizar.", "details": str(e)}), 500
        return jsonify({"success": True, "produto": produto.to_dict()}), 200
    else:
        return jsonify({"success": True, "message": "Nenhuma alteração detectada", "produto": produto.to_dict()}), 200

@produto_bp.route("/<int:produto_id>", methods=["DELETE"])
def delete_produto(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"success": False, "error": "Produto não encontrado"}), 404

    # Check for related transactions or sales before deleting? (Optional, depends on requirements)
    # if produto.transacoes or produto.itens_venda:
    #     return jsonify({"success": False, "error": "Não é possível excluir produto com histórico de transações ou vendas."}), 400

    try:
        db.session.delete(produto)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao excluir.", "details": str(e)}), 500

    return jsonify({"success": True, "message": f"Produto {produto_id} excluído com sucesso"}), 200

