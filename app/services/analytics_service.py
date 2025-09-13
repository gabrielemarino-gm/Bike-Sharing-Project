import pandas as pd
from app import db
from app.models.bike_record import BikeRecord
from sqlalchemy import func
import logging

class AnalyticsService:
    """Servizio per le analisi statistiche dei dati"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_hourly_aggregations(self):
        """Statistiche aggregate per ora del giorno"""
        try:
            stats = db.session.query(
                BikeRecord.hour,
                func.avg(BikeRecord.cnt).label('avg_count'),
                func.sum(BikeRecord.cnt).label('total_count'),
                func.avg(BikeRecord.casual).label('avg_casual'),
                func.avg(BikeRecord.registered).label('avg_registered'),
                func.count(BikeRecord.id).label('records_count')
            ).group_by(BikeRecord.hour).order_by(BikeRecord.hour).all()
            
            return {
                'hourly_stats': [
                    {
                        'hour': stat.hr,
                        'average_count': round(float(stat.avg_count), 2),
                        'total_count': stat.total_count,
                        'average_casual': round(float(stat.avg_casual), 2),
                        'average_registered': round(float(stat.avg_registered), 2),
                        'records_count': stat.records_count
                    }
                    for stat in stats
                ]
            }
        except Exception as e:
            self.logger.error(f"Errore nelle statistiche orarie: {str(e)}")
            raise
    
    def get_daily_aggregations(self):
        """Statistiche aggregate per giorno della settimana"""
        try:
            stats = db.session.query(
                BikeRecord.week_day,
                func.avg(BikeRecord.cnt).label('avg_count'),
                func.sum(BikeRecord.cnt).label('total_count'),
                func.count(BikeRecord.id).label('records_count')
            ).group_by(BikeRecord.week_day).order_by(BikeRecord.week_day).all()
            
            weekday_names = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
            
            return {
                'daily_stats': [
                    {
                        'weekday': stat.weekday,
                        'weekday_name': weekday_names[stat.weekday] if stat.weekday < len(weekday_names) else f'Giorno {stat.weekday}',
                        'average_count': round(float(stat.avg_count), 2),
                        'total_count': stat.total_count,
                        'records_count': stat.records_count
                    }
                    for stat in stats
                ]
            }
        except Exception as e:
            self.logger.error(f"Errore nelle statistiche giornaliere: {str(e)}")
            raise
    
    def get_seasonal_aggregations(self):
        """Statistiche aggregate per stagione"""
        try:
            stats = db.session.query(
                BikeRecord.season,
                func.avg(BikeRecord.cnt).label('avg_count'),
                func.sum(BikeRecord.cnt).label('total_count'),
                func.avg(BikeRecord.temperature).label('avg_temp'),
                func.count(BikeRecord.id).label('records_count')
            ).group_by(BikeRecord.season).order_by(BikeRecord.season).all()
            
            season_names = {1: 'Inverno', 2: 'Primavera', 3: 'Estate', 4: 'Autunno'}
            
            return {
                'seasonal_stats': [
                    {
                        'season': stat.season,
                        'season_name': season_names.get(stat.season, f'Stagione {stat.season}'),
                        'average_count': round(float(stat.avg_count), 2),
                        'total_count': stat.total_count,
                        'average_temperature': round(float(stat.avg_temp), 3),
                        'records_count': stat.records_count
                    }
                    for stat in stats
                ]
            }
        except Exception as e:
            self.logger.error(f"Errore nelle statistiche stagionali: {str(e)}")
            raise
    
    def get_weather_aggregations(self):
        """Statistiche aggregate per condizioni meteorologiche"""
        try:
            stats = db.session.query(
                BikeRecord.weather_situa,
                func.avg(BikeRecord.cnt).label('avg_count'),
                func.sum(BikeRecord.cnt).label('total_count'),
                func.avg(BikeRecord.temperature).label('avg_temp'),
                func.avg(BikeRecord.humidity).label('avg_humidity'),
                func.avg(BikeRecord.wind_speed).label('avg_windspeed'),
                func.count(BikeRecord.id).label('records_count')
            ).group_by(BikeRecord.weather_situa).order_by(BikeRecord.weather_situa).all()
            
            weather_descriptions = {
                1: 'Sereno/Poco nuvoloso',
                2: 'Nebbia/Nuvoloso',
                3: 'Pioggia leggera/Neve',
                4: 'Pioggia forte/Temporale'
            }
            
            return {
                'weather_stats': [
                    {
                        'weather_situation': stat.weathersit,
                        'weather_description': weather_descriptions.get(stat.weathersit, f'Condizione {stat.weathersit}'),
                        'average_count': round(float(stat.avg_count), 2),
                        'total_count': stat.total_count,
                        'average_temperature': round(float(stat.avg_temp), 3),
                        'average_humidity': round(float(stat.avg_humidity), 3),
                        'average_windspeed': round(float(stat.avg_windspeed), 3),
                        'records_count': stat.records_count
                    }
                    for stat in stats
                ]
            }
        except Exception as e:
            self.logger.error(f"Errore nelle statistiche meteo: {str(e)}")
            raise
    
    def export_to_csv(self):
        """Esporta le analisi complete in formato CSV"""
        try:
            # Recupera tutti i dati
            records = db.session.query(BikeRecord).all()
            
            if not records:
                return "Nessun dato disponibile per l'esportazione"
            
            # Converti in DataFrame
            data = [record.to_dict() for record in records]
            df = pd.DataFrame(data)
            
            # Aggiungi colonne calcolate
            df['total_users'] = df['casual'] + df['registered']
            df['temp_celsius'] = df['temp'] * 41  # Denormalizza temperatura
            df['humidity_percent'] = df['hum'] * 100  # Denormalizza umidità
            df['windspeed_kmh'] = df['windspeed'] * 67  # Denormalizza velocità vento
            
            # Mappa valori categorici
            season_map = {1: 'Inverno', 2: 'Primavera', 3: 'Estate', 4: 'Autunno'}
            weather_map = {1: 'Sereno', 2: 'Nebbia', 3: 'Pioggia_leggera', 4: 'Pioggia_forte'}
            
            df['season_name'] = df['season'].map(season_map)
            df['weather_name'] = df['weathersit'].map(weather_map)
            
            # Esporta in CSV
            return df.to_csv(index=False)
            
        except Exception as e:
            self.logger.error(f"Errore nell'esportazione CSV: {str(e)}")
            raise
