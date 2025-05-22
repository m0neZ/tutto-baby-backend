# === routes/product_routes.py ===
from flask import Blueprint, request, jsonify, current_app
from src.models import db, Produto, TransacaoEstoque, FieldOption
from src.models.supplier import Fornecedor
from datetime import datetime
import os
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

produto_bp = Blueprint("produto_bp", __name__)

@produto_bp.route("/", methods=["GET"])
def get_all_produtos():
    produtos = Produto.query.all()
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
    
    # Extract data with defaults
    nome = data.get("nome")
    tamanho = data.get("tamanho")
    sexo = data.get("sexo")
    cor_estampa = data.get("cor_estampa")
    fornecedor_id = data.get("fornecedor_id")
    custo = data.get("custo")
    preco_venda = data.get("preco_venda")
    quantidade = data.get("quantidade", 1)
    data_compra_str = data.get("data_compra")
    
    # Validate required fields
    if not all([nome, tamanho, sexo, cor_estampa, fornecedor_id, custo, preco_venda]):
        return jsonify({"success": False, "error": "Todos os campos são obrigatórios"}), 400
    
    # Parse date
    try:
        if data_compra_str:
            data_compra = datetime.strptime(data_compra_str, "%Y-%m-%d").date()
        else:
            data_compra = datetime.now().date()
    except ValueError:
        return jsonify({"success": False, "error": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    # Create products (one per quantity for single-unit paradigm)
    produtos_criados = []
    
    try:
        for i in range(int(quantidade)):
            novo_produto = Produto(
                nome=nome,
                tamanho=tamanho,
                sexo=sexo,
                cor_estampa=cor_estampa,
                fornecedor_id=fornecedor_id,
                custo=float(custo),
                preco_venda=float(preco_venda),
                quantidade_atual=1,  # Always 1 in single-unit paradigm
                data_compra=data_compra
            )
            db.session.add(novo_produto)
            
            # Create purchase transaction
            transacao = TransacaoEstoque(
                produto=novo_produto,
                tipo_transacao="compra",
                quantidade=1,
                data_transacao=data_compra,
                observacoes="Compra inicial",
                custo_unitario_transacao=float(custo)
            )
            db.session.add(transacao)
            
            produtos_criados.append(novo_produto)
        
        db.session.commit()
        return jsonify({
            "success": True, 
            "message": f"{len(produtos_criados)} produto(s) criado(s) com sucesso",
            "produtos": [p.to_dict() for p in produtos_criados]
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@produto_bp.route("/<int:produto_id>", methods=["PUT"])
def update_produto(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"success": False, "error": "Produto não encontrado"}), 404
    
    data = request.json
    
    # Update fields
    if "nome" in data:
        produto.nome = data["nome"]
    if "tamanho" in data:
        produto.tamanho = data["tamanho"]
    if "sexo" in data:
        produto.sexo = data["sexo"]
    if "cor_estampa" in data:
        produto.cor_estampa = data["cor_estampa"]
    if "fornecedor_id" in data:
        produto.fornecedor_id = data["fornecedor_id"]
    if "custo" in data:
        produto.custo = float(data["custo"])
    if "preco_venda" in data:
        produto.preco_venda = float(data["preco_venda"])
    if "data_compra" in data:
        try:
            produto.data_compra = datetime.strptime(data["data_compra"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"success": False, "error": "Formato de data inválido. Use YYYY-MM-DD"}), 400
    
    try:
        db.session.commit()
        return jsonify({"success": True, "produto": produto.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@produto_bp.route("/<int:produto_id>", methods=["DELETE"])
def delete_produto(produto_id):
    produto = Produto.query.get(produto_id)
    if not produto:
        return jsonify({"success": False, "error": "Produto não encontrado"}), 404
    
    # Check if product has quantity = 1 (can only delete products with quantity = 1)
    if produto.quantidade_atual != 1:
        return jsonify({"success": False, "error": "Só é possível excluir produtos com quantidade = 1."}), 400
    
    try:
        # Delete associated transactions
        TransacaoEstoque.query.filter_by(produto_id=produto_id).delete()
        
        # Delete the product
        db.session.delete(produto)
        db.session.commit()
        return jsonify({"success": True, "message": "Produto excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@produto_bp.route("/clear_all_test_data", methods=["POST"])
def clear_all_test_data():
    try:
        # Delete all transactions first (due to foreign key constraints)
        TransacaoEstoque.query.delete()
        
        # Delete all products
        num_deleted = db.session.query(Produto).delete()
        
        db.session.commit()
        return jsonify({
            "success": True, 
            "message": f"Todos os dados de teste foram excluídos com sucesso. {num_deleted} produtos removidos."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@produto_bp.route("/import", methods=["POST"])
def import_produtos():
    data = request.json
    if not data or "products" not in data or not isinstance(data["products"], list):
        return jsonify({"success": False, "error": "Dados de importação inválidos"}), 400
    
    products_data = data["products"]
    if len(products_data) == 0:
        return jsonify({"success": False, "error": "Nenhum produto para importar"}), 400
    
    # Track new options created
    new_options = {
        "tamanhos": [],
        "cores": [],
        "fornecedores": []
    }
    
    # Process products
    produtos_criados = []
    
    try:
        for product in products_data:
            # Extract data
            nome = product.get("nome")
            tamanho = product.get("tamanho")
            sexo = product.get("sexo")
            cor_estampa = product.get("cor_estampa")
            fornecedor_nome = product.get("fornecedor")
            custo_str = product.get("custo")
            preco_venda_str = product.get("preco_venda")
            quantidade_str = product.get("quantidade", "1")
            data_compra_str = product.get("data_compra")
            
            # Validate required fields
            if not all([nome, tamanho, sexo, cor_estampa, fornecedor_nome, custo_str, preco_venda_str]):
                continue  # Skip invalid products
            
            # Parse numeric values
            try:
                custo = float(custo_str)
                preco_venda = float(preco_venda_str)
                quantidade = int(quantidade_str) if quantidade_str else 1
            except (ValueError, TypeError):
                continue  # Skip if numeric conversion fails
            
            # Parse date
            try:
                if data_compra_str:
                    data_compra = datetime.strptime(data_compra_str, "%Y-%m-%d").date()
                else:
                    data_compra = datetime.now().date()
            except ValueError:
                data_compra = datetime.now().date()  # Default to today if format is wrong
            
            # Check if tamanho exists, create if not
            tamanho_option = FieldOption.query.filter_by(
                type="tamanho", 
                value=tamanho
            ).first()
            
            if not tamanho_option:
                tamanho_option = FieldOption(
                    type="tamanho",
                    value=tamanho,
                    is_active=True
                )
                db.session.add(tamanho_option)
                new_options["tamanhos"].append(tamanho)
            
            # Check if cor_estampa exists, create if not
            cor_option = FieldOption.query.filter_by(
                type="cor_estampa", 
                value=cor_estampa
            ).first()
            
            if not cor_option:
                cor_option = FieldOption(
                    type="cor_estampa",
                    value=cor_estampa,
                    is_active=True
                )
                db.session.add(cor_option)
                new_options["cores"].append(cor_estampa)
            
            # Check if fornecedor exists in the fornecedores table, create if not
            fornecedor = Fornecedor.query.filter_by(nome=fornecedor_nome).first()
            
            if not fornecedor:
                fornecedor = Fornecedor(
                    nome=fornecedor_nome,
                    is_active=True
                )
                db.session.add(fornecedor)
                db.session.flush()  # Get ID for the new fornecedor
                new_options["fornecedores"].append(fornecedor_nome)
            
            fornecedor_id = fornecedor.id
            
            # Create products (one per quantity for single-unit paradigm)
            for i in range(quantidade):
                novo_produto = Produto(
                    nome=nome,
                    tamanho=tamanho,
                    sexo=sexo,
                    cor_estampa=cor_estampa,
                    fornecedor_id=fornecedor_id,
                    custo=custo,
                    preco_venda=preco_venda,
                    quantidade_atual=1,  # Always 1 in single-unit paradigm
                    data_compra=data_compra
                )
                db.session.add(novo_produto)
                
                # Create purchase transaction
                transacao = TransacaoEstoque(
                    produto=novo_produto,
                    tipo_transacao="compra",
                    quantidade=1,
                    data_transacao=data_compra,
                    observacoes="Importação",
                    custo_unitario_transacao=custo
                )
                db.session.add(transacao)
                
                produtos_criados.append(novo_produto)
        
        db.session.commit()
        
        # Clean up new_options to only include non-empty lists
        for key in list(new_options.keys()):
            if not new_options[key]:
                del new_options[key]
        
        return jsonify({
            "success": True, 
            "message": f"{len(produtos_criados)} produto(s) importado(s) com sucesso",
            "imported": len(produtos_criados),
            "newOptions": new_options if any(new_options.values()) else None
        }), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"success": False, "error": f"Erro de banco de dados: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
