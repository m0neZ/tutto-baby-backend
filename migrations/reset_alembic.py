"""Script to reset Alembic version table

This script will reset the Alembic version table to track only the consolidated migration.
Run this script before applying the new migration to ensure a clean migration chain.
"""
import os
import sys
import traceback
from sqlalchemy import create_engine, text
from flask import Flask

# Add more detailed error handling and logging
try:
    # Print environment for debugging
    print("Starting reset_alembic.py script")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Import the Config class
    try:
        from src.config import Config
        print("Successfully imported Config")
    except ImportError as e:
        print(f"Error importing Config: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Print database URL (with password masked)
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not found')
    if db_url != 'Not found':
        # Mask password for security if present
        masked_url = db_url
        if '@' in db_url and ':' in db_url:
            parts = db_url.split('@')
            credentials = parts[0].split(':')
            if len(credentials) > 2:
                masked_url = f"{credentials[0]}:****@{parts[1]}"
        print(f"Database URL: {masked_url}")
    else:
        print("WARNING: SQLALCHEMY_DATABASE_URI not found in config")
    
    def reset_alembic_version():
        try:
            # Create database connection
            print("Creating database engine...")
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            
            print("Connecting to database...")
            with engine.connect() as conn:
                # Check if alembic_version table exists
                print("Checking if alembic_version table exists...")
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version')"
                ))
                table_exists = result.scalar()
                
                if table_exists:
                    print("alembic_version table exists, resetting...")
                    # Delete all existing version records
                    conn.execute(text("DELETE FROM alembic_version"))
                    
                    # Insert our consolidated migration version
                    conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('1a2b3c4d5e6f')"))
                    conn.commit()
                    
                    print("Alembic version table reset successfully to track only the consolidated migration.")
                else:
                    print("Alembic version table doesn't exist yet. No reset needed.")
                    
                # Verify the current version
                try:
                    result = conn.execute(text("SELECT version_num FROM alembic_version"))
                    versions = [row[0] for row in result]
                    print(f"Current alembic versions after reset: {versions}")
                except Exception as e:
                    print(f"Error verifying alembic version: {e}")
        
        except Exception as e:
            print(f"Error in reset_alembic_version: {e}")
            traceback.print_exc()
            sys.exit(1)

    if __name__ == "__main__":
        reset_alembic_version()
        print("Script completed successfully")

except Exception as e:
    print(f"Unhandled exception in reset_alembic.py: {e}")
    traceback.print_exc()
    sys.exit(1)
