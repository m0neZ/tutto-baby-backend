# === routes/supplier_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, Fornecedor # Updated import path

# Rename blueprint for consistency
fornecedor_bp = Blueprint("fornecedor_bp", __name__)

@fornecedor_bp.route("/", methods=["GET"])
def get_all_fornecedores():
    # Add query parameter to optionally include inactive suppliers
    include_inactive = request.args.get("include_inactive", "false").lower() == "true"

    query = Fornecedor.query
    if not include_inactive:
        query = query.filter_by(is_active=True)

    fornecedores = query.order_by(Fornecedor.nome).all()
    return jsonify({"success": True, "fornecedores": [f.to_dict() for f in fornecedores]}), 200

@fornecedor_bp.route("/<int:fornecedor_id>", methods=["GET"])
def get_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get(fornecedor_id)
    if not fornecedor:
        return jsonify({"success": False, "error": "Fornecedor não encontrado"}), 404
    return jsonify({"success": True, "fornecedor": fornecedor.to_dict()}), 200

@fornecedor_bp.route("/", methods=["POST"])
def create_fornecedor():
    data = request.json
    nome = data.get("nome")

    if not nome:
        return jsonify({"success": False, "error": "Nome do fornecedor é obrigatório"}), 400

    # Check if supplier with the same name already exists
    existing = Fornecedor.query.filter(db.func.lower(Fornecedor.nome) == nome.lower()).first()
    if existing:
        # Corrected the f-string syntax (removed newlines)
        return jsonify({"success": False, "error": f"Fornecedor '{nome}' já existe"}), 409

    # Create new supplier, active by default
    novo_fornecedor = Fornecedor(nome=nome, is_active=True)

    try:
        db.session.add(novo_fornecedor)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao criar fornecedor.", "details": str(e)}), 500

    return jsonify({"success": True, "fornecedor": novo_fornecedor.to_dict()}), 201

@fornecedor_bp.route("/<int:fornecedor_id>", methods=["PUT"])
def update_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get(fornecedor_id)
    if not fornecedor:
        return jsonify({"success": False, "error": "Fornecedor não encontrado"}), 404

    data = request.json
    nome = data.get("nome")

    if not nome:
        return jsonify({"success": False, "error": "Nome do fornecedor é obrigatório"}), 400

    # Check if another supplier with the same name exists
    existing = Fornecedor.query.filter(
        db.func.lower(Fornecedor.nome) == nome.lower(),
        Fornecedor.id != fornecedor_id
    ).first()
    if existing:
        # Corrected the f-string syntax (removed newlines)
        return jsonify({"success": False, "error": f"Outro fornecedor com o nome '{nome}' já existe"}), 409

    updated = False
    if fornecedor.nome != nome:
        fornecedor.nome = nome
        updated = True

    if updated:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "Erro interno do servidor ao atualizar fornecedor.", "details": str(e)}), 500
        return jsonify({"success": True, "fornecedor": fornecedor.to_dict()}), 200
    else:
        return jsonify({"success": True, "message": "Nenhuma alteração detectada", "fornecedor": fornecedor.to_dict()}), 200

@fornecedor_bp.route("/<int:fornecedor_id>/activate", methods=["PATCH"])
def activate_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get(fornecedor_id)
    if not fornecedor:
        return jsonify({"success": False, "error": "Fornecedor não encontrado"}), 404

    if fornecedor.is_active:
        return jsonify({"success": True, "message": "Fornecedor já está ativo"}), 200

    fornecedor.is_active = True
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao ativar fornecedor.", "details": str(e)}), 500

    return jsonify({"success": True, "message": "Fornecedor ativado com sucesso", "fornecedor": fornecedor.to_dict()}), 200

@fornecedor_bp.route("/<int:fornecedor_id>/deactivate", methods=["PATCH"])
def deactivate_fornecedor(fornecedor_id):
    fornecedor = Fornecedor.query.get(fornecedor_id)
    if not fornecedor:
        return jsonify({"success": False, "error": "Fornecedor não encontrado"}), 404

    if not fornecedor.is_active:
        return jsonify({"success": True, "message": "Fornecedor já está inativo"}), 200

    # Optional: Check if supplier is linked to active products before deactivating?
    # if Produto.query.filter_by(fornecedor_id=fornecedor_id, quantidade_atual > 0).count() > 0:
    #     return jsonify({"success": False, "error": "Não é possível desativar fornecedor com produtos ativos em estoque."}), 400

    fornecedor.is_active = False
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao desativar fornecedor.", "details": str(e)}), 500

    return jsonify({"success": True, "message": "Fornecedor desativado com sucesso", "fornecedor": fornecedor.to_dict()}), 200

# DELETE route is not implemented as per requirement to use activate/deactivate

