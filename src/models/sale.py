# === models/sale.py ===
from . import db
from datetime import datetime

class Venda(db.Model):
    __tablename__ = 'vendas'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True) # Sale might not always have a registered client
    data_venda = db.Column(db.DateTime, default=datetime.utcnow)
    valor_total = db.Column(db.Float, nullable=False, default=0.0)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to SaleItem
    itens = db.relationship('ItemVenda', backref='venda', lazy=True, cascade="all, delete-orphan")
    # Relationship back to InventoryTransaction
    transacoes_estoque = db.relationship('TransacaoEstoque', backref='venda', lazy=True)

    def calculate_total(self):
        self.valor_total = sum(item.preco_unitario * item.quantidade for item in self.itens)

    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'nome_cliente': self.cliente.nome if self.cliente else 'N/A',
            'data_venda': self.data_venda.isoformat() if self.data_venda else None,
            'valor_total': self.valor_total,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'itens': [item.to_dict() for item in self.itens]
        }

class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    # Store price and cost at the time of sale for historical accuracy
    preco_unitario = db.Column(db.Float, nullable=False)
    custo_unitario = db.Column(db.Float, nullable=False) # Cost of the product when sold
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'venda_id': self.venda_id,
            'produto_id': self.produto_id,
            'nome_produto': self.produto.nome if self.produto else None,
            'quantidade': self.quantidade,
            'preco_unitario': self.preco_unitario,
            'custo_unitario': self.custo_unitario,
            'subtotal': self.preco_unitario * self.quantidade,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

