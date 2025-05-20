from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from src.config import Config
from src.models import db
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

    # Register blueprints
    register_routes(app)

    # Health-check
    @app.route("/health")
    def health_check():
        return jsonify({"status": "ok"}), 200

    # Handle HTTP errors cleanly
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({"success": False, "error": e.description}), e.code

    # Catch-all for other exceptions
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Server Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

    return app

# Entry point for deployment (e.g. gunicorn)
app = create_app()
