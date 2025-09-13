import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
import logging
from app import db
from app.models.bike_record import BikeRecord
from app.config import Config

class PredictionService:
    """Servizio per predizioni con modelli ML"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.model_info = {}
        self.feature_columns = ['season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
                               'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed']
    
    def train_model(self, model_type='linear_regression'):
        """Addestra un modello ML"""
        try:
            # Carica i dati
            df = self._load_data_for_training()
            if df.empty:
                raise ValueError("Nessun dato disponibile per l'addestramento")
            
            # Prepara features e target
            X = df[self.feature_columns]
            y = df['cnt']
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Seleziona e addestra il modello
            if model_type == 'linear_regression':
                model = LinearRegression()
            elif model_type == 'decision_tree':
                model = DecisionTreeRegressor(random_state=42, max_depth=10)
            elif model_type == 'random_forest':
                model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            else:
                raise ValueError(f"Tipo di modello non supportato: {model_type}")
            
            # Addestramento
            model.fit(X_train, y_train)
            
            # Predizioni di test
            y_pred = model.predict(X_test)
            
            # Metriche di valutazione
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Salva il modello
            model_path = os.path.join(Config.MODEL_PATH, f'{model_type}_model.joblib')
            os.makedirs(Config.MODEL_PATH, exist_ok=True)
            joblib.dump(model, model_path)
            
            # Aggiorna informazioni del modello
            self.model = model
            self.model_info = {
                'model_type': model_type,
                'model_path': model_path,
                'training_date': pd.Timestamp.now().isoformat(),
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'metrics': {
                    'mse': float(mse),
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'r2_score': float(r2)
                },
                'feature_columns': self.feature_columns
            }
            
            # Salva info del modello
            info_path = os.path.join(Config.MODEL_PATH, f'{model_type}_info.joblib')
            joblib.dump(self.model_info, info_path)
            
            return {
                'message': f'Modello {model_type} addestrato con successo',
                'model_info': self.model_info
            }
            
        except Exception as e:
            self.logger.error(f"Errore nell'addestramento del modello: {str(e)}")
            raise
    
    def predict(self, features):
        """Effettua una predizione"""
        try:
            # Carica il modello se non è già caricato
            if self.model is None:
                self._load_latest_model()
            
            if self.model is None:
                raise ValueError("Nessun modello addestrato disponibile")
            
            # Prepara le features
            feature_array = np.array([[
                features.get('season', 1),
                features.get('yr', 0),
                features.get('mnth', 1),
                features.get('hr', 12),
                features.get('holiday', 0),
                features.get('weekday', 1),
                features.get('workingday', 1),
                features.get('weathersit', 1),
                features.get('temp', 0.5),
                features.get('atemp', 0.5),
                features.get('hum', 0.5),
                features.get('windspeed', 0.2)
            ]])
            
            # Predizione
            prediction = self.model.predict(feature_array)[0]
            
            return {
                'predicted_count': max(0, int(round(prediction))),  # Non può essere negativo
                'features_used': features,
                'model_type': self.model_info.get('model_type', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Errore nella predizione: {str(e)}")
            raise
    
    def get_model_info(self):
        """Restituisce informazioni sul modello corrente"""
        try:
            if not self.model_info:
                self._load_latest_model()
            
            return self.model_info if self.model_info else {'message': 'Nessun modello addestrato'}
            
        except Exception as e:
            self.logger.error(f"Errore nel recupero info modello: {str(e)}")
            raise
    
    def evaluate_model(self):
        """Valuta le performance del modello su nuovi dati"""
        try:
            if self.model is None:
                self._load_latest_model()
            
            if self.model is None:
                raise ValueError("Nessun modello disponibile per la valutazione")
            
            # Carica dati di test
            df = self._load_data_for_training()
            if df.empty:
                raise ValueError("Nessun dato disponibile per la valutazione")
            
            X = df[self.feature_columns]
            y = df['cnt']
            
            # Predizioni
            y_pred = self.model.predict(X)
            
            # Metriche
            mse = mean_squared_error(y, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            return {
                'evaluation_metrics': {
                    'mse': float(mse),
                    'rmse': float(rmse),
                    'mae': float(mae),
                    'r2_score': float(r2)
                },
                'data_points': len(df),
                'model_type': self.model_info.get('model_type', 'unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Errore nella valutazione del modello: {str(e)}")
            raise
    
    def _load_data_for_training(self):
        """Carica dati dal database per l'addestramento"""
        try:
            records = db.session.query(BikeRecord).all()
            if not records:
                return pd.DataFrame()
            
            data = [record.to_dict() for record in records]
            df = pd.DataFrame(data)
            
            # Rimuovi righe con valori mancanti
            df = df.dropna(subset=self.feature_columns + ['cnt'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Errore nel caricamento dati: {str(e)}")
            raise
    
    def _load_latest_model(self):
        """Carica l'ultimo modello addestrato"""
        try:
            if not os.path.exists(Config.MODEL_PATH):
                return
            
            # Cerca file di modelli
            model_files = [f for f in os.listdir(Config.MODEL_PATH) if f.endswith('_model.joblib')]
            
            if not model_files:
                return
            
            # Prendi il più recente (per ora il primo trovato)
            latest_model_file = model_files[0]
            model_path = os.path.join(Config.MODEL_PATH, latest_model_file)
            
            # Carica modello
            self.model = joblib.load(model_path)
            
            # Carica info del modello
            model_name = latest_model_file.replace('_model.joblib', '')
            info_path = os.path.join(Config.MODEL_PATH, f'{model_name}_info.joblib')
            
            if os.path.exists(info_path):
                self.model_info = joblib.load(info_path)
            
        except Exception as e:
            self.logger.error(f"Errore nel caricamento del modello: {str(e)}")
            self.model = None
            self.model_info = {}
