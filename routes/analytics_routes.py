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

# NUOVI ENDPOINTS PER DOWNLOAD CSV

# curl -X GET http://localhost:5001/api/analytics/mean-rental-by-hour/download
@analytics_bp.route('/mean-rental-by-hour/download', methods=['GET'])
def download_hourly_patterns_csv():
    """Download analisi pattern orari in formato CSV"""
    try:
        data = analytics_service.get_hourly_rental_patterns()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        # Prepara i dati per CSV
        csv_data = []
        if isinstance(data, dict):
            for hour, avg_rentals in data.items():
                csv_data.append({
                    'hour': hour,
                    'average_rentals': avg_rentals
                })
        else:
            csv_data = data
        
        headers = ['hour', 'average_rentals']
        filename = f'hourly_patterns_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(csv_data, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV pattern orari: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante il download: {str(e)}'
        }), 500

# curl -X GET http://localhost:5001/api/analytics/weekday-vs-weekend/download
@analytics_bp.route('/weekday-vs-weekend/download', methods=['GET'])
def download_weekday_weekend_csv():
    """Download confronto weekday vs weekend in formato CSV"""
    try:
        data = analytics_service.get_weekday_weekend_comparison()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        # Prepara i dati per CSV
        csv_data = []
        if isinstance(data, dict):
            for day_type, stats in data.items():
                if isinstance(stats, dict):
                    row = {'day_type': day_type}
                    row.update(stats)
                    csv_data.append(row)
                else:
                    csv_data.append({
                        'day_type': day_type,
                        'value': stats
                    })
        else:
            csv_data = data
        
        # Determina headers dinamicamente
        if csv_data:
            headers = list(csv_data[0].keys())
        else:
            headers = ['day_type', 'average_rentals']
        
        filename = f'weekday_weekend_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(csv_data, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV weekday vs weekend: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante il download: {str(e)}'
        }), 500

# curl -X GET http://localhost:5001/api/analytics/weather-impact/download
@analytics_bp.route('/weather-impact/download', methods=['GET'])
def download_weather_impact_csv():
    """Download analisi impatto meteo in formato CSV"""
    try:
        data = analytics_service.get_weather_impact_analysis()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        # Prepara i dati per CSV
        csv_data = []
        if isinstance(data, dict):
            for weather_condition, stats in data.items():
                if isinstance(stats, dict):
                    row = {'weather_condition': weather_condition}
                    row.update(stats)
                    csv_data.append(row)
                else:
                    csv_data.append({
                        'weather_condition': weather_condition,
                        'value': stats
                    })
        else:
            csv_data = data
        
        # Determina headers dinamicamente
        if csv_data:
            headers = list(csv_data[0].keys())
        else:
            headers = ['weather_condition', 'average_rentals']
        
        filename = f'weather_impact_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(csv_data, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV impatto meteo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante il download: {str(e)}'
        }), 500

# curl -X GET http://localhost:5001/api/analytics/download-all
@analytics_bp.route('/download-all', methods=['GET'])
def download_all_analytics_csv():
    """Download di tutte le analisi in un unico file CSV"""
    try:
        # Ottieni tutti i dati
        hourly_data = analytics_service.get_hourly_rental_patterns()
        weekday_data = analytics_service.get_weekday_weekend_comparison()
        weather_data = analytics_service.get_weather_impact_analysis()
        
        if not any([hourly_data, weekday_data, weather_data]):
            return jsonify({
                'success': False,
                'error': 'Nessun dato trovato nel database'
            }), 404
        
        # Crea un CSV con tutte le sezioni
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Sezione Pattern Orari
        if hourly_data:
            writer.writerow(['=== PATTERN ORARI ==='])
            writer.writerow(['hour', 'average_rentals'])
            if isinstance(hourly_data, dict):
                for hour, avg_rentals in hourly_data.items():
                    writer.writerow([hour, avg_rentals])
            writer.writerow([])  # Riga vuota
        
        # Sezione Weekday vs Weekend
        if weekday_data:
            writer.writerow(['=== WEEKDAY VS WEEKEND ==='])
            if isinstance(weekday_data, dict):
                for day_type, stats in weekday_data.items():
                    if isinstance(stats, dict):
                        headers = ['day_type'] + list(stats.keys())
                        writer.writerow(headers)
                        row = [day_type] + list(stats.values())
                        writer.writerow(row)
                    else:
                        writer.writerow(['day_type', 'value'])
                        writer.writerow([day_type, stats])
            writer.writerow([])  # Riga vuota
        
        # Sezione Impatto Meteo
        if weather_data:
            writer.writerow(['=== IMPATTO METEO ==='])
            if isinstance(weather_data, dict):
                for condition, stats in weather_data.items():
                    if isinstance(stats, dict):
                        headers = ['weather_condition'] + list(stats.keys())
                        writer.writerow(headers)
                        row = [condition] + list(stats.values())
                        writer.writerow(row)
                    else:
                        writer.writerow(['weather_condition', 'value'])
                        writer.writerow([condition, stats])
        
        output.seek(0)
        filename = f'complete_analytics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        logging.error(f"Errore nel download CSV completo: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Errore durante il download: {str(e)}'
        }), 500