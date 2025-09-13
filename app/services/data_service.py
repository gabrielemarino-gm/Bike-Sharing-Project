import pandas as pd
import numpy as np
from app import db
from app.models.bike_record import BikeRecord
from sqlalchemy import func
import logging
import requests
import io

class DataService:
    """Servizio per la gestione dei dati"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def load_default_dataset(self):
        """Carica il dataset UCI Bike Sharing di default"""
        try:
            # URL del dataset UCI Bike Sharing (hour.csv)
            url = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"
            
            # Per questo esempio, creiamo alcuni dati di esempio
            # In produzione, scaricheresti e processeresti il file ZIP
            sample_data = self._create_sample_data()
            
            return self._load_dataframe(sample_data)
        except Exception as e:
            self.logger.error(f"Errore nel caricamento del dataset di default: {str(e)}")
            raise
    
    def load_from_file(self, file):
        """Carica dati da file CSV caricato"""
        try:
            # Leggi il file CSV
            df = pd.read_csv(file)
            return self._load_dataframe(df)
        except Exception as e:
            self.logger.error(f"Errore nel caricamento da file: {str(e)}")
            raise
    
    def load_from_url(self, url):
        """Carica dati da URL"""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            df = pd.read_csv(io.StringIO(response.text))
            return self._load_dataframe(df)
        except Exception as e:
            self.logger.error(f"Errore nel caricamento da URL: {str(e)}")
            raise
    
    def _load_dataframe(self, df):
        """Carica un DataFrame nel database"""
        try:
            # Pulisci i dati esistenti
            db.session.query(BikeRecord).delete()
            
            records_loaded = 0
            for _, row in df.iterrows():
                record = BikeRecord(
                    instant=row.get('instant'),
                    dteday=pd.to_datetime(row.get('dteday')).date() if pd.notna(row.get('dteday')) else None,
                    season=row.get('season'),
                    yr=row.get('yr'),
                    mnth=row.get('mnth'),
                    hr=row.get('hr'),
                    holiday=row.get('holiday'),
                    weekday=row.get('weekday'),
                    workingday=row.get('workingday'),
                    weathersit=row.get('weathersit'),
                    temp=row.get('temp'),
                    atemp=row.get('atemp'),
                    hum=row.get('hum'),
                    windspeed=row.get('windspeed'),
                    casual=row.get('casual'),
                    registered=row.get('registered'),
                    cnt=row.get('cnt')
                )
                db.session.add(record)
                records_loaded += 1
            
            db.session.commit()
            
            return {
                'message': 'Dataset caricato con successo',
                'records_loaded': records_loaded,
                'columns': list(df.columns)
            }
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Errore nel caricamento del DataFrame: {str(e)}")
            raise
    
    def get_dataset_status(self):
        """Restituisce informazioni sui dati caricati"""
        try:
            total_records = db.session.query(BikeRecord).count()
            
            if total_records == 0:
                return {
                    'total_records': 0,
                    'message': 'Nessun dato caricato'
                }
            
            # Statistiche di base
            stats = db.session.query(
                func.min(BikeRecord.dteday).label('start_date'),
                func.max(BikeRecord.dteday).label('end_date'),
                func.avg(BikeRecord.cnt).label('avg_count'),
                func.min(BikeRecord.cnt).label('min_count'),
                func.max(BikeRecord.cnt).label('max_count')
            ).first()
            
            return {
                'total_records': total_records,
                'date_range': {
                    'start': stats.start_date.isoformat() if stats.start_date else None,
                    'end': stats.end_date.isoformat() if stats.end_date else None
                },
                'count_statistics': {
                    'average': round(float(stats.avg_count), 2) if stats.avg_count else 0,
                    'minimum': stats.min_count,
                    'maximum': stats.max_count
                }
            }
        except Exception as e:
            self.logger.error(f"Errore nel recupero dello status: {str(e)}")
            raise
    
    def get_sample_data(self, limit=10):
        """Restituisce un campione dei dati"""
        try:
            records = db.session.query(BikeRecord).limit(limit).all()
            return {
                'sample_data': [record.to_dict() for record in records],
                'count': len(records)
            }
        except Exception as e:
            self.logger.error(f"Errore nel recupero del campione: {str(e)}")
            raise
    
    def _create_sample_data(self):
        """Crea dati di esempio per il testing"""
        np.random.seed(42)
        
        # Crea 1000 record di esempio
        n_records = 1000
        data = {
            'instant': range(n_records),
            'dteday': pd.date_range('2011-01-01', periods=n_records//24, freq='D').repeat(24)[:n_records],
            'season': np.random.randint(1, 5, n_records),
            'yr': np.random.randint(0, 2, n_records),
            'mnth': np.random.randint(1, 13, n_records),
            'hr': np.tile(range(24), n_records//24 + 1)[:n_records],
            'holiday': np.random.randint(0, 2, n_records),
            'weekday': np.random.randint(0, 7, n_records),
            'workingday': np.random.randint(0, 2, n_records),
            'weathersit': np.random.randint(1, 4, n_records),
            'temp': np.random.uniform(0, 1, n_records),
            'atemp': np.random.uniform(0, 1, n_records),
            'hum': np.random.uniform(0, 1, n_records),
            'windspeed': np.random.uniform(0, 1, n_records),
            'casual': np.random.randint(0, 100, n_records),
            'registered': np.random.randint(0, 500, n_records),
            'cnt': np.random.randint(1, 600, n_records)
        }
        
        return pd.DataFrame(data)
