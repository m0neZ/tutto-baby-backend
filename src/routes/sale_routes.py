# === routes/sale_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, Venda, ItemVenda, Produto, TransacaoEstoque
from datetime import datetime
from sqlalchemy import func
from src.models.troca import Troca, ItemTroca

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
    cliente_nome = data.get("cliente_nome")
    cliente_sobrenome = data.get("cliente_sobrenome")
    forma_pagamento = data.get("forma_pagamento")
    data_venda = data.get("data_venda")
    produtos = data.get("produtos", [])
    status = data.get("status", "Pagamento Pendente")
    
    # Validate required fields
    if not cliente_nome:
        return jsonify({"success": False, "error": "Nome do cliente é obrigatório"}), 400
    
    if not produtos or not isinstance(produtos, list) or len(produtos) == 0:
        return jsonify({"success": False, "error": "Pelo menos um produto deve ser selecionado"}), 400
    
    # Validate products
    for item in produtos:
        produto_id = item.get("produto_id")
        if not produto_id:
            return jsonify({"success": False, "error": "ID do produto é obrigatório"}), 400
        
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"success": False, "error": f"Produto com ID {produto_id} não encontrado"}), 404
        
        # Check if product is available in stock
        if produto.quantidade_atual <= 0:
            return jsonify({"success": False, "error": f"Produto {produto.nome} não está disponível em estoque"}), 400
    
    try:
        # Parse date
        venda_date = datetime.strptime(data_venda, "%Y-%m-%d") if data_venda else datetime.utcnow()
        
        # Calculate total value
        valor_total = sum(float(item.get("preco_venda", 0)) for item in produtos)
        
        # Create sale record
        nova_venda = Venda(
            cliente_nome=cliente_nome,
            cliente_sobrenome=cliente_sobrenome,
            forma_pagamento=forma_pagamento,
            data_venda=venda_date,
            valor_total=valor_total,
            status=status
        )
        db.session.add(nova_venda)
        db.session.flush()  # Get ID for the new sale
        
        # Add products to sale and update inventory
        for item in produtos:
            produto_id = item.get("produto_id")
            produto = Produto.query.get(produto_id)
            
            # Add to sale items
            item_venda = ItemVenda(
                venda_id=nova_venda.id,
                produto_id=produto_id,
                quantidade=1,  # Always 1 in single-unit paradigm
                preco_unitario=produto.preco_venda,
                custo_unitario=produto.custo
            )
            db.session.add(item_venda)
            
            # Update inventory - FIFO logic
            # In single-unit paradigm, just set quantity to 0
            produto.quantidade_atual = 0
            
            # Create inventory transaction
            transacao = TransacaoEstoque(
                produto_id=produto_id,
                tipo_transacao="venda",
                quantidade=-1,  # Negative for removal from stock
                data_transacao=venda_date,
                observacoes=f"Venda ID: {nova_venda.id}",
                venda_id=nova_venda.id
            )
            db.session.add(transacao)
        
        db.session.commit()
        return jsonify({"success": True, "venda": nova_venda.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": "Erro interno do servidor ao criar venda.", 
            "details": str(e)
        }), 500

@venda_bp.route("/<int:venda_id>", methods=["PATCH"])
def update_venda(venda_id):
    venda = Venda.query.get(venda_id)
    if not venda:
        return jsonify({"success": False, "error": "Venda não encontrada"}), 404
    
    data = request.json
    
    # Update basic info
    if "cliente_nome" in data:
        venda.cliente_nome = data["cliente_nome"]
    if "cliente_sobrenome" in data:
        venda.cliente_sobrenome = data["cliente_sobrenome"]
    if "forma_pagamento" in data:
        venda.forma_pagamento = data["forma_pagamento"]
    if "data_venda" in data:
        venda.data_venda = datetime.strptime(data["data_venda"], "%Y-%m-%d")
    if "status" in data:
        venda.status = data["status"]
    if "observacoes" in data:
        venda.observacoes = data["observacoes"]
    
    # Handle product changes if provided
    if "produtos" in data and isinstance(data["produtos"], list):
        # This is more complex and requires careful handling of inventory
        # For simplicity, we'll just update the existing products
        # A more robust implementation would handle adding/removing products
        pass
    
    try:
        db.session.commit()
        return jsonify({"success": True, "venda": venda.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": "Erro interno do servidor ao atualizar venda.", 
            "details": str(e)
        }), 500

@venda_bp.route("/<int:venda_id>", methods=["DELETE"])
def delete_venda(venda_id):
    venda = Venda.query.get(venda_id)
    if not venda:
        return jsonify({"success": False, "error": "Venda não encontrada"}), 404
    
    try:
        # Get all products from this sale
        itens = ItemVenda.query.filter_by(venda_id=venda_id).all()
        
        # Return products to inventory if sale is being deleted
        for item in itens:
            produto = Produto.query.get(item.produto_id)
            if produto:
                # Return to inventory
                produto.quantidade_atual = 1  # Set back to 1 since it's being returned
                
                # Create inventory transaction
                transacao = TransacaoEstoque(
                    produto_id=item.produto_id,
                    tipo_transacao="cancelamento",
                    quantidade=1,  # Positive for return to stock
                    data_transacao=datetime.utcnow(),
                    observacoes=f"Cancelamento de Venda ID: {venda_id}"
                )
                db.session.add(transacao)
        
        # Update sale status instead of deleting
        venda.status = "Cancelado"
        
        db.session.commit()
        return jsonify({"success": True, "message": "Venda cancelada com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": "Erro interno do servidor ao cancelar venda.", 
            "details": str(e)
        }), 500

@venda_bp.route("/<int:venda_id>/confirm-payment", methods=["POST"])
def confirm_payment(venda_id):
    venda = Venda.query.get(venda_id)
    if not venda:
        return jsonify({"success": False, "error": "Venda não encontrada"}), 404
    
    if venda.status != "Pagamento Pendente":
        return jsonify({"success": False, "error": "Esta venda não está com pagamento pendente"}), 400
    
    data = request.json
    valor_pago = data.get("valor_pago")
    data_pagamento = data.get("data_pagamento")
    observacoes = data.get("observacoes")
    
    if not valor_pago or valor_pago <= 0:
        return jsonify({"success": False, "error": "Valor pago deve ser maior que zero"}), 400
    
    try:
        # Parse date
        payment_date = datetime.strptime(data_pagamento, "%Y-%m-%d") if data_pagamento else datetime.utcnow()
        
        # Calculate discount if applicable
        desconto_valor = venda.valor_total - float(valor_pago) if float(valor_pago) < venda.valor_total else 0
        desconto_percentual = (desconto_valor / venda.valor_total) * 100 if venda.valor_total > 0 and desconto_valor > 0 else 0
        
        # Update sale
        venda.status = "Pago"
        venda.data_pagamento = payment_date
        venda.observacoes = observacoes
        venda.desconto_valor = desconto_valor
        venda.desconto_percentual = desconto_percentual
        
        db.session.commit()
        return jsonify({"success": True, "venda": venda.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": "Erro interno do servidor ao confirmar pagamento.", 
            "details": str(e)
        }), 500

@venda_bp.route("/fifo_info", methods=["GET"])
def get_fifo_info():
    # Get all products with quantity > 0
    produtos = Produto.query.filter(Produto.quantidade_atual > 0).all()
    
    # Group products by attributes (nome, tamanho, sexo, cor_estampa)
    grupos = {}
    for produto in produtos:
        key = (produto.nome, produto.tamanho, produto.sexo, produto.cor_estampa)
        if key not in grupos:
            grupos[key] = []
        grupos[key].append(produto)
    
    # Sort each group by data_compra (oldest first)
    for key in grupos:
        grupos[key].sort(key=lambda p: p.data_compra or datetime.max)
    
    # Create FIFO ranking for each product
    fifo_info = {}
    for key, produtos_grupo in grupos.items():
        for i, produto in enumerate(produtos_grupo):
            fifo_info[produto.id] = {
                "position": i + 1,
                "total_in_group": len(produtos_grupo),
                "group_key": key
            }
    
    return jsonify({"success": True, "fifo_info": fifo_info}), 200

@venda_bp.route("/exchange", methods=["POST"])
def create_exchange():
    # This endpoint is a proxy to the exchange route
    from src.routes.exchange_routes import create_troca
    return create_troca()
