from flask_jwt_extended import jwt_required
from .auth_routes import auth_bp
from .product_routes import produto_bp
from .supplier_routes import fornecedor_bp
from .transaction_routes import transacao_bp
from .sale_routes import venda_bp
from .client_routes import cliente_bp
from .opcao_campo_routes import opcao_campo_bp
from .field_routes import field_bp
from .report_routes import report_bp
from .alert_routes import alerta_bp

def register_routes(app):
    # Public auth endpoints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Secure all other blueprints under JWT protection
    @produto_bp.before_request
    @jwt_required()
    def secure_produtos(): pass
    app.register_blueprint(produto_bp, url_prefix="/api/produtos")

    @fornecedor_bp.before_request
    @jwt_required()
    def secure_fornecedores(): pass
    app.register_blueprint(fornecedor_bp, url_prefix="/api/fornecedores")

    @transacao_bp.before_request
    @jwt_required()
    def secure_transacoes(): pass
    app.register_blueprint(transacao_bp, url_prefix="/api/transacoes")

    @venda_bp.before_request
    @jwt_required()
    def secure_vendas(): pass
    app.register_blueprint(venda_bp, url_prefix="/api/vendas")

    @cliente_bp.before_request
    @jwt_required()
    def secure_clientes(): pass
    app.register_blueprint(cliente_bp, url_prefix="/api/clientes")

    @opcao_campo_bp.before_request
    @jwt_required()
    def secure_opcoes_campo(): pass
    app.register_blueprint(opcao_campo_bp, url_prefix="/api/opcoes_campo")

    @field_bp.before_request
    @jwt_required()
    def secure_fields(): pass
    app.register_blueprint(field_bp, url_prefix="/api/fields")

    @report_bp.before_request
    @jwt_required()
    def secure_reports(): pass
    app.register_blueprint(report_bp, url_prefix="/api")

    @alerta_bp.before_request
    @jwt_required()
    def secure_alertas(): pass
    app.register_blueprint(alerta_bp, url_prefix="/api/alertas")
