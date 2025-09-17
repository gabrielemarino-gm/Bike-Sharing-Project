from flask import Blueprint, request, jsonify, Response
from machine_learning.peak_demand_predictor import PeakDemandPredictor
from machine_learning.weather_impact_predictor import WeatherImpactPredictor
from machine_learning.rental_count_predictor import  RentalCountPredictor
import csv
import io
from datetime import datetime
import logging

prediction_bp = Blueprint('prediction', __name__)

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

# curl -X POST -H "Content-Type: application/json" -d '{"model_type": "logistic_regression"}' http://localhost:5001/api/prediction/train-peak-model
@prediction_bp.route('/train-peak-model', methods=['POST'])
def train_peak_model():
    """Addestra il modello ML per la previsione della domanda di picco"""
    try:
        model_type = request.json.get('model_type')
        model = PeakDemandPredictor(model_type=model_type, peak_threshold_percentile=80)

        # Addestra il modello
        result = model.train()
        logging.info(f"Training completato: {result}")

        # Salva il modello addestrato
        model.save_model()
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Errore nell'addestramento del modello: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"model_type": "random_forest"}' http://localhost:5001/api/prediction/train-weather-model
@prediction_bp.route('/train-weather-model', methods=['POST'])
def train_weather_model():
    """Addestra il modello ML per l'impatto meteo"""
    try:
        model_type = request.json.get('model_type')
        model = WeatherImpactPredictor(model_type=model_type)
        
        # Addestra il modello
        result = model.train()
        logging.info(f"Training completato: {result}")
        
        # Salva il modello addestrato
        model.save_model()
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Errore nell'addestramento del modello: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"model_type": "random_forest"}' http://localhost:5001/api/prediction/train-rental-model
@prediction_bp.route('/train-rental-model', methods=['POST'])
def train_rental_model():
    """Addestra il modello ML per il conteggio noleggi"""
    try:
        model_type = request.json.get('model_type', 'linear_regression')
        model = RentalCountPredictor(model_type=model_type)
        
        # Addestra il modello
        result = model.train()
        logging.info(f"Training completato: {result}")
        
        # Salva il modello addestrato
        model.save_model()
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Errore nell'addestramento del modello: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data": {
#     "season": 1,
#     "yr": 0,
#     "mnth": 1,
#     "hr": 0,
#     "holiday": 0,
#     "weekday": 6,
#     "workingday": 0,
#     "weathersit": 1,
#     "temp": 0.24,
#     "atemp": 0.2879,
#     "hum": 0.81,
#     "windspeed": 0.0
# }}' http://localhost:5001/api/prediction/predict-peak-demand
@prediction_bp.route('/predict-peak-demand', methods=['POST'])
def predict_peak_demand():
    """Prevede la domanda di picco usando il modello addestrato"""
    try:
        input_data = request.json.get('input_data')
        if not input_data:
            return jsonify({'error': 'Nessun dato di input fornito'}), 400
        
        prediction = PeakDemandPredictor.predict(input_data)
        return jsonify({'prediction': prediction}), 200
    except Exception as e:
        logging.error(f"Errore nella previsione della domanda di picco: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

# curl -X POST -H "Content-Type: application/json" -d '{"input_data": {
#     "season": 1,
#     "yr": 0,
#     "mnth": 1,
#     "hr": 0,
#     "holiday": 0,
#     "weekday": 6,
#     "workingday": 0,
#     "temp": 0.24,
#     "atemp": 0.2879,
#     "hum": 0.81,
#     "windspeed": 0.0
# }}' http://localhost:5001/api/prediction/predict-weather-impact
@prediction_bp.route('/predict-weather-impact', methods=['POST'])
def predict_weather_impact():
    """Prevede l'impatto delle condizioni meteo usando il modello addestrato"""
    try:
        input_data = request.json.get('input_data')
        if not input_data:
            return jsonify({'error': 'Nessun dato di input fornito'}), 400
        
        prediction = WeatherImpactPredictor.predict(input_data)
        return jsonify({'prediction': prediction}), 200
    except Exception as e:
        logging.error(f"Errore nella previsione dell'impatto meteo: {str(e)}")
        return jsonify({'error': str(e)}), 500


# curl -X POST -H "Content-Type: application/json" -d '{"input_data": {
#     "season": 1,
#     "yr": 0,
#     "mnth": 1,
#     "hr": 0,
#     "holiday": 0,
#     "weekday": 6,
#     "workingday": 0,
#     "weathersit": 1,
#     "temp": 0.24,
#     "atemp": 0.2879,
#     "hum": 0.81,
#     "windspeed": 0.0
# }}' http://localhost:5001/api/prediction/predict-rental-count
@prediction_bp.route('/predict-rental-count', methods=['POST'])
def predict_rental_count():
    """Prevede il conteggio dei noleggi usando il modello addestrato"""
    try:
        input_data = request.json.get('input_data')
        if not input_data:
            return jsonify({'error': 'Nessun dato di input fornito'}), 400
        
        prediction = RentalCountPredictor.predict(input_data)
        return jsonify({'prediction': prediction}), 200
    except Exception as e:
        logging.error(f"Errore nella previsione del conteggio noleggi: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data_list": [{"season": 1, "yr": 0, "mnth": 1, "hr": 0, "holiday": 0, "weekday": 6, "workingday": 0, "weathersit": 1, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}]}' http://localhost:5001/api/prediction/predict-peak-demand/download
@prediction_bp.route('/predict-peak-demand/download', methods=['POST'])
def download_peak_demand_predictions_csv():
    """Download predizioni domanda di picco in formato CSV"""
    try:
        input_data_list = request.json.get('input_data_list', [])
        if not input_data_list:
            return jsonify({'error': 'Lista input_data_list richiesta'}), 400
        
        results = []
        for i, input_data in enumerate(input_data_list):
            try:
                prediction = PeakDemandPredictor.predict(input_data)
                result_row = {
                    'prediction_id': i + 1,
                    'season': input_data.get('season'),
                    'yr': input_data.get('yr'),
                    'mnth': input_data.get('mnth'),
                    'hr': input_data.get('hr'),
                    'holiday': input_data.get('holiday'),
                    'weekday': input_data.get('weekday'),
                    'workingday': input_data.get('workingday'),
                    'weathersit': input_data.get('weathersit'),
                    'temp': input_data.get('temp'),
                    'atemp': input_data.get('atemp'),
                    'hum': input_data.get('hum'),
                    'windspeed': input_data.get('windspeed'),
                    'predicted_peak': prediction.get('prediction', 'N/A'),
                    'confidence': prediction.get('confidence', 'N/A'),
                    'status': 'success'
                }
                results.append(result_row)
            except Exception as e:
                error_row = {
                    'prediction_id': i + 1,
                    'season': input_data.get('season'),
                    'yr': input_data.get('yr'),
                    'mnth': input_data.get('mnth'),
                    'hr': input_data.get('hr'),
                    'holiday': input_data.get('holiday'),
                    'weekday': input_data.get('weekday'),
                    'workingday': input_data.get('workingday'),
                    'weathersit': input_data.get('weathersit'),
                    'temp': input_data.get('temp'),
                    'atemp': input_data.get('atemp'),
                    'hum': input_data.get('hum'),
                    'windspeed': input_data.get('windspeed'),
                    'predicted_peak': 'ERROR',
                    'confidence': 'ERROR',
                    'status': f'error: {str(e)}'
                }
                results.append(error_row)
        
        headers = ['prediction_id', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                  'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 
                  'predicted_peak', 'confidence', 'status']
        
        filename = f'peak_demand_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(results, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni picchi: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data_list": [{"season": 1, "yr": 0, "mnth": 1, "hr": 0, "holiday": 0, "weekday": 6, "workingday": 0, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}]}' http://localhost:5001/api/prediction/predict-weather-impact/download
@prediction_bp.route('/predict-weather-impact/download', methods=['POST'])
def download_weather_impact_predictions_csv():
    """Download predizioni impatto meteo in formato CSV"""
    try:
        input_data_list = request.json.get('input_data_list', [])
        if not input_data_list:
            return jsonify({'error': 'Lista input_data_list richiesta'}), 400
        
        results = []
        for i, input_data in enumerate(input_data_list):
            try:
                prediction = WeatherImpactPredictor.predict(input_data)
                result_row = {
                    'prediction_id': i + 1,
                    'season': input_data.get('season'),
                    'yr': input_data.get('yr'),
                    'mnth': input_data.get('mnth'),
                    'hr': input_data.get('hr'),
                    'holiday': input_data.get('holiday'),
                    'weekday': input_data.get('weekday'),
                    'workingday': input_data.get('workingday'),
                    'temp': input_data.get('temp'),
                    'atemp': input_data.get('atemp'),
                    'hum': input_data.get('hum'),
                    'windspeed': input_data.get('windspeed'),
                    'predicted_impact': prediction.get('prediction', 'N/A'),
                    'impact_score': prediction.get('impact_score', 'N/A'),
                    'status': 'success'
                }
                results.append(result_row)
            except Exception as e:
                error_row = {
                    'prediction_id': i + 1,
                    'season': input_data.get('season'),
                    'yr': input_data.get('yr'),
                    'mnth': input_data.get('mnth'),
                    'hr': input_data.get('hr'),
                    'holiday': input_data.get('holiday'),
                    'weekday': input_data.get('weekday'),
                    'workingday': input_data.get('workingday'),
                    'temp': input_data.get('temp'),
                    'atemp': input_data.get('atemp'),
                    'hum': input_data.get('hum'),
                    'windspeed': input_data.get('windspeed'),
                    'predicted_impact': 'ERROR',
                    'impact_score': 'ERROR',
                    'status': f'error: {str(e)}'
                }
                results.append(error_row)
        
        headers = ['prediction_id', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                  'workingday', 'temp', 'atemp', 'hum', 'windspeed', 
                  'predicted_impact', 'impact_score', 'status']
        
        filename = f'weather_impact_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(results, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni meteo: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data_list": [{"season": 1, "yr": 0, "mnth": 1, "hr": 0, "holiday": 0, "weekday": 6, "workingday": 0, "weathersit": 1, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}]}' http://localhost:5001/api/prediction/predict-rental-count/download
@prediction_bp.route('/predict-rental-count/download', methods=['POST'])
def download_rental_count_predictions_csv():
    """Download predizioni conteggio noleggi in formato CSV"""
    try:
        input_data_list = request.json.get('input_data_list', [])
        if not input_data_list:
            return jsonify({'error': 'Lista input_data_list richiesta'}), 400
        
        results = []
        for i, input_data in enumerate(input_data_list):
            try:
                prediction = RentalCountPredictor.predict(input_data)
                result_row = {
                    'prediction_id': i + 1,
                    'season': input_data.get('season'),
                    'yr': input_data.get('yr'),
                    'mnth': input_data.get('mnth'),
                    'hr': input_data.get('hr'),
                    'holiday': input_data.get('holiday'),
                    'weekday': input_data.get('weekday'),
                    'workingday': input_data.get('workingday'),
                    'weathersit': input_data.get('weathersit'),
                    'temp': input_data.get('temp'),
                    'atemp': input_data.get('atemp'),
                    'hum': input_data.get('hum'),
                    'windspeed': input_data.get('windspeed'),
                    'predicted_count': prediction.get('prediction', 'N/A'),
                    'confidence_interval_low': prediction.get('confidence_interval', {}).get('low', 'N/A'),
                    'confidence_interval_high': prediction.get('confidence_interval', {}).get('high', 'N/A'),
                    'status': 'success'
                }
                results.append(result_row)
            except Exception as e:
                error_row = {
                    'prediction_id': i + 1,
                    'season': input_data.get('season'),
                    'yr': input_data.get('yr'),
                    'mnth': input_data.get('mnth'),
                    'hr': input_data.get('hr'),
                    'holiday': input_data.get('holiday'),
                    'weekday': input_data.get('weekday'),
                    'workingday': input_data.get('workingday'),
                    'weathersit': input_data.get('weathersit'),
                    'temp': input_data.get('temp'),
                    'atemp': input_data.get('atemp'),
                    'hum': input_data.get('hum'),
                    'windspeed': input_data.get('windspeed'),
                    'predicted_count': 'ERROR',
                    'confidence_interval_low': 'ERROR',
                    'confidence_interval_high': 'ERROR',
                    'status': f'error: {str(e)}'
                }
                results.append(error_row)
        
        headers = ['prediction_id', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                  'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 
                  'predicted_count', 'confidence_interval_low', 'confidence_interval_high', 'status']
        
        filename = f'rental_count_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response(results, filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni conteggio: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data_list": [{"season": 1, "yr": 0, "mnth": 1, "hr": 0, "holiday": 0, "weekday": 6, "workingday": 0, "weathersit": 1, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}], "prediction_types": ["peak_demand", "weather_impact", "rental_count"]}' http://localhost:5001/api/prediction/download-all-predictions -o all_predictions.csv
@prediction_bp.route('/download-all-predictions', methods=['POST'])
def download_all_predictions_csv():
    """Download di tutte le predizioni in un unico file CSV"""
    try:
        input_data_list = request.json.get('input_data_list', [])
        prediction_types = request.json.get('prediction_types', ['peak_demand', 'weather_impact', 'rental_count'])
        
        if not input_data_list:
            return jsonify({'error': 'Lista input_data_list richiesta'}), 400
        
        # Crea un CSV con tutte le predizioni
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header generale
        writer.writerow(['=== REPORT PREDIZIONI COMPLETE ==='])
        writer.writerow([f'Generato il: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
        writer.writerow([f'Numero di predizioni: {len(input_data_list)}'])
        writer.writerow([])
        
        for prediction_type in prediction_types:
            writer.writerow([f'=== {prediction_type.upper().replace("_", " ")} ==='])
            
            if prediction_type == 'peak_demand':
                headers = ['prediction_id', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                          'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 
                          'predicted_peak', 'confidence', 'status']
                writer.writerow(headers)
                
                for i, input_data in enumerate(input_data_list):
                    try:
                        prediction = PeakDemandPredictor.predict(input_data)
                        row = [i + 1, input_data.get('season'), input_data.get('yr'), 
                              input_data.get('mnth'), input_data.get('hr'), input_data.get('holiday'),
                              input_data.get('weekday'), input_data.get('workingday'), 
                              input_data.get('weathersit'), input_data.get('temp'), 
                              input_data.get('atemp'), input_data.get('hum'), 
                              input_data.get('windspeed'), prediction.get('prediction', 'N/A'),
                              prediction.get('confidence', 'N/A'), 'success']
                        writer.writerow(row)
                    except Exception as e:
                        row = [i + 1, input_data.get('season'), input_data.get('yr'), 
                              input_data.get('mnth'), input_data.get('hr'), input_data.get('holiday'),
                              input_data.get('weekday'), input_data.get('workingday'), 
                              input_data.get('weathersit'), input_data.get('temp'), 
                              input_data.get('atemp'), input_data.get('hum'), 
                              input_data.get('windspeed'), 'ERROR', 'ERROR', f'error: {str(e)}']
                        writer.writerow(row)
            
            elif prediction_type == 'weather_impact':
                headers = ['prediction_id', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                          'workingday', 'temp', 'atemp', 'hum', 'windspeed', 
                          'predicted_impact', 'impact_score', 'status']
                writer.writerow(headers)
                
                for i, input_data in enumerate(input_data_list):
                    try:
                        prediction = WeatherImpactPredictor.predict(input_data)
                        row = [i + 1, input_data.get('season'), input_data.get('yr'), 
                              input_data.get('mnth'), input_data.get('hr'), input_data.get('holiday'),
                              input_data.get('weekday'), input_data.get('workingday'), 
                              input_data.get('temp'), input_data.get('atemp'), 
                              input_data.get('hum'), input_data.get('windspeed'),
                              prediction.get('prediction', 'N/A'), 
                              prediction.get('impact_score', 'N/A'), 'success']
                        writer.writerow(row)
                    except Exception as e:
                        row = [i + 1, input_data.get('season'), input_data.get('yr'), 
                              input_data.get('mnth'), input_data.get('hr'), input_data.get('holiday'),
                              input_data.get('weekday'), input_data.get('workingday'), 
                              input_data.get('temp'), input_data.get('atemp'), 
                              input_data.get('hum'), input_data.get('windspeed'),
                              'ERROR', 'ERROR', f'error: {str(e)}']
                        writer.writerow(row)
            
            elif prediction_type == 'rental_count':
                headers = ['prediction_id', 'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                          'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed', 
                          'predicted_count', 'confidence_interval_low', 'confidence_interval_high', 'status']
                writer.writerow(headers)
                
                for i, input_data in enumerate(input_data_list):
                    try:
                        prediction = RentalCountPredictor.predict(input_data)
                        row = [i + 1, input_data.get('season'), input_data.get('yr'), 
                              input_data.get('mnth'), input_data.get('hr'), input_data.get('holiday'),
                              input_data.get('weekday'), input_data.get('workingday'), 
                              input_data.get('weathersit'), input_data.get('temp'), 
                              input_data.get('atemp'), input_data.get('hum'), 
                              input_data.get('windspeed'), prediction.get('prediction', 'N/A'),
                              prediction.get('confidence_interval', {}).get('low', 'N/A'),
                              prediction.get('confidence_interval', {}).get('high', 'N/A'), 'success']
                        writer.writerow(row)
                    except Exception as e:
                        row = [i + 1, input_data.get('season'), input_data.get('yr'), 
                              input_data.get('mnth'), input_data.get('hr'), input_data.get('holiday'),
                              input_data.get('weekday'), input_data.get('workingday'), 
                              input_data.get('weathersit'), input_data.get('temp'), 
                              input_data.get('atemp'), input_data.get('hum'), 
                              input_data.get('windspeed'), 'ERROR', 'ERROR', 'ERROR', f'error: {str(e)}']
                        writer.writerow(row)
            
            writer.writerow([])  # Riga vuota tra sezioni
        
        output.seek(0)
        filename = f'all_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni complete: {str(e)}")
        return jsonify({'error': str(e)}), 500