# === routes/opcao_campo_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, FieldOption # Updated import path

# Rename blueprint
opcao_campo_bp = Blueprint("opcao_campo_bp", __name__)

# Define allowed field types for this manager
ALLOWED_FIELD_TYPES = ["tamanho", "cor_estampa", "fornecedor"]

@opcao_campo_bp.route("/<tipo_campo>", methods=["GET"])
def get_opcoes_campo(tipo_campo):
    if tipo_campo not in ALLOWED_FIELD_TYPES:
        return jsonify({"success": False, "error": f"Tipo de campo inválido: {tipo_campo}"}), 400

    # Query parameter to include inactive options
    incluir_inativos = request.args.get("incluir_inativos", "false").lower() == "true"

    query = FieldOption.query.filter_by(type=tipo_campo)

    if not incluir_inativos:
        query = query.filter_by(is_active=True)

    # Order by active status (active first), then alphabetically
    opcoes = query.order_by(FieldOption.is_active.desc(), FieldOption.value.asc()).all()
    return jsonify({"success": True, "opcoes": [opt.to_dict() for opt in opcoes]}), 200

@opcao_campo_bp.route("/<tipo_campo>", methods=["POST"])
def add_opcao_campo(tipo_campo):
    if tipo_campo not in ALLOWED_FIELD_TYPES:
        return jsonify({"success": False, "error": f"Tipo de campo inválido: {tipo_campo}"}), 400

    data = request.get_json()
    valor = data.get("value", "").strip()

    if not valor:
        return jsonify({"success": False, "error": "O valor da opção é obrigatório"}), 400

    # Check if option already exists (case-insensitive check)
    existing = FieldOption.query.filter(
        FieldOption.type == tipo_campo,
        db.func.lower(FieldOption.value) == valor.lower()
    ).first()

    if existing:
        # If exists and is inactive, reactivate it instead of erroring?
        # Or just return error as implemented now.
        # Corrected the f-string syntax
        error_message = f"A opção '{valor}' já existe para {tipo_campo}." # Corrected f-string on single line
        return jsonify({"success": False, "error": error_message}), 409

    # Create new option, active by default
    nova_opcao = FieldOption(type=tipo_campo, value=valor, is_active=True)

    try:
        db.session.add(nova_opcao)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao adicionar opção.", "details": str(e)}), 500

    return jsonify({"success": True, "opcao": nova_opcao.to_dict()}), 201

@opcao_campo_bp.route("/<int:opcao_id>/deactivate", methods=["PATCH"])
def deactivate_opcao(opcao_id):
    opcao = FieldOption.query.get(opcao_id)
    if not opcao:
        return jsonify({"success": False, "error": "Opção não encontrada"}), 404

    if not opcao.is_active:
        return jsonify({"success": True, "message": "Opção já está inativa"}), 200

    # Optional: Check if this option is currently used by active products?

    opcao.is_active = False
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao desativar opção.", "details": str(e)}), 500

    return jsonify({"success": True, "message": "Opção desativada com sucesso", "opcao": opcao.to_dict()}), 200

@opcao_campo_bp.route("/<int:opcao_id>/activate", methods=["PATCH"])
def activate_opcao(opcao_id):
    opcao = FieldOption.query.get(opcao_id)
    if not opcao:
        return jsonify({"success": False, "error": "Opção não encontrada"}), 404

    if opcao.is_active:
        return jsonify({"success": True, "message": "Opção já está ativa"}), 200

    opcao.is_active = True
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao ativar opção.", "details": str(e)}), 500

    return jsonify({"success": True, "message": "Opção ativada com sucesso", "opcao": opcao.to_dict()}), 200

# DELETE route is not implemented as per requirement to use activate/deactivate

