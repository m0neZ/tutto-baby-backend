# === routes/field_routes.py ===
from flask import Blueprint, jsonify
from src.models import db, Produto
from sqlalchemy import distinct
import sys # Added for basic error printing

field_bp = Blueprint("field_bp", __name__)

# Map frontend names to backend/DB column names
FIELD_MAP = {
    "size": "tamanho",
    "color_print": "cor_estampa",
    "gender": "sexo" # Assuming frontend might use 'gender', map to 'sexo'
}
# Validate using frontend names
ALLOWED_FRONTEND_FIELDS = list(FIELD_MAP.keys())

@field_bp.route("/<frontend_field_name>", methods=["GET"])
def get_distinct_field_values(frontend_field_name):
    if frontend_field_name not in ALLOWED_FRONTEND_FIELDS:
        return jsonify({"success": False, "error": f"Campo inválido para obter valores distintos: {frontend_field_name}"}), 400

    # Get the corresponding backend field name
    backend_field_name = FIELD_MAP.get(frontend_field_name)
    if not backend_field_name:
         # Should not happen if ALLOWED_FRONTEND_FIELDS is derived from FIELD_MAP
         return jsonify({"success": False, "error": f"Mapeamento interno não encontrado para: {frontend_field_name}"}), 500

    try:
        # Get the column object from the Produto model using the backend name
        column = getattr(Produto, backend_field_name, None)
        if column is None:
            return jsonify({"success": False, "error": f"Coluna interna não encontrada no modelo: {backend_field_name}"}), 500

        # Refined query for distinct, non-null, non-empty values
        query = db.session.query(distinct(column)).filter(column.isnot(None), column != '').order_by(column)
        results = query.all()

        # Extract values from the result tuples
        values = [result[0] for result in results]

        return jsonify({"success": True, "field": frontend_field_name, "values": values}), 200

    except Exception as e:
        # Log the error for debugging (basic print to stderr)
        print(f"Error fetching distinct values for {frontend_field_name} ({backend_field_name}): {e}", file=sys.stderr)
        return jsonify({"success": False, "error": "Erro interno do servidor ao buscar valores distintos.", "details": str(e)}), 500

