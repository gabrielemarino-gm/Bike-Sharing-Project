from flask import Blueprint, request, jsonify
from app.services.data_service import DataService
import logging

data_bp = Blueprint('data', __name__)
data_service = DataService()

@data_bp.route('/load', methods=['POST'])
def load_dataset():
    """Carica il dataset nel database"""
    try:
        # Controlla se è stato fornito un file o un URL
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'Nessun file selezionato'}), 400
            
            result = data_service.load_from_file(file)
        elif 'url' in request.json:
            url = request.json['url']
            result = data_service.load_from_url(url)
        else:
            # Carica il dataset di default UCI Bike Sharing
            result = data_service.load_default_dataset()
        
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Errore nel caricamento del dataset: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/status', methods=['GET'])
def get_data_status():
    """Restituisce informazioni sui dati caricati"""
    try:
        status = data_service.get_dataset_status()
        return jsonify(status), 200
    except Exception as e:
        logging.error(f"Errore nel recupero dello status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_bp.route('/sample', methods=['GET'])
def get_sample_data():
    """Restituisce un campione dei dati"""
    try:
        limit = request.args.get('limit', 10, type=int)
        sample = data_service.get_sample_data(limit)
        return jsonify(sample), 200
    except Exception as e:
        logging.error(f"Errore nel recupero del campione: {str(e)}")
        return jsonify({'error': str(e)}), 500
