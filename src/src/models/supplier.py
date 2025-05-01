# === models/supplier.py ===
from . import db
from datetime import datetime

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    # Field for managing activation status, linked to OptionManager
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    # contact_info removed as per instruction to manage suppliers via Admin page like other options
    # contact_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'is_active': self.is_active,
            # 'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 'product_count': len(self.produtos) # Avoid calculating this here for performance, query if needed
        }

