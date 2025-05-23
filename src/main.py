import os
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from src.config import Config
from src.models import db
from src.models.user import User
from src.routes import register_routes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    JWTManager(app)

    # Restrict CORS to your frontend domain
    CORS(app, origins=["https://www.tuttobaby.com.br"], supports_credentials=True)

    # Ensure database tables exist and seed initial admin user if none exists
    with app.app_context():
        # Ensure tables exist
        db.create_all()

        # Auto-seed initial admin user if none exists
        try:
            user_count = User.query.count()
        except Exception as e:
            app.logger.error(f"Error counting users: {e}")
            user_count = 0

        if user_count == 0:
            admin_email = os.getenv("ADMIN_EMAIL", "").strip()
            admin_pass  = os.getenv("ADMIN_PASS", "").strip()
            if admin_email and admin_pass:
                admin = User(email=admin_email, name="Administrator")
                admin.set_password(admin_pass)
                admin.role = "admin"
                db.session.add(admin)
                db.session.commit()
                app.logger.info(f"Auto-created admin user: {admin_email}")
            else:
                app.logger.warning(
                    "No ADMIN_EMAIL/ADMIN_PASS set or empty; skipping auto-seed of admin user."
                )

    # Register blueprints
    register_routes(app)

    # Health-check endpoint
    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    @app.route('/api/admin/reset-vendas-table', methods=['GET'])
@jwt_required()
def reset_vendas_table():
    try:
        # Drop the table
        db.session.execute(text("DROP TABLE IF EXISTS vendas CASCADE"))
        db.session.commit()
        
        # Force SQLAlchemy to recreate the table on next app startup
        return jsonify({"success": True, "message": "Vendas table dropped. It will be recreated on next app restart."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


    # HTTP exception handler
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"success": False, "error": e.description}), e.code

    # Catch-all for unexpected errors
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Server Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

    return app

# Entrypoint
app = create_app()
