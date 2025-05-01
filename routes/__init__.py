# === routes/__init__.py ===
# Import renamed and new blueprints
from .product_routes import produto_bp
from .supplier_routes import fornecedor_bp
from .transaction_routes import transacao_bp
from .sale_routes import venda_bp
from .client_routes import cliente_bp
from .opcao_campo_routes import opcao_campo_bp
from .field_routes import field_bp # Added missing import for field_routes
from .report_routes import report_bp # Import the new report blueprint
from .alert_routes import alerta_bp # Import the renamed alert blueprint

def register_routes(app):
    # Register with Portuguese prefixes where appropriate
    # Corrected missing quotes around url_prefix
    app.register_blueprint(produto_bp, url_prefix="/api/produtos")
    app.register_blueprint(fornecedor_bp, url_prefix="/api/fornecedores")
    app.register_blueprint(transacao_bp, url_prefix="/api/transacoes")
    app.register_blueprint(venda_bp, url_prefix="/api/vendas")
    app.register_blueprint(cliente_bp, url_prefix="/api/clientes")
    app.register_blueprint(opcao_campo_bp, url_prefix="/api/opcoes_campo") # Route for managing field options like size, color
    app.register_blueprint(field_bp, url_prefix="/api/fields") # Added missing registration for field_routes
    app.register_blueprint(report_bp, url_prefix="/api") # Register report routes (contains summaries)
    app.register_blueprint(alerta_bp, url_prefix="/api/alertas") # Changed prefix to Portuguese

    # Note: Removed summary_bp as its functionality is in report_bp
    # Ensure app.py calls this register_routes function correctly.

