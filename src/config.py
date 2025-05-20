import os
from datetime import timedelta

class Config:
    # Required environment variables
    if 'DATABASE_URL' not in os.environ:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    if 'SECRET_KEY' not in os.environ:
        raise RuntimeError("SECRET_KEY environment variable is not set")
    if 'JWT_SECRET' not in os.environ:
        raise RuntimeError("JWT_SECRET environment variable is not set")

    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask session signing
    SECRET_KEY = os.environ['SECRET_KEY']

    # JWT configuration
    JWT_SECRET_KEY = os.environ['JWT_SECRET']
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', '900')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', '604800')))

    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'false').lower() == 'true'
