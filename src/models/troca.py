# === models/troca.py ===
from datetime import datetime
from src.models import db

class Troca(db.Model):
    __tablename__ = 'trocas'
    
    id = db.Column(db.Integer, primary_key=True)
    venda_original_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    cliente_nome = db.Column(db.String(100), nullable=False)
    cliente_sobrenome = db.Column(db.String(100), nullable=False)
    data_troca = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    valor_produtos_devolvidos = db.Column(db.Float, nullable=False, default=0)
    valor_produtos_novos = db.Column(db.Float, nullable=False, default=0)
    diferenca_valor = db.Column(db.Float, nullable=False, default=0)
    
    # Relationships
    venda_original = db.relationship('Venda', foreign_keys=[venda_original_id], backref='trocas_originadas')
    itens = db.relationship('ItemTroca', backref='troca', cascade='all, delete-orphan')
    vendas = db.relationship('Venda', backref='troca_origem', primaryjoin="Venda.troca_id==Troca.id")
    
    def to_dict(self):
        return {
            'id': self.id,
            'venda_original_id': self.venda_original_id,
            'cliente_nome': self.cliente_nome,
            'cliente_sobrenome': self.cliente_sobrenome,
            'data_troca': self.data_troca.isoformat() if self.data_troca else None,
            'valor_produtos_devolvidos': self.valor_produtos_devolvidos,
            'valor_produtos_novos': self.valor_produtos_novos,
            'diferenca_valor': self.diferenca_valor,
            'itens': [item.to_dict() for item in self.itens] if self.itens else []
        }

class ItemTroca(db.Model):
    __tablename__ = 'itens_troca'
    
    id = db.Column(db.Integer, primary_key=True)
    troca_id = db.Column(db.Integer, db.ForeignKey('trocas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'devolvido' or 'novo'
    valor = db.Column(db.Float, nullable=False)
    
    # Relationships
    produto = db.relationship('Produto')
    
    def to_dict(self):
        return {
            'id': self.id,
            'troca_id': self.troca_id,
            'produto_id': self.produto_id,
            'tipo': self.tipo,
            'valor': self.valor,
            'produto': self.produto.to_dict() if self.produto else None
        }
