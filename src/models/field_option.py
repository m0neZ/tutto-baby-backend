from . import db
from datetime import datetime

class FieldOption(db.Model):
    __tablename__ = 'field_options'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # size, color_print, supplier
    value = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'value': self.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
