"""
Modello ML per predizione dei picchi di domanda di noleggi biciclette
Tipo: Classificazione Binaria
Target: is_peak (1 se cnt > soglia, 0 altrimenti)
Features: season, yr, mnth, hr, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed
"""

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import os
import logging


class PeakDemandPredictor:
    """Predittore dei picchi di domanda"""
    
    def __init__(self, model_type='random_forest', peak_threshold_percentile=80):
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        self.peak_threshold_percentile = peak_threshold_percentile
        self.peak_threshold_value = None

        # Features usate per il training/predizione. 
        # Potrebbero essere migliorate con un lavoro di feature importance e selezione
        # Esclusi: 
        #   • 'dteday' per evitare data leakage: il giorno specifico non deve influenzare il modello, se è festivo lo indica holiday
        #   • 'casual' e 'registered' per evitare leakage da target
        #   • 'cnt' per evitare leakage da target
        self.feature_names = [
            'season', 'yr', 'mnth', 'hr', 'holiday', 'weekday', 
            'workingday', 'weathersit', 'temp', 'atemp', 'hum', 'windspeed'
        ]
        
        self.training_metrics = {}
        self.logger = logging.getLogger(__name__)
    
    def initialize_model(self):
        """Inizializza il modello ML in base al tipo scelto"""
        if self.model_type == 'logistic_regression':
            return LogisticRegression(random_state=44, max_iter=1000)
        elif self.model_type == 'decision_tree':
            return DecisionTreeClassifier(
                random_state=44, 
                max_depth=10,
                min_samples_split=10
            )
        elif self.model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=100, 
                random_state=44, 
                max_depth=10,
                min_samples_split=10,
                class_weight='balanced'
            )
        else:
            raise ValueError(f"Tipo di modello non supportato: {self.model_type}")
    
    def calculate_peak_threshold(self, cnt_values):
        """Calcola la soglia per definire un picco"""
        try:
            # Calcola percentile configurabile, settando la soglia al valore del percentile (default 80-esimo)
            threshold = np.percentile(cnt_values, self.peak_threshold_percentile) 
            
            # Calcoliamo la media per capire se la soglia ha senso
            # I picchi dovrebbero essere almeno 1.2x la media
            mean_cnt = np.mean(cnt_values)
            min_reasonable_threshold = mean_cnt * 1.2
            
            # Se la soglia è troppo bassa rispetto alla media, la settiamo a un valore ragionevole
            if threshold < min_reasonable_threshold:
                self.logger.warning(f"Soglia calcolata ({threshold:.1f}) sotto soglia ragionevole ({min_reasonable_threshold:.1f})")
                threshold = min_reasonable_threshold

            self.peak_threshold_value = threshold
            self.logger.info(f"Soglia picco calcolata: {threshold:.1f}")
            
            return threshold
            
        except Exception as e:
            self.logger.error(f"Errore nel calcolo soglia: {str(e)}")
            
            # Fallback a percentile semplice
            threshold = np.percentile(cnt_values, self.peak_threshold_percentile)
            self.peak_threshold_value = threshold

            self.logger.info(f"Soglia picco settata al {self.peak_threshold_percentile} percentile: {threshold:.1f}")
            return threshold

    def create_peak_labels(self, cnt_values):
        """Crea le etichette binary per picchi"""
        if self.peak_threshold_value is None:
            self.peak_threshold_value = self.calculate_peak_threshold(cnt_values)
        
        # Etichetto a 1 se cnt > soglia, 0 altrimenti
        peak_labels = (cnt_values > self.peak_threshold_value).astype(int)

        return peak_labels
    
    def prepare_features(self, data):
        """Prepara le features per il training/predizione"""
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
            data = training_data.copy()
            data = data.dropna()
            
            if len(data) < 100:
                raise ValueError("Dataset troppo piccolo per training")
            
            # Preparare features e creare target binary
            X = self.prepare_features(data)
            y = self.create_peak_labels(data['cnt'])
            
            self.logger.info(f"Features shape: {X.shape}, Target shape: {y.shape}")
            
            # Verificare bilanciamento classi
            peak_ratio = np.mean(y)
            self.logger.info(f"Rapporto picchi: {peak_ratio:.2%}")
            
            # Train/test split stratificato
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=44, stratify=y
            )
            
            # Inizializzare e addestrare il modello
            self.model = self.initialize_model()
            self.model.fit(X_train, y_train)
            
            # Valutazione del modello
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1] if hasattr(self.model, 'predict_proba') else y_pred
            self.training_metrics = self.calculate_metrics(y_test, y_pred, y_pred_proba)
            
            # Marcare come addestrato
            self.is_trained = True
            
            self.logger.info(f"Modello {self.model_type} addestrato con successo")
            self.logger.info(f"Accuracy: {self.training_metrics['accuracy']:.3f}")
            self.logger.info(f"F1-Score: {self.training_metrics['f1_score']:.3f}")
            
            return self.training_metrics
            
        except Exception as e:
            self.logger.error(f"Errore durante il training: {str(e)}")
            raise
    
    def predict(self, features):
        """
        Predice se ci sarà un picco di domanda
        
        Args:
            features (dict): Dizionario con features per predizione
        
        Returns:
            dict: Predizione di picco e probabilità
        """
        if not self.is_trained:
            raise ValueError("Modello non ancora addestrato")
        
        try:
            # Preparare features per predizione
            X = self.prepare_single_features(features)
            
            # Effettuare predizione
            is_peak = self.model.predict(X)[0]
            
            # Calcolare probabilità se disponibile
            if hasattr(self.model, 'predict_proba'):
                peak_probability = self.model.predict_proba(X)[0, 1]
            else:
                peak_probability = float(is_peak) # Mettere 1.0 se predetto picco, 0.0 altrimenti
            
            return {
                'is_peak': bool(is_peak),
                'peak_probability': float(peak_probability),
                'peak_threshold': self.peak_threshold_value,
                'model_type': self.model_type,
                'features_used': list(features.keys())
            }

        except Exception as e:
            self.logger.error(f"Errore durante la predizione: {str(e)}")
            raise
    
    def prepare_single_features(self, features):
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
    
    def calculate_metrics(self, y_true, y_pred, y_pred_proba):
        """Calcola metriche di valutazione per classificazione"""
        try:
            from sklearn.metrics import roc_auc_score, average_precision_score
            
            # Metriche base
            accuracy = accuracy_score(y_true, y_pred)
            precision = precision_score(y_true, y_pred, zero_division=0)
            recall = recall_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            
            # Metriche probabilistiche
            roc_auc = roc_auc_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0.5
            pr_auc = average_precision_score(y_true, y_pred_proba) if len(np.unique(y_true)) > 1 else 0.5
            
            # Confusion matrix
            cm = confusion_matrix(y_true, y_pred)
            
            return {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'roc_auc': float(roc_auc),
                'pr_auc': float(pr_auc),
                'confusion_matrix': cm.tolist(),
                'test_samples': len(y_true),
                'positive_samples': int(np.sum(y_true)),
                'negative_samples': int(len(y_true) - np.sum(y_true))
            }
            
        except Exception as e:
            self.logger.error(f"Errore nel calcolo metriche: {str(e)}")
            return {
                'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0,
                'f1_score': 0.0, 'roc_auc': 0.0, 'pr_auc': 0.0
            }
    
    def save_model(self, filename=None):
        """Salva il modello addestrato"""
        if not self.is_trained:
            raise ValueError("Nessun modello addestrato da salvare")

        try:
            # Nome file di default
            if filename is None:
                filename = f'peak_demand_predictor_{self.model_type}.joblib'

            # Percorso assoluto per salvare in /progetto/ml_models/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            models_dir = os.path.join(project_root, 'ml_models')
            filepath = os.path.join(models_dir, filename)
            
            # Crea directory se non esiste
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Salva modello e metadati
            model_data = {
                'model': self.model,
                'model_type': self.model_type,
                'feature_names': self.feature_names,
                'peak_threshold_value': self.peak_threshold_value,
                'peak_threshold_percentile': self.peak_threshold_percentile,
                'training_metrics': self.training_metrics,
                'is_trained': self.is_trained,
                'created_at': pd.Timestamp.now().isoformat()
            }
            
            # Salvare con joblib
            joblib.dump(model_data, filepath)
            self.logger.info(f"Modello picchi salvato in {filepath}")
            
        except Exception as e:
            self.logger.error(f"Errore nel salvataggio modello: {str(e)}")
            raise
    
    def load_model(self, filename=None):
        """Carica un modello pre-addestrato"""
        
        try:
            # Nome file di default
            if filename is None:
                filename = f'peak_demand_predictor_{self.model_type}.joblib'

            # Percorso assoluto per salvare in /progetto/ml_models/
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            models_dir = os.path.join(project_root, 'ml_models')
            filepath = os.path.join(models_dir, filename)
            
            # Carica modello e metadati
            model_data = joblib.load(filepath)
            
            # Verifica struttura dati
            required_keys = ['model', 'model_type', 'feature_names', 'is_trained']
            for key in required_keys:
                if key not in model_data:
                    raise ValueError(f"File modello corrotto: manca '{key}'")
            
            # Ripristina stato del modello
            self.model = model_data['model']
            self.model_type = model_data['model_type']
            self.feature_names = model_data['feature_names']
            self.peak_threshold_value = model_data['peak_threshold_value']
            self.peak_threshold_percentile = model_data['peak_threshold_percentile']
            self.training_metrics = model_data['training_metrics']
            self.is_trained = model_data['is_trained']
            
            self.logger.info(f"Modello picchi caricato da {filepath}")
            self.logger.info(f"Tipo modello: {self.model_type}, Soglia: {self.peak_threshold_value}")
            
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
            'peak_threshold_percentile': self.peak_threshold_percentile,
            'peak_threshold_value': self.peak_threshold_value,
            'training_metrics': self.training_metrics if self.is_trained else None,
            'target_variable': 'is_peak (binary classification)',
            'prediction_type': 'Peak Demand Detection'
        }
        
    def print_model_info(self):
        """Stampa informazioni sul modello"""
        info = self.get_model_info()
        print("Modello PeakDemandPredictor Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        print()
        return
