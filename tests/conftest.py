import pytest
from app import create_app, db
from app.models.bike_record import BikeRecord

@pytest.fixture
def app():
    """Crea un'istanza dell'app per i test"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Client di test per le richieste HTTP"""
    return app.test_client()

@pytest.fixture
def sample_data(app):
    """Dati di esempio per i test"""
    with app.app_context():
        record = BikeRecord(
            instant=1,
            season=1,
            yr=0,
            mnth=1,
            hr=0,
            holiday=0,
            weekday=6,
            workingday=0,
            weathersit=1,
            temp=0.24,
            atemp=0.2879,
            hum=0.81,
            windspeed=0.0,
            casual=3,
            registered=13,
            cnt=16
        )
        db.session.add(record)
        db.session.commit()
        return record
