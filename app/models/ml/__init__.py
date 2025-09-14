"""
Package per modelli di Machine Learning
Contiene i predittori specializzati per l'analisi bike sharing
"""

from .rental_count_predictor import RentalCountPredictor
from .peak_demand_predictor import PeakDemandPredictor
from .weather_impact_predictor import WeatherImpactPredictor

__all__ = [
    'RentalCountPredictor',
    'PeakDemandPredictor', 
    'WeatherImpactPredictor'
]

# Versione del package ML
__version__ = '1.0.0'

# Metadata sui modelli disponibili
AVAILABLE_MODELS = {
    'rental_count': {
        'class': RentalCountPredictor,
        'description': 'Predizione numero totale noleggi',
        'type': 'regression',
        'target': 'cnt'
    },
    'peak_demand': {
        'class': PeakDemandPredictor,
        'description': 'Predizione picchi di domanda',
        'type': 'binary_classification',
        'target': 'is_peak'
    },
    'weather_impact': {
        'class': WeatherImpactPredictor,
        'description': 'Analisi impatto condizioni meteo',
        'type': 'regression + analysis',
        'target': 'weather_impact_score'
    }
}

def get_available_models():
    """Restituisce informazioni sui modelli disponibili"""
    return AVAILABLE_MODELS

def create_model(model_name, **kwargs):
    """
    Factory function per creare istanze dei modelli
    
    Args:
        model_name (str): Nome del modello ('rental_count', 'peak_demand', 'weather_impact')
        **kwargs: Parametri specifici per il modello
        
    Returns:
        Istanza del modello richiesto
    """
    if model_name not in AVAILABLE_MODELS:
        available = ', '.join(AVAILABLE_MODELS.keys())
        raise ValueError(f"Modello '{model_name}' non disponibile. Modelli disponibili: {available}")
    
    model_class = AVAILABLE_MODELS[model_name]['class']
    return model_class(**kwargs)
