# === models/sale.py ===
from datetime import datetime
from src.models import db

class Venda(db.Model):
    __tablename__ = 'vendas'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_sobrenome = db.Column(db.String(100), nullable=True)
    data_venda = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_pagamento = db.Column(db.DateTime, nullable=True)
    valor_total = db.Column(db.Float, nullable=False, default=0)
    forma_pagamento = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='Pagamento Pendente', nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    desconto_percentual = db.Column(db.Float, nullable=True)
    desconto_valor = db.Column(db.Float, nullable=True)
    troca_id = db.Column(db.Integer, db.ForeignKey('trocas.id'), nullable=True)
    
    # Relationships
    itens = db.relationship('ItemVenda', backref='venda', cascade='all, delete-orphan')
    transacoes = db.relationship('TransacaoEstoque', backref='venda')
    # Note: 'cliente' backref is defined in the Cliente model
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'cliente_nome': self.cliente_nome,
            'cliente_sobrenome': self.cliente_sobrenome,
            'data_venda': self.data_venda.isoformat() if self.data_venda else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'valor_total': self.valor_total,
            'forma_pagamento': self.forma_pagamento,
            'status': self.status,
            'observacoes': self.observacoes,
            'desconto_percentual': self.desconto_percentual,
            'desconto_valor': self.desconto_valor,
            'troca_id': self.troca_id,
            'produtos': [item.to_dict() for item in self.itens] if self.itens else []
        }

class ItemVenda(db.Model):
    __tablename__ = 'itens_venda'
    
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=1)
    preco_unitario = db.Column(db.Float, nullable=False)
    custo_unitario = db.Column(db.Float, nullable=False)
    
    # Removed explicit relationship to resolve conflict with backref
    # produto = db.relationship('Produto')  # This line was causing the conflict
    
    def to_dict(self):
        return {
            'id': self.id,
            'venda_id': self.venda_id,
            'produto_id': self.produto_id,
            'quantidade': self.quantidade,
            'preco_venda': self.preco_unitario,
            'custo': self.custo_unitario,
            'nome': self.produto.nome if self.produto else None,
            'tamanho': self.produto.tamanho if self.produto else None,
            'cor_estampa': self.produto.cor_estampa if self.produto else None
        }
