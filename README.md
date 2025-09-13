# MoveSolution-Job-Interviews-Project
A backend application that loads and stores a mobility dataset, provides REST APIs to query aggregated statistics, predicts future usage with a simple ML model, and allows downloading processed results in CSV. Built with Python (FastAPI, scikit-learn, SQLAlchemy), using a SQL-like database.

# Bike Sharing Analytics API

API REST per l'analisi e predizione di dati di bike sharing utilizzando Flask e machine learning.

## Struttura del Progetto

```
├── app/
│   ├── __init__.py          # Factory per l'app Flask
│   ├── config.py            # Configurazioni
│   ├── models/              # Modelli del database
│   │   ├── __init__.py
│   │   └── bike_record.py   # Modello BikeRecord
│   ├── routes/              # Endpoint API
│   │   ├── data_routes.py   # Gestione dati
│   │   ├── analytics_routes.py  # Analisi
│   │   └── prediction_routes.py # Predizioni ML
│   └── services/            # Logica di business
│       ├── data_service.py
│       ├── analytics_service.py
│       └── prediction_service.py
├── data/                    # Directory per i dati
├── ml_models/              # Modelli ML salvati
├── tests/                  # Test unitari
├── requirements.txt        # Dipendenze Python
├── Dockerfile             # Container Docker
└── run.py                 # Entry point dell'applicazione
```

## Setup e Installazione

1. **Clona il repository**
```bash
git clone <repository-url>
cd bike-sharing-api
```

2. **Crea un ambiente virtuale**
```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

3. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configura le variabili d'ambiente**
```bash
cp .env.example .env
# Modifica il file .env con le tue configurazioni
```

5. **Avvia l'applicazione**
```bash
python run.py
```

## API Endpoints

### Data Management
- `POST /api/data/load` - Carica dataset
- `GET /api/data/status` - Stato del dataset
- `GET /api/data/sample` - Campione dei dati

### Analytics
- `GET /api/analytics/hourly` - Statistiche orarie
- `GET /api/analytics/daily` - Statistiche giornaliere
- `GET /api/analytics/seasonal` - Statistiche stagionali
- `GET /api/analytics/weather` - Statistiche meteo
- `GET /api/analytics/export/csv` - Esporta analisi in CSV

### Machine Learning
- `POST /api/prediction/train` - Addestra modello
- `POST /api/prediction/predict` - Effettua predizione
- `GET /api/prediction/model/info` - Info modello
- `GET /api/prediction/evaluate` - Valuta modello

## Tecnologie Utilizzate

- **Flask**: Framework web
- **SQLAlchemy**: ORM per database
- **Pandas**: Manipolazione dati
- **Scikit-learn**: Machine learning
- **PostgreSQL/SQLite**: Database
- **Docker**: Containerizzazione

## Dataset

Il progetto utilizza il [UCI Bike Sharing Dataset](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) che contiene:
- Dati orari di noleggio biciclette
- Informazioni meteorologiche
- Variabili temporali (stagione, mese, ora, ecc.)
- Utenti casuali vs registrati

## Esempi di Utilizzo

### Caricamento Dataset
```bash
curl -X POST http://localhost:5000/api/data/load
```

### Statistiche Orarie
```bash
curl http://localhost:5000/api/analytics/hourly
```

### Addestramento Modello
```bash
curl -X POST http://localhost:5000/api/prediction/train \
  -H "Content-Type: application/json" \
  -d '{"model_type": "linear_regression"}'
```

### Predizione
```bash
curl -X POST http://localhost:5000/api/prediction/predict \
  -H "Content-Type: application/json" \
  -d '{"features": {"temp": 0.5, "hum": 0.6, "windspeed": 0.2, "hr": 12}}'
```

## Docker

### Build dell'immagine
```bash
docker build -t bike-sharing-api .
```

### Esecuzione del container
```bash
docker run -p 5000:5000 bike-sharing-api
```

## Testing

```bash
pytest tests/
```

## Contributi

1. Fork del progetto
2. Crea un branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push del branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request
