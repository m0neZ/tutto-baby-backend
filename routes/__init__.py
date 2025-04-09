# === routes/__init__.py ===
from routes.product_routes import product_bp
from routes.supplier_routes import supplier_bp
from routes.transaction_routes import transaction_bp
from routes.summary_routes import summary_bp
from routes.alert_routes import alert_bp
from .field_routes import field_bp

def register_routes(app):
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(supplier_bp, url_prefix='/api/suppliers')
    app.register_blueprint(transaction_bp, url_prefix='/api/transactions')
    app.register_blueprint(summary_bp, url_prefix='/api')
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')
    app.register_blueprint(field_bp, url_prefix='/api/fields')
