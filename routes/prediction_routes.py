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

# curl -X POST -H "Content-Type: application/json" -d '{"input_data": {"season": 1, "yr": 0, "mnth": 1, "hr": 0, "holiday": 0, "weekday": 6, "workingday": 0, "weathersit": 1, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}}' http://localhost:5001/api/prediction/predict-peak-demand/download
@prediction_bp.route('/predict-peak-demand/download', methods=['POST'])
def download_peak_demand_predictions_csv():
    """Download predizioni domanda di picco in formato CSV"""
    try:
        input_data = request.json.get('input_data')
        if not input_data:
            return jsonify({'error': 'Richiesto input_data'}), 400

        try:
            prediction = PeakDemandPredictor.predict(input_data)
            
            print("Debug Peak Prediction", prediction)
            logging.info(f"Prediction: {prediction}")
            
            # Estrai le features utilizzate dal modello
            features_used = prediction.get('features_used', [])
            
            # Converti il valore booleano in formato numerico per il CSV
            is_peak = prediction.get('is_peak', False)
            predicted_peak = 1 if is_peak else 0
            
            # Estrai probabilità e soglia
            peak_probability = round(float(prediction.get('peak_probability', 0)), 4)
            peak_threshold = round(float(prediction.get('peak_threshold', 0)), 2)
            
            result_row = {
                'prediction_id': 1,
                # Features utilizzate dal modello (nell'ordine corretto)
                'season': input_data.get('season', 'N/A'),
                'yr': input_data.get('yr', 'N/A'),
                'mnth': input_data.get('mnth', 'N/A'),
                'hr': input_data.get('hr', 'N/A'),
                'holiday': input_data.get('holiday', 'N/A'),
                'weekday': input_data.get('weekday', 'N/A'),
                'workingday': input_data.get('workingday', 'N/A'),
                'weathersit': input_data.get('weathersit', 'N/A'),
                'temp': input_data.get('temp', 'N/A'),
                'atemp': input_data.get('atemp', 'N/A'),
                'hum': input_data.get('hum', 'N/A'),
                'windspeed': input_data.get('windspeed', 'N/A'),
                # Risultati della predizione
                'is_peak': predicted_peak,
                'peak_probability': peak_probability,
                'peak_threshold': peak_threshold,
                'model_type': prediction.get('model_type', 'N/A'),
                'features_count': len(features_used),
                'status': 'success'
            }
            
        except Exception as e:
            logging.error(f"Errore nella predizione: {str(e)}")
            result_row = {
                'prediction_id': 1,
                # Features (anche in caso di errore per mantenere la struttura)
                'season': input_data.get('season', 'N/A'),
                'yr': input_data.get('yr', 'N/A'),
                'mnth': input_data.get('mnth', 'N/A'),
                'hr': input_data.get('hr', 'N/A'),
                'holiday': input_data.get('holiday', 'N/A'),
                'weekday': input_data.get('weekday', 'N/A'),
                'workingday': input_data.get('workingday', 'N/A'),
                'weathersit': input_data.get('weathersit', 'N/A'),
                'temp': input_data.get('temp', 'N/A'),
                'atemp': input_data.get('atemp', 'N/A'),
                'hum': input_data.get('hum', 'N/A'),
                'windspeed': input_data.get('windspeed', 'N/A'),
                # Risultati in errore
                'is_peak': 'ERROR',
                'peak_probability': 'ERROR',
                'peak_threshold': 'ERROR',
                'model_type': 'ERROR',
                'features_count': 'ERROR',
                'status': f'error: {str(e)}'
            }
        
        # Headers ordinati logicamente: ID, Features, Risultati, Status
        headers = [
            'prediction_id',
            # Features utilizzate dal modello
            'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 
            'weathersit', 'temp', 'atemp', 'hum', 'windspeed',
            # Risultati della predizione
            'is_peak', 'peak_probability', 'peak_threshold', 'model_type', 'features_count', 'status'
        ]
        
        filename = f'peak_demand_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response([result_row], filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni picchi: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data": {"weathersit": 1, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}}' http://localhost:5001/api/prediction/predict-weather-impact/download
@prediction_bp.route('/predict-weather-impact/download', methods=['POST'])
def download_weather_impact_predictions_csv():
    """Download predizioni impatto meteo in formato CSV"""
    try:
        input_data = request.json.get('input_data')
        if not input_data:
            return jsonify({'error': 'Richiesto input_data'}), 400

        try:
            prediction = WeatherImpactPredictor.predict(input_data)
            
            logging.info(f"Prediction: {prediction}")
            
            # Estrai le features utilizzate dal modello
            features_used = prediction.get('features_used', [])
            
            result_row = {
                'prediction_id': 1,
                # Features utilizzate dal modello (nell'ordine corretto)
                'weathersit': input_data.get('weathersit', 'N/A'),
                'temp': input_data.get('temp', 'N/A'),
                'atemp': input_data.get('atemp', 'N/A'),
                'hum': input_data.get('hum', 'N/A'),
                'windspeed': input_data.get('windspeed', 'N/A'),
                # Risultati della predizione
                'predicted_impact': round(float(prediction.get('predicted_impact', 0)), 6),
                'model_type': prediction.get('model_type', 'N/A'),
                'features_count': len(features_used),
                'status': 'success'
            }
            
        except Exception as e:
            logging.error(f"Errore nella predizione: {str(e)}")
            result_row = {
                'prediction_id': 1,
                # Features (anche in caso di errore per mantenere la struttura)
                'weathersit': input_data.get('weathersit', 'N/A'),
                'temp': input_data.get('temp', 'N/A'),
                'atemp': input_data.get('atemp', 'N/A'),
                'hum': input_data.get('hum', 'N/A'),
                'windspeed': input_data.get('windspeed', 'N/A'),
                # Risultati in errore
                'predicted_impact': 'ERROR',
                'model_type': 'ERROR',
                'features_count': 'ERROR',
                'status': f'error: {str(e)}'
            }
        
        # Headers ordinati logicamente: ID, Features, Risultati, Status
        headers = [
            'prediction_id',
            # Features utilizzate dal modello
            'weathersit', 'temp', 'atemp', 'hum', 'windspeed',
            # Risultati della predizione
            'predicted_impact', 'model_type', 'features_count', 'status'
        ]
        
        filename = f'weather_impact_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response([result_row], filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni meteo: {str(e)}")
        return jsonify({'error': str(e)}), 500

# curl -X POST -H "Content-Type: application/json" -d '{"input_data": {"season": 1, "yr": 0, "mnth": 1, "hr": 0, "holiday": 0, "weekday": 6, "workingday": 0, "weathersit": 1, "temp": 0.24, "atemp": 0.2879, "hum": 0.81, "windspeed": 0.0}}' http://localhost:5001/api/prediction/predict-rental-count/download
@prediction_bp.route('/predict-rental-count/download', methods=['POST'])
def download_rental_count_predictions_csv():
    """Download predizioni conteggio noleggi in formato CSV"""
    try:
        input_data = request.json.get('input_data')
        if not input_data:
            return jsonify({'error': 'Richiesto input_data'}), 400

        try:
            prediction = RentalCountPredictor.predict(input_data)
            
            logging.info(f"Prediction: {prediction}")
            
            # Estrai le features utilizzate dal modello
            features_used = prediction.get('features_used', [])
            
            result_row = {
                'prediction_id': 1,
                # Features utilizzate dal modello (nell'ordine corretto)
                'season': input_data.get('season', 'N/A'),
                'yr': input_data.get('yr', 'N/A'),
                'mnth': input_data.get('mnth', 'N/A'),
                'hr': input_data.get('hr', 'N/A'),
                'holiday': input_data.get('holiday', 'N/A'),
                'weekday': input_data.get('weekday', 'N/A'),
                'workingday': input_data.get('workingday', 'N/A'),
                'weathersit': input_data.get('weathersit', 'N/A'),
                'temp': input_data.get('temp', 'N/A'),
                'atemp': input_data.get('atemp', 'N/A'),
                'hum': input_data.get('hum', 'N/A'),
                'windspeed': input_data.get('windspeed', 'N/A'),
                # Risultati della predizione
                'predicted_rentals': int(prediction.get('predicted_rentals', 0)),
                'model_type': prediction.get('model_type', 'N/A'),
                'features_count': len(features_used),
                'status': 'success'
            }
            
        except Exception as e:
            logging.error(f"Errore nella predizione: {str(e)}")
            result_row = {
                'prediction_id': 1,
                # Features (anche in caso di errore per mantenere la struttura)
                'season': input_data.get('season', 'N/A'),
                'yr': input_data.get('yr', 'N/A'),
                'mnth': input_data.get('mnth', 'N/A'),
                'hr': input_data.get('hr', 'N/A'),
                'holiday': input_data.get('holiday', 'N/A'),
                'weekday': input_data.get('weekday', 'N/A'),
                'workingday': input_data.get('workingday', 'N/A'),
                'weathersit': input_data.get('weathersit', 'N/A'),
                'temp': input_data.get('temp', 'N/A'),
                'atemp': input_data.get('atemp', 'N/A'),
                'hum': input_data.get('hum', 'N/A'),
                'windspeed': input_data.get('windspeed', 'N/A'),
                # Risultati in errore
                'predicted_rentals': 'ERROR',
                'model_type': 'ERROR',
                'features_count': 'ERROR',
                'status': f'error: {str(e)}'
            }
        
        # Headers ordinati logicamente: ID, Features, Risultati, Status
        headers = [
            'prediction_id',
            # Features utilizzate dal modello
            'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday', 
            'weathersit', 'temp', 'atemp', 'hum', 'windspeed',
            # Risultati della predizione
            'predicted_rentals', 'model_type', 'features_count', 'status'
        ]
        
        filename = f'rental_count_predictions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return create_csv_response([result_row], filename, headers)
        
    except Exception as e:
        logging.error(f"Errore nel download CSV predizioni conteggio: {str(e)}")
        return jsonify({'error': str(e)}), 500
