# === models/product.py ===
from . import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import MONEY # Consider using appropriate type for currency

class Produto(db.Model):
    __tablename__ = 'produtos'

    id = db.Column(db.Integer, primary_key=True)
    # sku will be generated automatically later
    sku = db.Column(db.String(50), unique=True, nullable=True) # Made nullable temporarily
    nome = db.Column(db.String(150), nullable=False) # Increased length slightly
    sexo = db.Column(db.String(10), nullable=False) # Masculino / Feminino
    tamanho = db.Column(db.String(50), nullable=False) # Managed via FieldOption
    cor_estampa = db.Column(db.String(50), nullable=False) # Managed via FieldOption
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    # Using Float for now, consider Decimal or Integer cents for precision
    custo = db.Column(db.Float, nullable=False)
    preco_venda = db.Column(db.Float, nullable=False)
    quantidade_atual = db.Column(db.Integer, default=0)
    limite_reabastecimento = db.Column(db.Integer, default=5)
    data_compra = db.Column(db.Date) # Date of initial purchase/entry
    # Removed data_venda, will be handled by Sales model
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    fornecedor = db.relationship('Fornecedor', backref=db.backref('produtos', lazy=True))
    transacoes = db.relationship('TransacaoEstoque', backref='produto', lazy=True)
    # Relationship to SaleItem for tracking sales
    itens_venda = db.relationship('ItemVenda', backref='produto', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'nome': self.nome,
            'sexo': self.sexo,
            'tamanho': self.tamanho,
            'cor_estampa': self.cor_estampa,
            'fornecedor_id': self.fornecedor_id,
            'nome_fornecedor': self.fornecedor.nome if self.fornecedor else None,
            'custo': self.custo,
            'preco_venda': self.preco_venda,
            'quantidade_atual': self.quantidade_atual,
            'limite_reabastecimento': self.limite_reabastecimento,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'data_compra': self.data_compra.isoformat() if self.data_compra else None,
            # 'data_venda' removed
        }

