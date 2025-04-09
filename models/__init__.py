from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.product import Product
from models.supplier import Supplier
from models.transaction import InventoryTransaction
from .field_option import FieldOption
