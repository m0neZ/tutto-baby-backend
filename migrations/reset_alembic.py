"""Script to reset Alembic version table

This script will reset the Alembic version table to track only the consolidated migration.
Run this script before applying the new migration to ensure a clean migration chain.
"""
from sqlalchemy import create_engine, text
from flask import Flask
from src.config import Config

app = Flask(__name__)
app.config.from_object(Config)

def reset_alembic_version():
    # Create database connection
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    
    with engine.connect() as conn:
        # Check if alembic_version table exists
        result = conn.execute(text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
        ))
        table_exists = result.scalar()
        
        if table_exists:
            # Delete all existing version records
            conn.execute(text("DELETE FROM alembic_version"))
            
            # Insert our consolidated migration version
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('1a2b3c4d5e6f')"))
            conn.commit()
            
            print("Alembic version table reset successfully to track only the consolidated migration.")
        else:
            print("Alembic version table doesn't exist yet. No reset needed.")

if __name__ == "__main__":
    reset_alembic_version()
