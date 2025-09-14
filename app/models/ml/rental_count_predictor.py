"""
Modello ML per predizione del numero totale di noleggi biciclette
Tipo: Regressione
Target: cnt (count totale)
Features: season, yr, mnth, hr, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import cross_val_score, KFold
import os
import logging

class RentalCountPredictor:
    """Predittore del numero totale di noleggi"""
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.is_trained = False

        # Features usate per il training/predizione. 
        # Potrebbero essere migliorate con un lavoro di feature importance e selezione
        # Esclusi: 
        #   'dteday' per evitare data leakage: il giorno specifico non deve influenzare il modello, se è festivo lo indica holiday
        #   'casual' e 'registered' per evitare leakage da target
        #   'cnt' per evitare leakage da target
        self.feature_names = [
            'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
            'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed'
        ]
        
        self.training_metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def initialize_model(self):
        """Inizializza il modello ML in base al tipo scelto"""
        if self.model_type == 'linear_regression':
            return LinearRegression()
        elif self.model_type == 'decision_tree':
            return DecisionTreeRegressor(random_state=44, max_depth=15)
        elif self.model_type == 'random_forest':
            return RandomForestRegressor(
                n_estimators=100, 
                random_state=44, 
                max_depth=15,
                min_samples_split=5
            )
        else:
            raise ValueError(f"Tipo di modello non supportato: {self.model_type}")
    
    def prepare_features(self, data):
        """Prepara le features per il training/predizione, eliminando 
        eventuali colonne non necessarie.
        
         Args:
            data (dict or pd.DataFrame): Dati di input
            
        Returns:
            pd.DataFrame: DataFrame con solo le features richieste
        """
        if isinstance(data, dict):
            # Singola predizione
            return pd.DataFrame([data])[self.feature_names]
        elif isinstance(data, pd.DataFrame):
            # Dataset completo
            return data[self.feature_names]
        else:
            raise ValueError("Data deve essere dict o DataFrame")
    
    def train(self, training_data):
        """
        Addestra il modello sui dati di training
        
        Args:
            training_data (pd.DataFrame): Dataset con features e target 'cnt'
            
        Returns:
            dict: Metriche di training
        """
        try:
            # Preprocessing dei dati
            # Gestione valori mancanti
            data = training_data.copy()
            
            # Rimuovi righe con NaN
            data = data.dropna() 
            self.logger.info(f"Dati dopo pulizia: {len(data)} record")
            
            # Preparare features e target
            X = self.prepare_features(data)
            y = data['cnt']

            self.logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=44, shuffle=True
            )
            
            # Inizializzare e addestrare il modello
            self.model = self.initialize_model()
            self.model.fit(X_train, y_train)
            
            # Valutazione del modello
            y_pred = self.model.predict(X_test)
            self.training_metrics = self.calculate_metrics(y_test, y_pred, X_test, X_train, y_train)
            
            # Marcare come addestrato
            self.is_trained = True
            
            self.logger.info(f"Modello {self.model_type} addestrato con successo")
            self.logger.info(f"R² Score: {self.training_metrics['r2_score']:.3f}")
            self.logger.info(f"RMSE: {self.training_metrics['rmse']:.2f}")
            
            return self.training_metrics
            
        except Exception as e:
            self.logger.error(f"Errore durante il training: {str(e)}")
            raise
    
    def predict(self, features):
        """
        Effettua predizione del numero di noleggi
        
        Args:
            features (dict): Dizionario con features per predizione
            
        Returns:
            dict: Predizione e confidence score
        """
        if not self.is_trained:
            raise ValueError("Modello non ancora addestrato")
        
        try:
            # Preparare features per predizione
            X = self.prepare_features_single(features)
            
            # Effettuare predizione
            prediction = self.model.predict(X)[0] # [0] per ottenere valore scalare
            prediction = max(0, int(round(prediction)))  # Non può essere negativo
            
            return {
                'predicted_rentals': prediction,
                'model_type': self.model_type,
                'features_used': list(features.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Errore durante la predizione: {str(e)}")
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
        for feature in self.feature_names:
            if feature in features:
                feature_values.append(features[feature])
            else:
                # TODO: Forse meglio lanciare errore se mancano features
                # raise ValueError(f"Feature mancante: {feature_name}")
                self.logger.warning(f"Feature mancante: {feature}, uso valore di default 0")
                feature_values.append(0)  # Valore di default se mancante
        
        return np.array(feature_values).reshape(1, -1) # Array 2D
    
    
    def calculate_metrics(self, y_true, y_pred, X_test=None, X_train=None, y_train=None):
        """
        Calcola metriche di valutazione per regressione
        
        Args:
            y_true (array-like): Valori reali del test set
            y_pred (array-like): Valori predetti del test set
            X_test (array-like, optional): Features del test set per CV
            X_train (array-like, optional): Features del train set per CV
            y_train (array-like, optional): Target del train set per CV
            
        Returns:
            dict: Metriche complete di valutazione
        """
        # Metriche base sui dati di test
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # MAPE (gestisce divisione per zero)
        mask = y_true != 0
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.any() else 0.0
        
        metrics = {
            'rmse': float(rmse),
            'mae': float(mae), 
            'r2_score': float(r2),
            'mape': float(mape),
            'test_samples': len(y_true)
        }
        
        # Cross-validation se abbiamo i dati di training
        if X_train is not None and y_train is not None:
            try:
                # Combina train e test per la cross-validation
                X_full = np.vstack([X_train, X_test]) if X_test is not None else X_train
                y_full = np.concatenate([y_train, y_true]) if X_test is not None else y_train
                
                # K-Fold CV
                kfold = KFold(n_splits=10, shuffle=True, random_state=44)
                
                # CV scores per diverse metriche
                cv_rmse_scores = -cross_val_score(self.model, X_full, y_full, cv=kfold, scoring='neg_mean_squared_error') 
                cv_rmse_scores = np.sqrt(cv_rmse_scores)
                
                cv_mae_scores = -cross_val_score(self.model, X_full, y_full, cv=kfold, scoring='neg_mean_absolute_error')
                cv_r2_scores = cross_val_score(self.model, X_full, y_full, cv=kfold, scoring='r2')
                
                metrics.update({
                    'cv_rmse_mean': float(cv_rmse_scores.mean()),
                    'cv_rmse_std': float(cv_rmse_scores.std()),
                    'cv_mae_mean': float(cv_mae_scores.mean()),
                    'cv_mae_std': float(cv_mae_scores.std()),
                    'cv_r2_mean': float(cv_r2_scores.mean()),
                    'cv_r2_std': float(cv_r2_scores.std()),
                    'cv_folds': len(cv_rmse_scores)
                })
                
            except Exception as e:
                self.logger.warning(f"Cross-validation fallita: {str(e)}")
        
        return metrics
    
    def save_model(self, filename=None):
        """Salva il modello addestrato"""
        if not self.is_trained:
            raise ValueError("Nessun modello addestrato da salvare")

        try:
            # Nome file di default
            if filename is None:
                filename = f'rental_count_predictor_{self.model_type}.joblib'

            # Percorso assoluto per salvare in /progetto/ml_models/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            models_dir = os.path.join(project_root, 'ml_models')
            filepath = os.path.join(models_dir, filename)

            # Creare directory se non esiste
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Preparare dati da salvare
            model_data = {
                'model': self.model,
                'model_type': self.model_type,
                'feature_names': self.feature_names,
                'training_metrics': self.training_metrics,
                'is_trained': self.is_trained,
                'created_at': pd.Timestamp.now().isoformat()
            }

            # Salvare con joblib
            joblib.dump(model_data, filepath)
            self.logger.info(f"Modello salvato in {filepath}")
            
            
        except Exception as e:
            self.logger.error(f"Errore nel salvataggio modello: {str(e)}")
            raise
    
    def load_model(self, filename=None):
        """Carica un modello pre-addestrato"""
        
        try:
            # Nome file di default
            if filename is None:
                filename = f'rental_count_predictor_{self.model_type}.joblib'

            # Percorso assoluto per salvare in /progetto/ml_models/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            models_dir = os.path.join(project_root, 'ml_models')
            filepath = os.path.join(models_dir, filename)
            
            # Caricare dati del modello
            model_data = joblib.load(filepath)
            
            # Verificare struttura dati
            required_keys = ['model', 'model_type', 'feature_names', 'is_trained']
            for key in required_keys:
                if key not in model_data:
                    raise ValueError(f"File modello corrotto: manca '{key}'")
            
            # Ripristinare stato del modello
            self.model = model_data['model']
            self.model_type = model_data['model_type']
            self.feature_names = model_data['feature_names']
            self.training_metrics = model_data.get('training_metrics', {})
            self.is_trained = model_data['is_trained']

            self.logger.info(f"Modello predittivo caricato da {filepath}")
            self.logger.info(f"Tipo modello: {self.model_type}")
            
            if self.training_metrics:
                r2 = self.training_metrics.get('r2_score', 'N/A')
                rmse = self.training_metrics.get('rmse', 'N/A')
                self.logger.info(f"Performance: R²={r2}, RMSE={rmse}")
            
        except Exception as e:
            self.logger.error(f"Errore nel caricamento modello: {str(e)}")
            raise
    
    def get_model_info(self):
        """Restituisce informazioni sul modello"""
        return {
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'feature_count': len(self.feature_names),
            'features': self.feature_names,
            'training_metrics': self.training_metrics if self.is_trained else None,
            'target_variable': 'cnt (total rental count)',
            'prediction_type': 'Total rental count (regression)',
        }

    def print_model_info(self):
        """Stampa informazioni sul modello"""
        info = self.get_model_info()
        print("Modello RentalCountPredictor Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
        return