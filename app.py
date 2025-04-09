from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db
from config import Config
from routes import register_routes
from routes.field_routes import field_bp

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

db.init_app(app)

# ✅ CORS only from your Vercel frontend
CORS(app, supports_credentials=True, origins=["https://tutto-baby-frontend.vercel.app"])

# ✅ Blueprint explicitly registered with /api/fields prefix
app.register_blueprint(field_bp, url_prefix='/api/fields')

register_routes(app)

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500
