"""Modulo per analisi dati noleggio bici"""

from . import db, BikeRecord
from sqlalchemy import func, case
import logging

class BikeAnalytics:
    
    def get_hourly_rental_patterns(self):
        """Calcola pattern orari di noleggio con statistiche dettagliate"""
        try:
            # Query per aggregazione per ora
            hourly_data = db.session.query(
                BikeRecord.hr.label('hour'),
                func.avg(BikeRecord.cnt).label('avg_rentals'),
                func.max(BikeRecord.cnt).label('max_rentals'),
                func.min(BikeRecord.cnt).label('min_rentals'),
                func.count(BikeRecord.id).label('sample_count'),
                func.sum(BikeRecord.cnt).label('total_rentals')
            ).group_by(BikeRecord.hr).order_by(BikeRecord.hr).all()
            
            if not hourly_data:
                return None
            
            return self._process_hourly_data(hourly_data)
            
        except Exception as e:
            logging.error(f"Errore nel recupero pattern orari: {str(e)}")
            raise
    
    def get_weekday_weekend_comparison(self):
        """Confronta noleggi tra giorni lavorativi e weekend"""
        try:
            # Query principale per weekday vs weekend
            weekday_weekend_data = db.session.query(
                case(
                    (BikeRecord.weekday.in_([0, 6]), 'Weekend'),
                    else_='Weekday'
                ).label('day_type'),
                func.avg(BikeRecord.cnt).label('avg_rentals'),  # Media noleggi
                func.max(BikeRecord.cnt).label('max_rentals'),  # Max noleggi
                func.min(BikeRecord.cnt).label('min_rentals'),  # Min noleggi
                func.count(BikeRecord.id).label('sample_count'),# Conteggio campioni
                func.sum(BikeRecord.cnt).label('total_rentals'),# Totale noleggi
            ).group_by(
                case(
                    (BikeRecord.weekday.in_([0, 6]), 'Weekend'),
                    else_='Weekday'
                )
            ).all()
            
            # Query dettagliata per giorno
            daily_breakdown = db.session.query(
                BikeRecord.weekday.label('weekday'),
                func.avg(BikeRecord.cnt).label('avg_rentals'),
                func.count(BikeRecord.id).label('sample_count')
            ).group_by(BikeRecord.weekday).order_by(BikeRecord.weekday).all()
            
            if not weekday_weekend_data or not daily_breakdown:
                return None
                
            return self._process_weekday_data(weekday_weekend_data, daily_breakdown)
            
        except Exception as e:
            logging.error(f"Errore nel confronto weekday vs weekend: {str(e)}")
            raise
    
    def get_weather_impact_analysis(self):
        """Analizza impatto condizioni meteo sui noleggi"""
        try:
            # Query condizioni meteo
            weather_impact_data = db.session.query(
                BikeRecord.weathersit.label('weather_condition'),
                func.avg(BikeRecord.cnt).label('avg_rentals'),
                func.max(BikeRecord.cnt).label('max_rentals'),
                func.min(BikeRecord.cnt).label('min_rentals'),
                func.count(BikeRecord.id).label('sample_count'),
                func.sum(BikeRecord.cnt).label('total_rentals'),
                func.avg(BikeRecord.temp).label('avg_temp'),
                func.avg(BikeRecord.hum).label('avg_humidity'),
                func.avg(BikeRecord.windspeed).label('avg_windspeed')
            ).group_by(BikeRecord.weathersit).order_by(BikeRecord.weathersit).all()
            
            # Query correlazione temperatura
            temp_correlation = db.session.query(
                case(
                    (BikeRecord.temp < 0.3, 'Freddo'),
                    (BikeRecord.temp < 0.7, 'Mite'),
                    else_='Caldo'
                ).label('temp_category'),
                func.avg(BikeRecord.cnt).label('avg_rentals'),
                func.count(BikeRecord.id).label('sample_count')
            ).group_by(
                case(
                    (BikeRecord.temp < 0.3, 'Freddo'),
                    (BikeRecord.temp < 0.7, 'Mite'),
                    else_='Caldo'
                )
            ).all()
            
            if not weather_impact_data:
                return None
                
            return self._process_weather_data(weather_impact_data, temp_correlation)
            
        except Exception as e:
            logging.error(f"Errore nell'analisi meteo: {str(e)}")
            raise
    
    def _process_hourly_data(self, hourly_data):
        """Processa dati orari e calcola statistiche"""
        hourly_patterns = []
        peak_hour = None
        low_hour = None
        
        for row in hourly_data:
            hour_stats = {
                'hour': row.hour,
                'avg_rentals': round(row.avg_rentals, 2),
                'max_rentals': row.max_rentals,
                'min_rentals': row.min_rentals,
                'total_rentals': row.total_rentals,
                'sample_count': row.sample_count
            }
            hourly_patterns.append(hour_stats)
            
            if peak_hour is None or hour_stats['avg_rentals'] > peak_hour['avg_rentals']:
                peak_hour = hour_stats
            if low_hour is None or hour_stats['avg_rentals'] < low_hour['avg_rentals']:
                low_hour = hour_stats
        
        # Calcola soglie e pattern
        total_avg = sum(h['avg_rentals'] for h in hourly_patterns) / len(hourly_patterns)
        threshold = total_avg * 1.5
        low_threshold = total_avg * 0.5
        
        peak_hours = [h['hour'] for h in hourly_patterns if h['avg_rentals'] >= threshold]
        low_hours = [h['hour'] for h in hourly_patterns if h['avg_rentals'] <= low_threshold]
        
        return {
            'hourly_patterns': hourly_patterns,
            'summary': {
                'overall_avg': round(total_avg, 2),
                'peak_hour': peak_hour,
                'low_hour': low_hour,
                'peak_hours': peak_hours,
                'low_hours': low_hours,
                'total_hours_analyzed': len(hourly_patterns)
            }
        }
    
    def _process_weekday_data(self, weekday_weekend_data, daily_breakdown):
        """Processa dati weekday vs weekend"""
        day_names = {
            0: 'DOM', 1: 'LUN', 2: 'MAR', 3: 'MER',
            4: 'GIO', 5: 'VEN', 6: 'SAB'
        }
        
        # Processa dati principali
        comparison_data = {}
        for row in weekday_weekend_data:
            comparison_data[row.day_type] = {
                'avg_rentals': round(row.avg_rentals, 2),
                'max_rentals': row.max_rentals,
                'min_rentals': row.min_rentals,
                'total_rentals': row.total_rentals,
                'sample_count': row.sample_count,
            }
        
        # Processa breakdown giornaliero
        daily_stats = []
        for row in daily_breakdown:
            daily_stats.append({
                'weekday': row.weekday,
                'day_name': day_names[row.weekday],
                'day_type': 'Weekend' if row.weekday in [0, 6] else 'Weekday',
                'avg_rentals': round(row.avg_rentals, 2),
                'sample_count': row.sample_count
            })
        
        # Calcola statistiche
        weekday_avg = comparison_data.get('Weekday', {}).get('avg_rentals', 0)
        weekend_avg = comparison_data.get('Weekend', {}).get('avg_rentals', 0)
        
        percentage_difference = 0
        if weekday_avg > 0:
            percentage_difference = round(((weekend_avg - weekday_avg) / weekday_avg) * 100, 2)
        
        most_active_day = max(daily_stats, key=lambda x: x['avg_rentals'])
        least_active_day = min(daily_stats, key=lambda x: x['avg_rentals'])
        
        return {
            'comparison': comparison_data,
            'daily_breakdown': daily_stats,
            'summary': {
                'percentage_difference': percentage_difference,
                'weekend_vs_weekday': 'higher' if weekend_avg > weekday_avg else 'lower',
                'most_active_day': most_active_day,
                'least_active_day': least_active_day,
                'total_days_analyzed': len(daily_stats)
            }
        }
    
    def _process_weather_data(self, weather_impact_data, temp_correlation):
        """Processa dati impatto meteo"""
        weather_conditions = {
            1: 'Sereno/Poche nuvole',
            2: 'Nebbia/Nuvoloso', 
            3: 'Neve/Pioggia leggera',
            4: 'Pioggia/Neve intensa'
        }
        
        weather_stats = []
        best_weather = None
        worst_weather = None
        
        for row in weather_impact_data:
            weather_stat = {
                'weather_code': row.weather_condition,
                'weather_name': weather_conditions.get(row.weather_condition, 'Sconosciuto'),
                'avg_rentals': round(row.avg_rentals, 2),
                'max_rentals': row.max_rentals,
                'min_rentals': row.min_rentals,
                'total_rentals': row.total_rentals,
                'sample_count': row.sample_count,
                'avg_temperature': round(row.avg_temp, 3) if row.avg_temp else 0,
                'avg_humidity': round(row.avg_humidity, 3) if row.avg_humidity else 0,
                'avg_windspeed': round(row.avg_windspeed, 3) if row.avg_windspeed else 0
            }
            weather_stats.append(weather_stat)
            
            if best_weather is None or weather_stat['avg_rentals'] > best_weather['avg_rentals']:
                best_weather = weather_stat
            if worst_weather is None or weather_stat['avg_rentals'] < worst_weather['avg_rentals']:
                worst_weather = weather_stat
        
        # Processa correlazione temperatura
        temp_stats = []
        for row in temp_correlation:
            temp_stats.append({
                'temperature_category': row.temp_category,
                'avg_rentals': round(row.avg_rentals, 2),
                'sample_count': row.sample_count
            })
        
        # Calcola impatto
        weather_impact_percentage = 0
        if worst_weather and best_weather and worst_weather['avg_rentals'] > 0:
            weather_impact_percentage = round(
                ((best_weather['avg_rentals'] - worst_weather['avg_rentals']) / worst_weather['avg_rentals']) * 100, 2
            )
        
        return {
            'weather_conditions': weather_stats,
            'temperature_impact': temp_stats,
            'summary': {
                'best_weather_condition': best_weather,
                'worst_weather_condition': worst_weather,
                'weather_impact_percentage': weather_impact_percentage,
                'total_weather_conditions': len(weather_stats)
            }
        }