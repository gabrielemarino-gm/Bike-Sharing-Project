#!/usr/bin/env python3
"""
Script di test per verificare che tutti i modelli ML funzionino correttamente
"""

import sys
import os
import logging
import pandas as pd
import numpy as np

# Aggiunge il path dell'app per imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from models.ml.rental_count_predictor import RentalCountPredictor
from models.ml.peak_demand_predictor import PeakDemandPredictor  
from models.ml.weather_impact_predictor import WeatherImpactPredictor

def load_data_from_csv(filepath):
    """Carica dati da file CSV"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File non trovato: {filepath}")
    
    data = pd.read_csv(filepath)
    return data

def test_rental_count_predictor():
    """Test del modello di predizione numero noleggi"""
    print("\n🚲 Testing RentalCountPredictor...")
    
    # Crea dati e modello
    data = load_data_from_csv("data/hour.csv")
    predictor = RentalCountPredictor(model_type='random_forest')
    
    # Training
    print("   Training modello...")
    metrics = predictor.train(data)
    print(f"   ✅ Training completato. R²: {metrics['r2_score']:.3f}")
    
    # Test predizione
    test_features = {
        'season': 2, 'yr': 1, 'mnth': 6, 'hr': 14,
        'holiday': 0, 'weekday': 2, 'workingday': 1,
        'weathersit': 1, 'temp': 0.7, 'atemp': 0.68,
        'hum': 0.5, 'windspeed': 0.2
    }
    prediction = predictor.predict(test_features)
    print(f"   ✅ Predizione: {prediction['predicted_rentals']} noleggi")
        
    # Salvataggio modello
    predictor.save_model()
    print("   ✅ Modello salvato correttamente.")

    return True

def test_peak_demand_predictor():
    """Test del modello di predizione picchi"""
    print("\n📈 Testing PeakDemandPredictor...")
    
    # Crea dati e modello
    data = load_data_from_csv("data/hour.csv")
    predictor = PeakDemandPredictor(model_type='random_forest')
    
    # Training
    print("   Training modello...")
    metrics = predictor.train(data)
    print(f"   ✅ Training completato. F1-Score: {metrics['f1_score']:.3f}")
    
    # Salvataggio modello
    predictor.save_model()
    print("   ✅ Modello salvato correttamente.")
    
    return True

def test_weather_impact_predictor():
    """Test del modello di impatto meteo"""
    print("\n🌦️  Testing WeatherImpactPredictor...")
    
    # Crea dati e modello
    data = load_data_from_csv("data/hour.csv")
    predictor = WeatherImpactPredictor(model_type='random_forest')
    
    # Training
    print("   Training modello...")
    metrics = predictor.train(data)
    print(f"   ✅ Training completato. R²: {metrics['r2_score']:.3f}")

    # Salvataggio modello
    predictor.save_model()
    print("   ✅ Modello salvato correttamente.")

    return True

def main():
    """Esegue tutti i test"""
    print("🧪 Test dei modelli ML per Bike Sharing Analytics")
    print("=" * 50)
    
    try:
        # Test tutti i modelli
        test_rental_count_predictor()
        test_peak_demand_predictor()
        test_weather_impact_predictor()
        
        # Test Load modelli
        model_rcp = RentalCountPredictor()
        model_rcp.load_model()
        model_rcp.print_model_info()
        if model_rcp and model_rcp.model:
            print("   ✅ RentalCountPredictor caricato correttamente.")

        model_pdp = PeakDemandPredictor()
        model_pdp.load_model()
        model_pdp.print_model_info()
        if model_pdp and model_pdp.model:
            print("   ✅ PeakDemandPredictor caricato correttamente.")

        model_wip = WeatherImpactPredictor()
        model_wip.load_model()
        model_wip.print_model_info()
        if model_wip and model_wip.model:
            print("   ✅ WeatherImpactPredictor caricato correttamente.")
        
        print("\n✅ Tutti i test completati con successo!")
        
    except Exception as e:
        print(f"\n❌ Errore durante i test: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
