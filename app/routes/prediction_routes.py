from flask import Blueprint, request, jsonify
from app.services.prediction_service import PredictionService
import logging

prediction_bp = Blueprint('prediction', __name__)
prediction_service = PredictionService()

@prediction_bp.route('/train', methods=['POST'])
def train_model():
    """Addestra il modello ML"""
    try:
        model_type = request.json.get('model_type', 'linear_regression')
        result = prediction_service.train_model(model_type)
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Errore nell'addestramento del modello: {str(e)}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/predict', methods=['POST'])
def make_prediction():
    """Effettua una predizione"""
    try:
        features = request.json.get('features')
        if not features:
            return jsonify({'error': 'Features mancanti'}), 400
        
        prediction = prediction_service.predict(features)
        return jsonify({'prediction': prediction}), 200
    except Exception as e:
        logging.error(f"Errore nella predizione: {str(e)}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """Informazioni sul modello corrente"""
    try:
        info = prediction_service.get_model_info()
        return jsonify(info), 200
    except Exception as e:
        logging.error(f"Errore nel recupero info modello: {str(e)}")
        return jsonify({'error': str(e)}), 500

@prediction_bp.route('/evaluate', methods=['GET'])
def evaluate_model():
    """Valuta le performance del modello"""
    try:
        evaluation = prediction_service.evaluate_model()
        return jsonify(evaluation), 200
    except Exception as e:
        logging.error(f"Errore nella valutazione del modello: {str(e)}")
        return jsonify({'error': str(e)}), 500
