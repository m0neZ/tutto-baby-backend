import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__))) # Required for deployment

from flask import Flask, jsonify, request # Removed send_from_directory
from flask_cors import CORS
from src.models import db # Updated import path
from src.config import Config # Updated import path
from src.routes import register_routes # Updated import path

# Initialize Flask app
# Removed static_folder and static_url_path as frontend is deployed separately
app = Flask(__name__)
app.config.from_object(Config)

# Configure Database URI using Render's DATABASE_URL environment variable
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    # Render provides postgres://, SQLAlchemy needs postgresql://
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Fallback to a local SQLite database if DATABASE_URL is not set (for local development)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url or f"sqlite:///{os.path.join(os.path.dirname(app.instance_path), 'inventory.db')}"

# Initialize Database
db.init_app(app)

# Configure CORS
# Placeholder origin, will be updated after frontend deployment
CORS(app, supports_credentials=True, origins=[
    "*" # Temporarily allow all origins, will restrict later
])

# Register all blueprints using the function from routes/__init__.py
register_routes(app)

# Create database tables if they don't exist
# In a production setup, migrations (e.g., using Flask-Migrate) are preferred
with app.app_context():
    db.create_all()

# Removed serve_frontend route as frontend is deployed separately

# Error Handlers
@app.errorhandler(404)
def not_found(e):
    # API requests get JSON 404
    return jsonify({"success": False, "error": "Recurso não encontrado"}), 404

@app.errorhandler(500)
def server_error(e):
    # Log the error details for debugging
    app.logger.error(f"Server Error: {e}", exc_info=True)
    return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

# Optional: Add a simple health check endpoint
@app.route("/health")
def health_check():
    return jsonify({"status": "ok"}), 200

# Running the app section remains commented out for production deployment
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

