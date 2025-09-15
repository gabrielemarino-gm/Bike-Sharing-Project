"""
Database package initialization
"""
from flask_sqlalchemy import SQLAlchemy
import logging

# Initialize SQLAlchemy instance
db = SQLAlchemy()

def init_database(app):
    """Initialize database with Flask app"""
    try:
        db.init_app(app)
        logging.info("Database initialized successfully")
        return db
    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise

def create_tables():
    """Create all database tables"""
    try:
        db.create_all()
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        raise

# Import models after db initialization to avoid circular imports
from .bike_record import BikeRecord

# Export what's needed
__all__ = ['db', 'init_database', 'create_tables', 'BikeRecord', 'BikeDataLoader']