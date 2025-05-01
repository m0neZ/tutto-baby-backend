# wsgi.py
# This file acts as the entry point for Gunicorn on Render.

# Ensure the src directory is in the Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the Flask app instance from src.main
from main import app

# Make the app instance available for Gunicorn
if __name__ == "__main__":
    # This part is optional, mainly for local testing if needed
    # Render will use the 'app' variable directly via Gunicorn
    pass

