from app import db
from datetime import datetime

class BikeRecord(db.Model):
    """Model per i dati di bike sharing"""
    __tablename__ = 'bike_records'
    
    id = db.Column(db.Integer, primary_key=True)
    instant = db.Column(db.Integer)         # record index
    dteday = db.Column(db.Date)             # date
    season = db.Column(db.Integer)          # season (1:winter, 2:spring, 3:summer, 4:fall)
    year = db.Column(db.Integer)            # year (0: 2011, 1:2012)
    month = db.Column(db.Integer)           # month (1 to 12)
    hour = db.Column(db.Integer)            # hour (0 to 23)
    holi_day = db.Column(db.Integer)        # whether day is holiday or not
    week_day = db.Column(db.Integer)        # day of the week
    working_day = db.Column(db.Integer)     # if day is neither weekend nor holiday
    weather_situa = db.Column(db.Integer)   # weather situation
    temperature = db.Column(db.Float)       # normalized temperature in Celsius
    feeling_temp = db.Column(db.Float)      # normalized feeling temperature in Celsius
    humidity = db.Column(db.Float)          # normalized humidity
    wind_speed = db.Column(db.Float)        # normalized wind speed
    casual = db.Column(db.Integer)          # count of casual users
    registered = db.Column(db.Integer)      # count of registered users
    cnt = db.Column(db.Integer)             # count of total rental bikes

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BikeRecord {self.dteday} Hr:{self.hour} Count:{self.cnt}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'instant': self.instant,
            'dteday': self.dteday.isoformat() if self.dteday else None,
            'season': self.season,
            'yr': self.year,
            'mnth': self.month,
            'hr': self.hour,
            'holiday': self.holi_day,
            'weekday': self.week_day,
            'workingday': self.working_day,
            'weathersit': self.weather_situa,
            'temp': self.temperature,
            'atemp': self.feeling_temp,
            'hum': self.humidity,
            'windspeed': self.wind_speed,
            'casual': self.casual,
            'registered': self.registered,
            'cnt': self.cnt,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
