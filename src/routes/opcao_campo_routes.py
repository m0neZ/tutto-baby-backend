# === routes/opcao_campo_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, FieldOption, Produto, Fornecedor # Updated import path

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

# Updated endpoint for editing option value with product propagation
@opcao_campo_bp.route("/<tipo_campo>/<int:opcao_id>", methods=["PUT"])
def update_opcao_campo(tipo_campo, opcao_id):
    if tipo_campo not in ALLOWED_FIELD_TYPES:
        return jsonify({"success": False, "error": f"Tipo de campo inválido: {tipo_campo}"}), 400
        
    opcao = FieldOption.query.get(opcao_id)
    if not opcao:
        return jsonify({"success": False, "error": "Opção não encontrada"}), 404
        
    if opcao.type != tipo_campo:
        return jsonify({"success": False, "error": f"Opção não pertence ao tipo {tipo_campo}"}), 400
        
    data = request.get_json()
    novo_valor = data.get("value", "").strip()
    update_products = data.get("update_products", True)  # Default to True for backward compatibility
    
    if not novo_valor:
        return jsonify({"success": False, "error": "O valor da opção é obrigatório"}), 400
        
    # Check if new value already exists for another option
    existing = FieldOption.query.filter(
        FieldOption.type == tipo_campo,
        db.func.lower(FieldOption.value) == novo_valor.lower(),
        FieldOption.id != opcao_id
    ).first()
    
    if existing:
        error_message = f"A opção '{novo_valor}' já existe para {tipo_campo}."
        return jsonify({"success": False, "error": error_message}), 409
    
    # Store old value for product updates
    old_value = opcao.value
    
    # Update option value
    opcao.value = novo_valor
    
    try:
        # Commit the option change first
        db.session.commit()
        
        # Update all products using this option if requested
        updated_count = 0
        if update_products:
            if tipo_campo == "tamanho":
                # For tamanho, update all matching products directly
                products = Produto.query.filter(Produto.tamanho == old_value).all()
                for product in products:
                    product.tamanho = novo_valor
                    updated_count += 1
                
            elif tipo_campo == "cor_estampa":
                # For cor_estampa, update all matching products directly
                products = Produto.query.filter(Produto.cor_estampa == old_value).all()
                for product in products:
                    product.cor_estampa = novo_valor
                    updated_count += 1
                
            elif tipo_campo == "fornecedor":
                # For fornecedor, we need to find the fornecedor by name and update products
                # First, find the fornecedor with the old name
                old_fornecedor = Fornecedor.query.filter(Fornecedor.nome == old_value).first()
                if old_fornecedor:
                    # Create or update fornecedor with new name
                    new_fornecedor = Fornecedor.query.filter(Fornecedor.nome == novo_valor).first()
                    if not new_fornecedor:
                        # Create new fornecedor if it doesn't exist
                        new_fornecedor = Fornecedor(nome=novo_valor, is_active=old_fornecedor.is_active)
                        db.session.add(new_fornecedor)
                        db.session.flush()  # Get ID without committing
                    
                    # Update all products using the old fornecedor
                    products = Produto.query.filter(Produto.fornecedor_id == old_fornecedor.id).all()
                    for product in products:
                        product.fornecedor_id = new_fornecedor.id
                        updated_count += 1
            
            # Commit all product updates
            if updated_count > 0:
                db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": f"Opção atualizada com sucesso. {updated_count} produtos atualizados.", 
            "opcao": opcao.to_dict(),
            "updated_products": updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": f"Erro interno do servidor ao atualizar opção: {str(e)}", 
            "details": str(e)
        }), 500

# New endpoint for toggling option status
@opcao_campo_bp.route("/<tipo_campo>/<int:opcao_id>/status", methods=["PUT"])
def toggle_opcao_status(tipo_campo, opcao_id):
    if tipo_campo not in ALLOWED_FIELD_TYPES:
        return jsonify({"success": False, "error": f"Tipo de campo inválido: {tipo_campo}"}), 400
        
    opcao = FieldOption.query.get(opcao_id)
    if not opcao:
        return jsonify({"success": False, "error": "Opção não encontrada"}), 404
        
    if opcao.type != tipo_campo:
        return jsonify({"success": False, "error": f"Opção não pertence ao tipo {tipo_campo}"}), 400
        
    data = request.get_json()
    is_active = data.get("is_active")
    
    if is_active is None:
        return jsonify({"success": False, "error": "O status da opção é obrigatório"}), 400
        
    # Update option status
    opcao.is_active = bool(is_active)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": "Erro interno do servidor ao atualizar status da opção.", "details": str(e)}), 500
        
    status_msg = "ativada" if opcao.is_active else "desativada"
    return jsonify({"success": True, "message": f"Opção {status_msg} com sucesso", "opcao": opcao.to_dict()}), 200

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

# Special endpoint to generate authentication token for admin operations
@opcao_campo_bp.route("/admin_token", methods=["POST"])
def generate_admin_token():
    from flask import current_app
    import jwt
    import datetime
    
    # This is a simplified version - in production, you would validate credentials
    # For this example, we're creating a token with admin privileges
    
    payload = {
        'sub': 'admin',
        'role': 'admin',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    
    token = jwt.encode(
        payload,
        current_app.config.get('SECRET_KEY', 'dev_key'),
        algorithm='HS256'
    )
    
    return jsonify({
        'success': True,
        'token': token,
        'message': 'Use este token para operações administrativas como limpar dados de teste'
    }), 200
