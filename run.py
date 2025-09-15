"""
Entry point per l'applicazione Flask
"""
from flask import Flask, jsonify
from database import init_database, create_tables
import logging

# Import blueprints
from routes.data_routes import data_bp
from routes.analytics_routes import analytics_bp
from routes.prediction_routes import prediction_bp

def create_app():
    """Factory function per creare l'app Flask"""
    app = Flask(__name__)
    
    # Configurazione base
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bike_sharing.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dev-secret-key'
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # 🔧 INIZIALIZZA DATABASE ALL'AVVIO
    try:
        print("🔧 Inizializzazione database...")
        db = init_database(app)
        
        # Crea tabelle nel contesto dell'app
        with app.app_context():
            create_tables()
            print("✅ Database e tabelle inizializzati con successo!")
            
    except Exception as e:
        print(f"❌ Errore inizializzazione database: {e}")
        logging.error(f"Database initialization failed: {e}")
        raise
    
    # Registra blueprints
    try:
        app.register_blueprint(data_bp, url_prefix='/api/data')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        app.register_blueprint(prediction_bp, url_prefix='/api/prediction')
        print("✅ Blueprints registrati con successo!")
        
    except Exception as e:
        print(f"❌ Errore registrazione blueprints: {e}")
        logging.error(f"Blueprint registration failed: {e}")
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        """Health check con stato database"""
        try:
            from database import BikeRecord, db
            record_count = db.session.query(BikeRecord).count()
            db_status = 'Connected'
        except Exception as e:
            record_count = 0
            db_status = f'Error: {str(e)}'
        
        return jsonify({
            'status': 'OK',
            'message': 'Bike Sharing API is running!',
            'database': {
                'status': db_status,
                'total_records': record_count
            },
            'endpoints': {
                'data': '/api/data/',
                'analytics': '/api/analytics/',
                'prediction': '/api/prediction/'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logging.error(f"Internal server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    # Crea l'app con database inizializzato
    app = create_app()
    
    print("🚀 Avvio server Flask su porta 5001...")
    print("📊 Database inizializzato e pronto per l'uso")
    print("🔗 Health check: http://localhost:5001/")
    
    # Avvia il server
    app.run(debug=True, host='0.0.0.0', port=5001)