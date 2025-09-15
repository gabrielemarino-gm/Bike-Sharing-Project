from flask import Blueprint, request, jsonify
from machine_learning.peak_demand_predictor import PeakDemandPredictor
from machine_learning.weather_impact_predictor import WeatherImpactPredictor
from machine_learning.rental_count_predictor import  RentalCountPredictor

import logging

prediction_bp = Blueprint('prediction', __name__)

# curl -X POST -H "Content-Type: application/json" -d '{"model_type": "logistic_regression"}' http://localhost:5001/api/prediction/train-peak-model
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

# curl -X POST -H "Content-Type: application/json" -d '{"model_type": "random_forest"}' http://localhost:5001/api/prediction/train-weather-model
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
