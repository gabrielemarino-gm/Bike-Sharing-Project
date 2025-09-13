from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'OK',
            'message': 'Bike Sharing API is running!',
            'database': app.config['SQLALCHEMY_DATABASE_URI'].split('://')[0],
            'endpoints': {
                'data': '/api/data/',
                'analytics': '/api/analytics/',
                'prediction': '/api/prediction/'
            }
        })
    
    # Register blueprints
    from app.routes.data_routes import data_bp
    from app.routes.analytics_routes import analytics_bp
    from app.routes.prediction_routes import prediction_bp
    
    app.register_blueprint(data_bp, url_prefix='/api/data')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(prediction_bp, url_prefix='/api/prediction')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
