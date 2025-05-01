# === routes/client_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, Cliente # Updated import path

cliente_bp = Blueprint("cliente_bp", __name__)

@cliente_bp.route("/", methods=["GET"])
def get_all_clientes():
    # Add search/filtering later if needed
    clientes = Cliente.query.order_by(Cliente.nome).all()
    return jsonify({"success": True, "clientes": [c.to_dict() for c in clientes]}), 200

@cliente_bp.route("/<int:cliente_id>", methods=["GET"])
def get_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"success": False, "error": "Cliente não encontrado"}), 404
    return jsonify({"success": True, "cliente": cliente.to_dict()}), 200

@cliente_bp.route("/", methods=["POST"])
def create_cliente():
    data = request.json
    nome = data.get("nome")
    telefone = data.get("telefone")
    email = data.get("email")
    endereco = data.get("endereco")
    observacoes = data.get("observacoes")

    if not nome:
        return jsonify({"success": False, "error": "Nome do cliente é obrigatório"}), 400

    # Optional: Check for duplicate client based on name/email/phone?

    novo_cliente = Cliente(
        nome=nome,
        telefone=telefone,
        email=email,
        endereco=endereco,
        observacoes=observacoes
    )

    try:
        db.session.add(novo_cliente)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao criar cliente.", "details": str(e)}), 500

    return jsonify({"success": True, "cliente": novo_cliente.to_dict()}), 201

@cliente_bp.route("/<int:cliente_id>", methods=["PUT"])
def update_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"success": False, "error": "Cliente não encontrado"}), 404

    data = request.json
    updated = False

    fields_to_update = ["nome", "telefone", "email", "endereco", "observacoes"]
    for field in fields_to_update:
        if field in data:
            new_value = data[field]
            # Add specific validation if needed (e.g., email format)
            if getattr(cliente, field) != new_value:
                setattr(cliente, field, new_value)
                updated = True

    # Ensure name is not empty after update
    if not cliente.nome:
         return jsonify({"success": False, "error": "Nome do cliente não pode ser vazio"}), 400

    if updated:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": "Erro interno do servidor ao atualizar cliente.", "details": str(e)}), 500
        return jsonify({"success": True, "cliente": cliente.to_dict()}), 200
    else:
        return jsonify({"success": True, "message": "Nenhuma alteração detectada", "cliente": cliente.to_dict()}), 200

@cliente_bp.route("/<int:cliente_id>", methods=["DELETE"])
def delete_cliente(cliente_id):
    cliente = Cliente.query.get(cliente_id)
    if not cliente:
        return jsonify({"success": False, "error": "Cliente não encontrado"}), 404

    # Optional: Check if client has associated sales before deleting?
    # if cliente.vendas:
    #     return jsonify({"success": False, "error": "Não é possível excluir cliente com histórico de vendas."}), 400

    try:
        db.session.delete(cliente)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao excluir cliente.", "details": str(e)}), 500

    return jsonify({"success": True, "message": f"Cliente {cliente_id} excluído com sucesso"}), 200

