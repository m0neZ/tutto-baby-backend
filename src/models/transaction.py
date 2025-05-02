# === models/transaction.py ===
from . import db
from datetime import datetime

class TransacaoEstoque(db.Model):
    __tablename__ = 'transacoes_estoque'

    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    # Renamed transaction_type to tipo_transacao
    # Values: 'compra', 'venda', 'devolucao', 'ajuste'
    tipo_transacao = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    # Renamed transaction_date to data_transacao
    data_transacao = db.Column(db.DateTime, default=datetime.utcnow)
    # Renamed notes to observacoes
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Added cost_at_transaction for COGS calculation
    custo_unitario_transacao = db.Column(db.Float) # Store the product cost at the time of transaction
    # Added sale_id to link sales transactions to the Sale model
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'produto_id': self.produto_id,
            'nome_produto': self.produto.nome if self.produto else None,
            'tipo_transacao': self.tipo_transacao,
            'quantidade': self.quantidade,
            'data_transacao': self.data_transacao.isoformat() if self.data_transacao else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'custo_unitario_transacao': self.custo_unitario_transacao,
            'venda_id': self.venda_id
        }

