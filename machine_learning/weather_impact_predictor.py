"""
Modello ML per predizione dell'impatto delle condizioni meteorologiche sui noleggi
Tipo: Regressione + Analisi What-If
Target: weather_impact_score (Percentuale di variazione rispetto alla media per quella fascia oraria)
Features: weathersit, temp, atemp, hum, windspeed + features temporali per baseline
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import os
import logging

from database.data_loader import BikeDataLoader


class WeatherImpactPredictor:
    """Predittore dell'impatto meteo sui noleggi"""
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.baseline_model = None
        self.is_trained = False

        # Features utilizzate per il training/predizione.
        # Esclusi:
        #   • 'dteday' per evitare data leakage: il giorno specifico non deve influenzare il modello rispetto al meteo.
        #   • 'casual' e 'registered' per evitare leakage da target
        #   • 'cnt' per evitare leakage da target
        self.weather_features = ['weathersit', 'temp', 'atemp', 'hum', 'windspeed']
        self.temporal_features = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 'workingday']
        
        self.training_metrics = {}
        self.weather_baselines = {}
        self.logger = logging.getLogger(__name__)
    
    def initialize_model(self):
        """Inizializza il modello ML in base al tipo scelto"""
        if self.model_type == 'linear_regression':
            return LinearRegression()
        elif self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=100, 
                random_state=44, 
                max_depth=12
            )
        else:
            raise ValueError(f"Tipo di modello non supportato: {self.model_type}")
    
    def train(self):
        """
        Addestra il modello sui dati di training
                    
        Returns:
            dict: Metriche di training
        """
        try:
            # Preprocessing dei dati semplificato
            data = BikeDataLoader.download_data_in_dataframe()
            
            # Rimuovi righe con valori mancanti nelle features critiche
            data = data.dropna()
            
            # TODO: Controllare se 100 è un numero adeguato
            if len(data) < 100:
                raise ValueError("Dataset troppo piccolo per training")
            
            # Calcolare baseline: usiamo la media come baseline semplice
            hourly_means = data.groupby('hr')['cnt'].mean() # Prendo la media dei noleggi per ogni ora
            data['baseline_expected'] = data['hr'].map(hourly_means)
            
            # Weather impact score semplificato. Semplicemente viene calcolato come differenza percentuale
            # fra i noleggi effettivi e quelli medi per quell'ora (più 1 per evitare divisione per zero)
            data['weather_impact'] = (data['cnt'] - data['baseline_expected']) / (data['baseline_expected'] + 1)
            
            # Features meteo
            weather_features = ['weathersit', 'temp', 'atemp', 'hum', 'windspeed']
            X = data[weather_features].values
            y = data['weather_impact'].values
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=44
            )
            
            # Addestrare modello
            self.model = self.initialize_model()
            self.model.fit(X_train, y_train)
            
            # Valutazione
            y_pred = self.model.predict(X_test)
            self.training_metrics = self.calculate_metrics(y_test, y_pred)
            
            # Marcare come addestrato
            self.is_trained = True
            
            self.logger.info(f"Modello impatto meteo {self.model_type} addestrato con successo")
            return self.training_metrics
            
        except Exception as e:
            self.logger.error(f"Errore durante il training: {str(e)}")
            raise
    
    def calculate_metrics(self, y_true, y_pred):
        """Calcola metriche di valutazione per impatto meteo"""
        try:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            from scipy.stats import pearsonr
            
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            
            # Correlazione tra predetto e reale
            correlation, _ = pearsonr(y_true, y_pred) if len(y_true) > 1 else (0.0, 1.0)
            
            # Accuracy su classificazione impatto (positivo/negativo/neutro)
            y_true_cat = np.where(y_true > 0.1, 1, np.where(y_true < -0.1, -1, 0))
            y_pred_cat = np.where(y_pred > 0.1, 1, np.where(y_pred < -0.1, -1, 0))
            impact_accuracy = np.mean(y_true_cat == y_pred_cat)
            
            return {
                'rmse': float(rmse),
                'mae': float(mae),
                'r2_score': float(r2),
                'correlation': float(correlation),
                'impact_accuracy': float(impact_accuracy),
                'test_samples': len(y_true)
            }
            
        except Exception as e:
            self.logger.error(f"Errore nel calcolo metriche: {str(e)}")
            return {
                'rmse': 0.0, 'mae': 0.0, 'r2_score': 0.0, 
                'correlation': 0.0, 'impact_accuracy': 0.0
            }
    
    @classmethod
    def predict(cls, features):
        """
        Predice l'impatto meteo basato sulle features fornite
        Args:
            features (dict): Dizionario con le features necessarie
        
        Returns:
            dict: Predizione e dettagli del modello
        """
        # Carica il modello
        predictor = cls()
        predictor.load_model()

        if not predictor.is_trained:
            raise ValueError("Modello non ancora addestrato")

        try:    
            # Prepara le features
            X = predictor.prepare_features_single(features)

            # Effettua la predizione
            y_pred = predictor.model.predict(X)
            
            return {
                'predicted_impact': y_pred[0],
                'model_type': predictor.model_type,
                'features_used': list(features.keys())
            }
            
        except Exception as e:
            predictor.logger.error(f"Errore durante la predizione: {str(e)}")
            raise
    
    def prepare_features_single(self, features):
        """
        Prepara features per una singola predizione
        
        Args:
            features (dict): Features di input
            
        Returns:
            np.ndarray: Array 2D con features processate
        """
        
        # Crea array con valori di default
        feature_values = []
        for feature in self.weather_features + self.temporal_features:
            if feature in features:
                feature_values.append(features[feature])
            else:
                # TODO: Forse meglio lanciare errore se mancano features
                # raise ValueError(f"Feature mancante: {feature_name}")
                self.logger.warning(f"Feature mancante: {feature}, uso valore di default 0")
                feature_values.append(0)  # Valore di default se mancante
        
        return np.array(feature_values).reshape(1, -1) # Array 2D
    
  

    def save_model(self, filename=None):
        """Salva il modello addestrato"""
        if not self.is_trained:
            raise ValueError("Nessun modello addestrato da salvare")

        try:
            # Nome file di default
            if filename is None:
                filename = f'weather_impact_predictor_{self.model_type}.joblib'
            
            # Percorso assoluto per salvare in /progetto/weights/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            models_dir = os.path.join(current_dir, 'weights')
            filepath = os.path.join(models_dir, filename)
        
            # Crea directory se non esiste
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Salva modello e metadati completi
            model_data = {
                'model': self.model,
                'baseline_model': self.baseline_model,
                'model_type': self.model_type,
                'weather_features': self.weather_features,
                'temporal_features': self.temporal_features,
                'weather_baselines': self.weather_baselines,
                'hourly_baseline': getattr(self, 'hourly_baseline', {}),
                'training_metrics': self.training_metrics,
                'is_trained': self.is_trained,
                'created_at': pd.Timestamp.now().isoformat()
            }
            
            # Salvare con joblib
            joblib.dump(model_data, filepath)
            self.logger.info(f"Modello impatto meteo salvato in {filepath}")
            
        except Exception as e:
            self.logger.error(f"Errore nel salvataggio modello: {str(e)}")
            raise
    
    def load_model(self, filename=None):
        """Carica un modello pre-addestrato"""
        
        try:
            # Nome file di default
            if filename is None:
                filename = f'weather_impact_predictor_{self.model_type}.joblib'
            
            # Percorso assoluto per salvare in /progetto/weights/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            models_dir = os.path.join(current_dir, 'weights')
            filepath = os.path.join(models_dir, filename)
            
            # Carica modello e metadati completi
            model_data = joblib.load(filepath)
            
            # Verifica struttura dati
            required_keys = ['model', 'model_type', 'is_trained']
            for key in required_keys:
                if key not in model_data:
                    raise ValueError(f"File modello corrotto: manca '{key}'")
            
            # Ripristina stato del modello
            self.model = model_data['model']
            self.baseline_model = model_data.get('baseline_model')
            self.model_type = model_data['model_type']
            self.weather_features = model_data.get('weather_features', self.weather_features)
            self.temporal_features = model_data.get('temporal_features', self.temporal_features)
            self.weather_baselines = model_data.get('weather_baselines', {})
            self.hourly_baseline = model_data.get('hourly_baseline', {})
            self.training_metrics = model_data.get('training_metrics', {})
            self.is_trained = model_data['is_trained']
            
            self.logger.info(f"Modello impatto meteo caricato da {filepath}")
            self.logger.info(f"Modello tipo: {self.model_type}")
            self.logger.info(f"Baseline caricati: {len(self.weather_baselines)} specifici, {len(self.hourly_baseline)} orari")
        
        except FileNotFoundError:
            self.logger.error(f"File modello non trovato. Prima devi addestrare il modello")
            raise
        
        except Exception as e:
            self.logger.error(f"Errore nel caricamento modello: {str(e)}")
            raise
    
    def get_model_info(self):
        """Restituisce informazioni sul modello"""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'weather_features': self.weather_features,
            'temporal_features': self.temporal_features,
            'baselines_calculated': len(self.weather_baselines),
            'training_metrics': self.training_metrics if self.is_trained else None,
            'target_variable': 'weather_impact_score (% change from baseline)',
            'prediction_type': 'Weather Impact Analysis',
            'capabilities': [
                'Current weather impact prediction',
                'Alternative scenario analysis', 
                'Weather sensitivity analysis',
                'Optimal conditions recommendation'
            ]
        }
        
    def print_model_info(self):
        """Stampa informazioni sul modello"""
        info = self.get_model_info()
        print("Modello WeatherImpactPredictor Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
        return
