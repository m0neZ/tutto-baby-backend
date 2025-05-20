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
    CORS(app, origins=["https://tutto-baby-frontend.vercel.app"], supports_credentials=True)

    # Auto-seed initial admin user if none exists
    with app.app_context():
        if User.query.count() == 0:
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_pass = os.getenv("ADMIN_PASS")
            if admin_email and admin_pass:
                admin = User(email=admin_email, name="Administrator")
                admin.set_password(admin_pass)
                admin.role = "admin"
                db.session.add(admin)
                db.session.commit()
                app.logger.info(f"Auto-created admin user: {admin_email}")
            else:
                app.logger.warning(
                    "No ADMIN_EMAIL/ADMIN_PASS set; skipping auto-seed of admin user."
                )

    # Register blueprints
    register_routes(app)

    # Health-check endpoint
    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

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

# Entrypoint for Gunicorn
app = create_app()
