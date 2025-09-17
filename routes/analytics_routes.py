from flask import Blueprint, jsonify, Response
from database.data_analytics import BikeAnalytics
import logging
import csv
import io
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__)
analytics_service = BikeAnalytics()

def create_csv_response(data, filename, headers):
    """Crea una risposta CSV per il download"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Scrivi gli headers
    writer.writerow(headers)
    
    # Scrivi i dati
    if isinstance(data, list):
        for row in data:
            if isinstance(row, dict):
                writer.writerow([row.get(header, '') for header in headers])
            else:
                writer.writerow(row)
    elif isinstance(data, dict):
        # Se è un dizionario, converti in lista di righe
        for key, value in data.items():
            writer.writerow([key, value])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )

# curl -X GET http://localhost:5001/api/analytics/mean-rental-by-hour
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

# curl -X GET http://localhost:5001/api/analytics/weekday-vs-weekend
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

# curl -X GET http://localhost:5001/api/analytics/weather-impact
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


# curl -X GET http://localhost:5001/api/analytics/mean-rental-by-hour/download
@analytics_bp.route('/mean-rental-by-hour/download', methods=['GET'])
def download_hourly_patterns_csv():
    """Download analisi pattern orari in formato CSV convenzionale"""
    try:
        data = analytics_service.get_hourly_rental_patterns()
        
        if not data:
            return jsonify({'success': False, 'error': 'Nessun dato trovato'}), 404
        
        # Estrai la lista dei pattern orari
        hourly_patterns = data.get('hourly_patterns', [])
        
        if not hourly_patterns:
            return jsonify({'success': False, 'error': 'Nessun pattern orario trovato'}), 404
        
        csv_rows = []
        
        # Converti ogni pattern orario in una riga CSV
        for pattern in hourly_patterns:
            hour = pattern.get('hour', 0)
            avg_rentals = round(float(pattern.get('avg_rentals', 0)), 2)
            max_rentals = int(pattern.get('max_rentals', 0))
            min_rentals = int(pattern.get('min_rentals', 0))
            sample_count = int(pattern.get('sample_count', 0))
            total_rentals = int(pattern.get('total_rentals', 0))
            
            csv_rows.append([hour, avg_rentals, max_rentals, min_rentals, sample_count, total_rentals])
        
        headers = ['hour', 'avg_rentals', 'max_rentals', 'min_rentals', 'sample_count', 'total_rentals']
        filename = f'hourly_patterns_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(csv_rows, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore download CSV pattern orari: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
       
        
# curl -X GET http://localhost:5001/api/analytics/weekday-vs-weekend/download
@analytics_bp.route('/weekday-vs-weekend/download', methods=['GET'])
def download_weekday_weekend_csv():
    """Download weekday vs weekend in CSV"""
    try:
        data = analytics_service.get_weekday_weekend_comparison()
        
        if not data:
            return jsonify({'success': False, 'error': 'Nessun dato trovato'}), 404
        
        # Estrai la sezione comparison
        comparison_data = data.get('comparison', {})
        
        if not comparison_data:
            return jsonify({'success': False, 'error': 'Nessun dato comparison trovato'}), 404
        
        csv_rows = []
        
        # Converti ogni tipo di settimana in una riga CSV
        for week_type, stats in comparison_data.items():
            avg_rentals = round(float(stats.get('avg_rentals', 0)), 2)
            max_rentals = int(stats.get('max_rentals', 0))
            min_rentals = int(stats.get('min_rentals', 0))
            sample_count = int(stats.get('sample_count', 0))
            total_rentals = int(stats.get('total_rentals', 0))
            
            csv_rows.append([week_type, avg_rentals, max_rentals, min_rentals, sample_count, total_rentals])
        
        headers = ['Week-type', 'avg_rentals', 'max_rentals', 'min_rentals', 'sample_count', 'total_rentals']
        filename = f'weekday_weekend_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(csv_rows, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore download CSV weekday: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

        
# curl -X GET http://localhost:5001/api/analytics/weather-impact/download
@analytics_bp.route('/weather-impact/download', methods=['GET'])
def download_weather_impact_csv():
    """Download impatto meteo in CSV"""
    try:
        data = analytics_service.get_weather_impact_analysis()
        
        if not data:
            return jsonify({'success': False, 'error': 'Nessun dato trovato'}), 404
        
        # Log per debug
        logging.info(f"Dati weather impact ricevuti: {data}")
        
        csv_rows = []
        
        # Estrai la lista delle condizioni meteo
        weather_conditions = data.get('weather_conditions', [])
        
        if isinstance(weather_conditions, list):
            for condition in weather_conditions:
                if isinstance(condition, dict):
                    weather_code = condition.get('weather_code', 'N/A')
                    weather_description = condition.get('weather_name', f'Condizione {weather_code}')
                    avg_rentals = round(float(condition.get('avg_rentals', 0)), 2)
                    total_records = int(condition.get('sample_count', 0))
                    min_rentals = int(condition.get('min_rentals', 0))
                    max_rentals = int(condition.get('max_rentals', 0))
                    
                    csv_rows.append([
                        weather_code, 
                        weather_description, 
                        avg_rentals, 
                        total_records, 
                        min_rentals, 
                        max_rentals
                    ])
        
        if not csv_rows:
            return jsonify({'success': False, 'error': 'Nessun dato valido trovato'}), 404
        
        headers = ['weather_code', 'weather_description', 'average_rentals', 'total_records', 'min_rentals', 'max_rentals']
        filename = f'weather_impact_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(csv_rows, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore download CSV meteo: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
