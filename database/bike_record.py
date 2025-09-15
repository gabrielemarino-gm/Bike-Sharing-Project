from database import db
from datetime import datetime

class BikeRecord(db.Model):
    """
    Modello del dataset UCI Bike Sharing Dataset
    """
    __tablename__ = 'bike_records'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # === IDENTIFICATORI RECORD ===
    instant = db.Column(db.Integer, unique=True, nullable=False, index=True)  # record index
    dteday = db.Column(db.Date, nullable=False, index=True)                   # date
    
    # === CONTESTO TEMPORALE ===
    season = db.Column(db.Integer, nullable=False)        # 1:spring, 2:summer, 3:fall, 4:winter
    yr = db.Column(db.Integer, nullable=False)            # 0: 2011, 1:2012
    mnth = db.Column(db.Integer, nullable=False)          # 1 to 12
    hr = db.Column(db.Integer, nullable=False)            # 0 to 23
    
    # === CONTESTO SOCIALE/LAVORATIVO ===
    holiday = db.Column(db.Integer, nullable=False)       # 0/1 - holiday or not
    weekday = db.Column(db.Integer, nullable=False)       # day of the week (0-6)
    workingday = db.Column(db.Integer, nullable=False)    # 0/1 - working day or not
    
    # === CONDIZIONI METEOROLOGICHE ===
    weathersit = db.Column(db.Integer, nullable=False)    # 1-4 weather situation
    temp = db.Column(db.Float, nullable=False)            # Normalized temperature (0-1)
    atemp = db.Column(db.Float, nullable=False)           # Normalized feeling temperature (0-1)
    hum = db.Column(db.Float, nullable=False)             # Normalized humidity (0-1)
    windspeed = db.Column(db.Float, nullable=False)       # Normalized wind speed (0-1)
    
    # === CONTEGGI UTILIZZO ===
    casual = db.Column(db.Integer, nullable=False, default=0)      # casual users count
    registered = db.Column(db.Integer, nullable=False, default=0)  # registered users count
    cnt = db.Column(db.Integer, nullable=False, default=0)         # total rental bikes
    
    def __repr__(self):
        return f'<BikeRecord #{self.instant} {self.dteday} H:{self.hr} Count:{self.cnt}>'
    
    def to_dict(self, include_metadata=False):
        """Converte in dizionario - compatibile con formato dataset originale"""
        result = {
            # Dataset fields (exact match)
            'instant': self.instant,
            'dteday': self.dteday.isoformat() if self.dteday else None,
            'season': self.season,
            'yr': self.yr,
            'mnth': self.mnth,
            'hr': self.hr,
            'holiday': self.holiday,
            'weekday': self.weekday,
            'workingday': self.workingday,
            'weathersit': self.weathersit,
            'temp': self.temp,
            'atemp': self.atemp,
            'hum': self.hum,
            'windspeed': self.windspeed,
            'casual': self.casual,
            'registered': self.registered,
            'cnt': self.cnt
        }
        
        return result
    
    # === PROPERTY PER CONVERSIONI ===
    
    @property
    def temperature_celsius(self):
        """Temperatura in Celsius denormalizzata"""
        # temp è normalizzata dividendo per 41 (max)
        return self.temp * 41
    
    @property
    def feeling_temperature_celsius(self):
        """Temperatura percepita in Celsius denormalizzata"""
        # atemp è normalizzata dividendo per 50 (max)
        return self.atemp * 50
    
    @property
    def humidity_percentage(self):
        """Umidità in percentuale denormalizzata"""
        # hum è normalizzata dividendo per 100
        return self.hum * 100
    
    @property
    def windspeed_original(self):
        """Velocità vento denormalizzata"""
        # windspeed è normalizzata dividendo per 67 (max)
        return self.windspeed * 67
    
    @property
    def season_name(self):
        """Nome stagione leggibile"""
        seasons = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
        return seasons.get(self.season, 'Unknown')
    
    @property
    def weather_description(self):
        """Descrizione condizioni meteo"""
        descriptions = {
            1: 'Clear, Few clouds, Partly cloudy',
            2: 'Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist',
            3: 'Light Snow, Light Rain + Thunderstorm + Scattered clouds',
            4: 'Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog'
        }
        return descriptions.get(self.weathersit, 'Unknown')
    
    @property
    def weekday_name(self):
        """Nome giorno settimana"""
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        return weekdays[self.weekday] if 0 <= self.weekday <= 6 else 'Unknown'
    
    @property
    def is_weekend(self):
        """Verifica se è weekend"""
        return self.weekday in [0, 6]  # Sunday, Saturday
    
    @property
    def casual_percentage(self):
        """Percentuale utenti casuali"""
        return (self.casual / self.cnt * 100) if self.cnt > 0 else 0
    
    @property
    def registered_percentage(self):
        """Percentuale utenti registrati"""
        return (self.registered / self.cnt * 100) if self.cnt > 0 else 0
    
    # === METODI DI CLASSE ===
    @classmethod
    def create_from_csv_row(cls, row):
        """Factory method per creare record da riga CSV
        
        Args:
            row: Riga pandas Series o dict con i dati del dataset
            
        Returns:
            BikeRecord: Nuova istanza del record
        """
        return cls(
            instant=int(row['instant']),
            dteday=row['dteday'] if isinstance(row['dteday'], str) 
                  else row['dteday'].date() if hasattr(row['dteday'], 'date') 
                  else row['dteday'],
            season=int(row['season']),
            yr=int(row['yr']),
            mnth=int(row['mnth']),
            hr=int(row['hr']),
            holiday=int(row['holiday']),
            weekday=int(row['weekday']),
            workingday=int(row['workingday']),
            weathersit=int(row['weathersit']),
            temp=float(row['temp']),
            atemp=float(row['atemp']),
            hum=float(row['hum']),
            windspeed=float(row['windspeed']),
            casual=int(row['casual']),
            registered=int(row['registered']),
            cnt=int(row['cnt'])
        )
    
    @classmethod
    def get_hourly_patterns(cls):
        """Pattern utilizzo orari"""
        from sqlalchemy import func
        return db.session.query(
            cls.hr,
            func.avg(cls.cnt).label('avg_count'),
            func.max(cls.cnt).label('max_count'),
            func.min(cls.cnt).label('min_count'),
            func.count(cls.id).label('sample_count')
        ).group_by(cls.hr).order_by(cls.hr).all()
    
    @classmethod
    def get_seasonal_trends(cls):
        """Trend stagionali"""
        from sqlalchemy import func
        return db.session.query(
            cls.season,
            cls.mnth,
            func.avg(cls.cnt).label('avg_count'),
            func.sum(cls.cnt).label('total_count')
        ).group_by(cls.season, cls.mnth).order_by(cls.season, cls.mnth).all()
    
    @classmethod
    def get_weather_impact(cls):
        """Impatto condizioni meteo"""
        from sqlalchemy import func
        return db.session.query(
            cls.weathersit,
            func.avg(cls.cnt).label('avg_count'),
            func.avg(cls.temp).label('avg_temp'),
            func.avg(cls.hum).label('avg_humidity'),
            func.count(cls.id).label('sample_count')
        ).group_by(cls.weathersit).all()
    
    @classmethod
    def get_user_type_analysis(cls):
        """Analisi tipi utenti"""
        from sqlalchemy import func
        return db.session.query(
            cls.hr,
            cls.weekday,
            func.avg(cls.casual).label('avg_casual'),
            func.avg(cls.registered).label('avg_registered'),
            func.avg(cls.cnt).label('avg_total')
        ).group_by(cls.hr, cls.weekday).all()
    
    @classmethod 
    def get_dataset_statistics(cls):
        """Statistiche dataset complete"""
        from sqlalchemy import func
        
        stats = db.session.query(
            func.count(cls.id).label('total_records'),
            func.min(cls.dteday).label('start_date'),
            func.max(cls.dteday).label('end_date'),
            func.avg(cls.cnt).label('avg_usage'),
            func.max(cls.cnt).label('max_usage'),
            func.min(cls.cnt).label('min_usage'),
            func.sum(cls.cnt).label('total_usage'),
            func.sum(cls.casual).label('total_casual'),
            func.sum(cls.registered).label('total_registered')
        ).first()
        
        return {
            'total_records': stats.total_records,
            'date_range': {
                'start': stats.start_date.isoformat() if stats.start_date else None,
                'end': stats.end_date.isoformat() if stats.end_date else None
            },
            'usage_stats': {
                'average': float(stats.avg_usage) if stats.avg_usage else 0,
                'maximum': stats.max_usage or 0,
                'minimum': stats.min_usage or 0,
                'total': stats.total_usage or 0
            },
            'user_types': {
                'total_casual': stats.total_casual or 0,
                'total_registered': stats.total_registered or 0,
                'casual_percentage': (stats.total_casual / stats.total_usage * 100) if stats.total_usage else 0,
                'registered_percentage': (stats.total_registered / stats.total_usage * 100) if stats.total_usage else 0
            }
        }
