from flask import Blueprint, request, jsonify, send_file
from app.services.analytics_service import AnalyticsService
import logging
import io

analytics_bp = Blueprint('analytics', __name__)
analytics_service = AnalyticsService()

@analytics_bp.route('/hourly', methods=['GET'])
def get_hourly_stats():
    """Statistiche aggregate per ora"""
    try:
        stats = analytics_service.get_hourly_aggregations()
        return jsonify(stats), 200
    except Exception as e:
        logging.error(f"Errore nel calcolo delle statistiche orarie: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/daily', methods=['GET'])
def get_daily_stats():
    """Statistiche aggregate per giorno"""
    try:
        stats = analytics_service.get_daily_aggregations()
        return jsonify(stats), 200
    except Exception as e:
        logging.error(f"Errore nel calcolo delle statistiche giornaliere: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/seasonal', methods=['GET'])
def get_seasonal_stats():
    """Statistiche aggregate per stagione"""
    try:
        stats = analytics_service.get_seasonal_aggregations()
        return jsonify(stats), 200
    except Exception as e:
        logging.error(f"Errore nel calcolo delle statistiche stagionali: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/weather', methods=['GET'])
def get_weather_stats():
    """Statistiche aggregate per condizioni meteo"""
    try:
        stats = analytics_service.get_weather_aggregations()
        return jsonify(stats), 200
    except Exception as e:
        logging.error(f"Errore nel calcolo delle statistiche meteo: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/csv', methods=['GET'])
def export_analytics_csv():
    """Esporta le analisi in formato CSV"""
    try:
        csv_data = analytics_service.export_to_csv()
        
        output = io.BytesIO()
        output.write(csv_data.encode('utf-8'))
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name='bike_sharing_analytics.csv'
        )
    except Exception as e:
        logging.error(f"Errore nell'esportazione CSV: {str(e)}")
        return jsonify({'error': str(e)}), 500
