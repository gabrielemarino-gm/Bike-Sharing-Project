from flask import Blueprint, jsonify
from database.data_analytics import BikeAnalytics
import logging

analytics_bp = Blueprint('analytics', __name__)
analytics_service = BikeAnalytics()

# curl -X GET http://localhost:5001/api/analytics/mean-rental-by-hour
@analytics_bp.route('/mean-rental-by-hour', methods=['GET']) 
def mean_rental_by_hour():
    """Raggruppa per ora e calcola la media dei noleggi"""
    try:
        data = analytics_service.get_hourly_rental_patterns()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Analisi pattern orari completata con successo'
        }), 200
        
    except Exception as e:
        logging.error(f"Errore nell'analisi oraria: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante l\'analisi oraria: {str(e)}'
        }), 500

# curl -X GET http://localhost:5001/api/analytics/weekday-vs-weekend
@analytics_bp.route('/weekday-vs-weekend', methods=['GET'])
def weekday_vs_weekend():
    """Confronta noleggi medi tra giorni lavorativi e weekend"""
    try:
        data = analytics_service.get_weekday_weekend_comparison()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Confronto weekday vs weekend completato con successo'
        }), 200
        
    except Exception as e:
        logging.error(f"Errore nel confronto weekday vs weekend: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante il confronto: {str(e)}'
        }), 500

# curl -X GET http://localhost:5001/api/analytics/weather-impact
@analytics_bp.route('/weather-impact', methods=['GET'])
def weather_impact():
    """Analizza l'impatto delle condizioni meteo sui noleggi"""
    try:
        data = analytics_service.get_weather_impact_analysis()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Analisi impatto meteo completata con successo'
        }), 200
        
    except Exception as e:
        logging.error(f"Errore nell'analisi meteo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante l\'analisi meteo: {str(e)}'
        }), 500