# === models/product.py ===
from . import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    size = db.Column(db.String(20), nullable=False)
    color_print = db.Column(db.String(50), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    cost_price = db.Column(db.Float, nullable=False)
    retail_price = db.Column(db.Float, nullable=False)
    current_quantity = db.Column(db.Integer, default=0)
    reorder_threshold = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    purchase_date = db.Column(db.Date)
    sale_date = db.Column(db.Date)

    supplier = db.relationship('Supplier', backref=db.backref('products', lazy=True))
    transactions = db.relationship('InventoryTransaction', backref='product', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'name': self.name,
            'gender': self.gender,
            'size': self.size,
            'color_print': self.color_print,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'cost_price': self.cost_price,
            'retail_price': self.retail_price,
            'current_quantity': self.current_quantity,
            'reorder_threshold': self.reorder_threshold,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
        }
