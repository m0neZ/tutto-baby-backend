# === routes/exchange_routes.py ===
from flask import Blueprint, request, jsonify
from src.models import db, Venda, ItemVenda, Produto, TransacaoEstoque, Troca, ItemTroca
from datetime import datetime
from sqlalchemy import func

troca_bp = Blueprint("troca_bp", __name__)

@troca_bp.route("/", methods=["GET"])
def get_all_trocas():
    # Add filtering/pagination later if needed
    trocas = Troca.query.order_by(Troca.data_troca.desc()).all()
    return jsonify({"success": True, "trocas": [t.to_dict() for t in trocas]}), 200

@troca_bp.route("/<int:troca_id>", methods=["GET"])
def get_troca(troca_id):
    troca = Troca.query.get(troca_id)
    if not troca:
        return jsonify({"success": False, "error": "Troca não encontrada"}), 404
    return jsonify({"success": True, "troca": troca.to_dict()}), 200

@troca_bp.route("/", methods=["POST"])
def create_troca():
    data = request.json
    venda_original_id = data.get("venda_original_id")
    cliente_nome = data.get("cliente_nome")
    cliente_sobrenome = data.get("cliente_sobrenome")
    produtos_devolvidos = data.get("produtos_devolvidos", [])
    produtos_novos = data.get("produtos_novos", [])
    
    # Validate required fields
    if not venda_original_id:
        return jsonify({"success": False, "error": "ID da venda original é obrigatório"}), 400
    
    if not cliente_nome or not cliente_sobrenome:
        return jsonify({"success": False, "error": "Nome e sobrenome do cliente são obrigatórios"}), 400
    
    if not produtos_devolvidos or not isinstance(produtos_devolvidos, list) or len(produtos_devolvidos) == 0:
        return jsonify({"success": False, "error": "Pelo menos um produto deve ser devolvido"}), 400
    
    if not produtos_novos or not isinstance(produtos_novos, list) or len(produtos_novos) == 0:
        return jsonify({"success": False, "error": "Pelo menos um produto novo deve ser selecionado"}), 400
    
    # Check if original sale exists
    venda_original = Venda.query.get(venda_original_id)
    if not venda_original:
        return jsonify({"success": False, "error": f"Venda original com ID {venda_original_id} não encontrada"}), 404
    
    # Validate returned products
    for item in produtos_devolvidos:
        produto_id = item.get("produto_id")
        if not produto_id:
            return jsonify({"success": False, "error": "ID do produto devolvido é obrigatório"}), 400
        
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"success": False, "error": f"Produto com ID {produto_id} não encontrado"}), 404
        
        # Check if product belongs to the original sale
        item_venda = ItemVenda.query.filter_by(venda_id=venda_original_id, produto_id=produto_id).first()
        if not item_venda:
            return jsonify({"success": False, "error": f"Produto com ID {produto_id} não pertence à venda original"}), 400
    
    # Validate new products
    for item in produtos_novos:
        produto_id = item.get("produto_id")
        if not produto_id:
            return jsonify({"success": False, "error": "ID do produto novo é obrigatório"}), 400
        
        produto = Produto.query.get(produto_id)
        if not produto:
            return jsonify({"success": False, "error": f"Produto com ID {produto_id} não encontrado"}), 404
        
        # Check if product is available in stock
        if produto.quantidade_atual <= 0:
            return jsonify({"success": False, "error": f"Produto {produto.nome} não está disponível em estoque"}), 400
    
    try:
        # Create exchange record
        nova_troca = Troca(
            venda_original_id=venda_original_id,
            cliente_nome=cliente_nome,
            cliente_sobrenome=cliente_sobrenome,
            data_troca=datetime.utcnow(),
            valor_produtos_devolvidos=0,  # Will be calculated
            valor_produtos_novos=0,  # Will be calculated
            diferenca_valor=0  # Will be calculated
        )
        db.session.add(nova_troca)
        db.session.flush()  # Get ID for the new exchange
        
        # Process returned products
        valor_devolvidos = 0
        for item in produtos_devolvidos:
            produto_id = item.get("produto_id")
            produto = Produto.query.get(produto_id)
            
            # Add to exchange items
            item_troca = ItemTroca(
                troca_id=nova_troca.id,
                produto_id=produto_id,
                tipo="devolvido",
                valor=produto.preco_venda
            )
            db.session.add(item_troca)
            
            # Update inventory - return product to stock
            produto.quantidade_atual = 1  # Set to 1 since it's being returned
            
            # Create inventory transaction
            transacao = TransacaoEstoque(
                produto_id=produto_id,
                tipo_transacao="troca_devolucao",
                quantidade=1,  # Positive for return to stock
                data_transacao=datetime.utcnow(),
                observacoes=f"Troca ID: {nova_troca.id} - Devolução",
                troca_id=nova_troca.id
            )
            db.session.add(transacao)
            
            valor_devolvidos += produto.preco_venda
        
        # Process new products
        valor_novos = 0
        for item in produtos_novos:
            produto_id = item.get("produto_id")
            produto = Produto.query.get(produto_id)
            
            # Add to exchange items
            item_troca = ItemTroca(
                troca_id=nova_troca.id,
                produto_id=produto_id,
                tipo="novo",
                valor=produto.preco_venda
            )
            db.session.add(item_troca)
            
            # Update inventory - remove from stock
            produto.quantidade_atual = 0  # Set to 0 since it's being taken
            
            # Create inventory transaction
            transacao = TransacaoEstoque(
                produto_id=produto_id,
                tipo_transacao="troca_saida",
                quantidade=-1,  # Negative for removal from stock
                data_transacao=datetime.utcnow(),
                observacoes=f"Troca ID: {nova_troca.id} - Saída",
                troca_id=nova_troca.id
            )
            db.session.add(transacao)
            
            valor_novos += produto.preco_venda
        
        # Update exchange values
        nova_troca.valor_produtos_devolvidos = valor_devolvidos
        nova_troca.valor_produtos_novos = valor_novos
        nova_troca.diferenca_valor = valor_novos - valor_devolvidos
        
        # Create a new sale record for the exchange
        nova_venda = Venda(
            cliente_nome=cliente_nome,
            cliente_sobrenome=cliente_sobrenome,
            data_venda=datetime.utcnow(),
            valor_total=max(0, nova_troca.diferenca_valor),  # Only positive difference
            status="Troca" if nova_troca.diferenca_valor <= 0 else "Pagamento Pendente",
            observacoes=f"Troca ID: {nova_troca.id}",
            troca_id=nova_troca.id
        )
        db.session.add(nova_venda)
        db.session.flush()
        
        # Add items to the new sale
        for item in produtos_novos:
            produto_id = item.get("produto_id")
            produto = Produto.query.get(produto_id)
            
            item_venda = ItemVenda(
                venda_id=nova_venda.id,
                produto_id=produto_id,
                quantidade=1,  # Always 1 in single-unit paradigm
                preco_unitario=produto.preco_venda,
                custo_unitario=produto.custo
            )
            db.session.add(item_venda)
        
        db.session.commit()
        return jsonify({
            "success": True, 
            "troca": nova_troca.to_dict(),
            "venda": nova_venda.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "error": "Erro interno do servidor ao registrar troca.", 
            "details": str(e)
        }), 500

# Additional routes for exchange management can be added as needed

# Export the blueprint with the name expected in routes/__init__.py
exchange_bp = troca_bp
