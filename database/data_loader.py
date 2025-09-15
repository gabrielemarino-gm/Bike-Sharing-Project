"""
Caricamento dati nel database
"""
import pandas as pd
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from . import db, BikeRecord 

class BikeDataLoader:
    """Gestisce il caricamento dei dati nella tabella unificata"""
    
    def __init__(self):
        self.total_records = 0
        self.success_count = 0
        self.error_count = 0
    
    def load_from_file_object(self, file_obj, batch_size=1000):
        """
        Carica i dati da un file object (per upload Flask)
        
        Args:
            file_obj: File object da Flask request.files
            batch_size: Numero di record per batch
        """
        print(f"📊 Inizio caricamento dati da file upload: {file_obj.filename}")
        
        try:
            # Leggi CSV direttamente dal file object
            df = pd.read_csv(file_obj)
            self.total_records = len(df)
            print(f"📈 Record trovati: {self.total_records}")
            
            # Pulisci tabella esistente
            self._clear_existing_data()
            
            # Carica dati in batch
            self._load_in_batches(df, batch_size)

            print(f"📊 Caricamento completato: {self.success_count} successi, {self.error_count} errori")

        except Exception as e:
            print(f"❌ Errore durante il caricamento: {str(e)}")
            raise
        
    def download_data_in_dataframe():
        """Scarica dati dal database per l'addestramento
        Returns:
            DataFrame con i dati"""
        try:
            records = BikeRecord.query.all()
            data = [r.__dict__ for r in records]
            df = pd.DataFrame(data)
            return df
        except Exception as e:
            print(f"❌ Errore nel download dati: {str(e)}")
            raise
    
    def _clear_existing_data(self):
        """Pulisce i dati esistenti"""
        try:
            deleted = BikeRecord.query.delete()
            db.session.commit()
            print(f"🧹 Rimossi {deleted} record esistenti")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ Errore nella pulizia: {str(e)}")
    
    def _load_in_batches(self, df, batch_size):
        """Carica i dati in batch
        Args:
            df: DataFrame con i dati da caricare
            batch_size: Numero di record per batch"""
           
        # Processa ogni batch
        for i in range(0, len(df), batch_size):
            
            # Prendo il batch corrente
            batch = df.iloc[i:i+batch_size]

            # Processa il batch
            self._process_batch(batch, i)
    
    def _process_batch(self, batch, start_index):
        """Processa un singolo batch
        
        Args:
            batch: DataFrame con il batch di dati
            start_index: Indice di partenza del batch nel DataFrame originale
        """
        try:
            records = []
            
            # Crea record per ogni riga
            for _, row in batch.iterrows():
                record = self._create_bike_record(row)

                # Se il record è valido, aggiungilo alla lista, altrimenti ignora
                if record:
                    records.append(record)
            
            # Salva batch
            db.session.add_all(records)
            db.session.commit()
            self.success_count += len(records)
            
            print(f"✅ Batch {start_index//1000 + 1}: {len(records)} record salvati")
            
        except IntegrityError as e:
            # Rollback in caso di errore di integrità
            db.session.rollback()
            self.error_count += len(batch)
            print(f"❌ Errore di integrità nel batch {start_index//1000 + 1}: {str(e)}")
        except Exception as e:
            # Rollback in caso di errore generico
            db.session.rollback()
            self.error_count += len(batch)
            print(f"❌ Errore nel batch {start_index//1000 + 1}: {str(e)}")
    
    def _create_bike_record(self, row):
        """Crea un record BikeRecord dai dati CSV
        
        Args:
            row: Riga del DataFrame con i dati
        Returns:
            BikeRecord o None se errore
        """
        try:
            # Parsing della data
            date_str = str(row['dteday'])
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Crea il record
            return BikeRecord(
                instant=int(row['instant']),
                dteday=date_obj,
                season=int(row['season']),
                yr=int(row['yr']),
                mnth=int(row['mnth']),
                hr=int(row['hr']),
                holiday=bool(int(row['holiday'])),
                weekday=int(row['weekday']),
                workingday=bool(int(row['workingday'])),
                weathersit=int(row['weathersit']),
                temp=float(row['temp']),
                atemp=float(row['atemp']),
                hum=float(row['hum']),
                windspeed=float(row['windspeed']),
                casual=int(row['casual']),
                registered=int(row['registered']),
                cnt=int(row['cnt'])
            )
        except (ValueError, KeyError) as e:
            print(f"⚠️ Errore parsing riga {row['instant']}: {str(e)}")
            return None

    def get_stats(self):
        """Restituisce statistiche del database"""
        total = BikeRecord.query.count()
        
        stats = {
            'total_records': total,
            'date_range': self.get_date_range(),
            'weather_distribution': self.get_weather_distribution(),
            'seasonal_distribution': self.get_seasonal_distribution()
        }
        
        return stats
    
    def get_date_range(self):
        """Ottieni range di date nel database"""
        min_date = db.session.query(db.func.min(BikeRecord.dteday)).scalar()
        max_date = db.session.query(db.func.max(BikeRecord.dteday)).scalar()
        
        return {
            'min_date': min_date.isoformat() if min_date else None,
            'max_date': max_date.isoformat() if max_date else None
        }
    
    def get_weather_distribution(self):
        """Distribuzione condizioni meteo"""
        weather_counts = (db.session.query(BikeRecord.weathersit, db.func.count())
                         .group_by(BikeRecord.weathersit)
                         .all())
        
        return {f'weather_{w}': count for w, count in weather_counts}
    
    def get_seasonal_distribution(self):
        """Distribuzione stagionale"""
        season_counts = (db.session.query(BikeRecord.season, db.func.count())
                        .group_by(BikeRecord.season)
                        .all())
        
        return {f'season_{s}': count for s, count in season_counts}
