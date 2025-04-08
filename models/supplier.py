# === models/supplier.py ===
from . import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    contact_info = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'product_count': len(self.products)
        }