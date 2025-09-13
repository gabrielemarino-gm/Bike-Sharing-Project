import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration - percorso semplificato
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Default to SQLite nella directory corrente
        SQLALCHEMY_DATABASE_URI = 'sqlite:///bike_sharing.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Percorsi semplificati
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'ml_models'
    DATA_PATH = os.environ.get('DATA_PATH') or 'data'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
