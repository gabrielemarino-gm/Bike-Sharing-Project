"""
Routes per accesso ai dati - Struttura semplificata
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, date
import sys
import os

# Aggiungi path per import database
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from database import BikeRecord, db
from database.data_loader import BikeDataLoader
import logging

# Blueprint per routes dei dati
data_bp = Blueprint('data', __name__)

@data_bp.route('/status', methods=['GET']) # curl http://localhost:5001/api/data/status
def status():
    """Endpoint di stato semplice"""
    return jsonify({
        'status': 'OK',
        'message': 'API dati operativa',
    }), 200

@data_bp.route('/load', methods=['POST']) # curl -F "file=@data/bike_sharing_sample.csv" -F "batch_size=500" http://localhost:5001/api/data/load
def load_dataset():
    """
    Carica un dataset CSV nel database
    
    Expects:
        - file: File CSV con il dataset bike sharing
        - batch_size (optional): Dimensione batch per caricamento
    
    Returns:
        JSON con risultato del caricamento
    """
    try:
        # Verifica presenza file
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nessun file fornito. Usa il campo "file" per l\'upload.'
            }), 400
        
        # Ottieni file dall'upload
        file = request.files['file']
        
        # Verifica nome file
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nome file vuoto. Seleziona un file CSV valido.'
            }), 400
        
        # Verifica estensione CSV
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Formato file non supportato. Usa file CSV.'
            }), 400
        
        # Parametri opzionali
        batch_size = request.form.get('batch_size', 1000, type=int)
        
        try:
            # Inizializza loader
            loader = BikeDataLoader()
            
            # Carica dati direttamente dal file object
            loader.load_from_file_object(file, batch_size=batch_size)
            
            # Ottieni statistiche finali
            stats = loader.get_stats()
            
            return jsonify({
                'success': True,
                'message': 'Dataset caricato con successo!',
                'data': {
                    'filename': file.filename,
                    'total_records': loader.total_records,
                    'success_count': loader.success_count,
                    'error_count': loader.error_count,
                    'success_rate': round((loader.success_count / loader.total_records * 100), 2) if loader.total_records > 0 else 0,
                    'batch_size': batch_size,
                    'database_stats': stats
                }
            }), 200
            
        except Exception as e:
            logging.error(f"Errore nel caricamento dati: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Errore durante il caricamento: {str(e)}'
            }), 500
                
    except Exception as e:
        logging.error(f"Errore generale endpoint load: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore del server: {str(e)}'
        }), 500