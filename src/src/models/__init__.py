# === models/__init__.py ===
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models here to ensure they are registered with SQLAlchemy
from .product import Produto
from .supplier import Fornecedor
from .transaction import TransacaoEstoque
from .field_option import FieldOption
from .client import Cliente
from .sale import Venda, ItemVenda

