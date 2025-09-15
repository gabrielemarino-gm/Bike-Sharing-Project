# 🚴‍♂️ Bike Sharing API - Analisi e Predizione Dati

Un'API REST completa per l'analisi e la predizione dei dati di bike sharing, costruita con Flask e tecnologie di Machine Learning.

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Installazione](#-installazione)
- [Avvio del Server](#-avvio-del-server)
- [Struttura del Progetto](#-struttura-del-progetto)
- [API Endpoints](#-api-endpoints)
- [Esempi di Utilizzo](#-esempi-di-utilizzo)
- [Machine Learning](#-machine-learning)
- [Database](#-database)
- [Troubleshooting](#-troubleshooting)

## 🚀 Caratteristiche

- **Caricamento Dati**: Upload di dataset CSV con validazione automatica
- **Analisi Avanzata**: Pattern orari, analisi weekday vs weekend, impatto meteo
- **Machine Learning**: Predizione picchi di domanda, conteggio noleggi, impatto meteo
- **Database SQLite**: Persistenza dati con modello unificato
- **API RESTful**: Endpoints ben strutturati con gestione errori
- **Logging**: Sistema di logging completo per debugging

## 🛠️ Installazione

### Prerequisiti
- Python 3.8+
- pip

### Setup Ambiente

```bash
# Clone del repository
git clone <repository-url>
cd MoveSolution-Job-Interviews-Project

# Creazione ambiente virtuale (opzionale ma raccomandato)
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate

# Installazione dipendenze
pip install flask flask-sqlalchemy pandas numpy scikit-learn joblib
```

## 🚀 Avvio del Server

```bash
# Avvio dell'applicazione
python run.py
```

Il server sarà disponibile su: `http://localhost:5001`

## 📁 Struttura del Progetto

```
MoveSolution-Job-Interviews-Project/
├── app/
│   ├── __init__.py                 # App factory
│   └── routes/
│       ├── data_routes.py          # Endpoints per gestione dati
│       ├── analytics_routes.py     # Endpoints per analisi
│       └── prediction_routes.py    # Endpoints per ML
├── database/
│   ├── __init__.py                 # Configurazione database
│   ├── bike_record.py              # Modello dati unificato
│   ├── data_loader.py              # Caricamento dati
│   └── data_analytics.py           # Logica di analisi
├── machine_learning/
│   ├── peak_demand_predictor.py    # Predizione picchi
│   ├── rental_count_predictor.py   # Predizione conteggi
│   └── weather_impact_predictor.py # Predizione impatto meteo
├── instance/
│   └── bike_sharing.db             # Database SQLite
└── run.py                          # Entry point applicazione
```

## 🔌 API Endpoints

### Health Check
```bash
GET /
```

### 📊 Data Management

#### Caricamento Dataset
```bash
POST /api/data/load
Content-Type: multipart/form-data
```

#### Statistiche Dataset
```bash
GET /api/data/stats
```

#### Status del Sistema
```bash
GET /api/data/status
```

### 📈 Analytics

#### Pattern Orari
```bash
GET /api/analytics/mean-rental-by-hour
```

#### Confronto Weekday vs Weekend
```bash
GET /api/analytics/weekday-vs-weekend
```

#### Impatto Condizioni Meteo
```bash
GET /api/analytics/weather-impact
```

### 🤖 Machine Learning

#### Training Modello Picchi
```bash
POST /api/prediction/train-peak-model
Content-Type: application/json
```

#### Training Modello Conteggi
```bash
POST /api/prediction/train-rental-model
Content-Type: application/json
```

#### Predizione Picchi di Domanda
```bash
POST /api/prediction/predict-peak-demand
Content-Type: application/json
```

#### Predizione Conteggio Noleggi
```bash
POST /api/prediction/predict-rental-count
Content-Type: application/json
```

## 💻 Esempi di Utilizzo

### 1. Health Check del Sistema

```bash
curl -X GET http://localhost:5001/
```

**Risposta:**
```json
{
  "database": {
    "status": "Connected",
    "total_records": 17379
  },
  "endpoints": {
    "analytics": "/api/analytics/",
    "data": "/api/data/",
    "prediction": "/api/prediction/"
  },
  "message": "Bike Sharing API is running!",
  "status": "OK"
}
```

### 2. Caricamento Dataset CSV

```bash
curl -X POST \
  -F "file=@dataset.csv" \
  http://localhost:5001/api/data/load
```

**Risposta:**
```json
{
  "data": {
    "batch_size": 1000,
    "database_stats": {
      "date_range": {
        "max_date": "2012-12-31",
        "min_date": "2011-01-01"
      },
      "seasonal_distribution": {
        "season_1": 4242,
        "season_2": 4409,
        "season_3": 4496,
        "season_4": 4232
      },
      "total_records": 17379,
      "weather_distribution": {
        "weather_1": 11413,
        "weather_2": 4544,
        "weather_3": 1419,
        "weather_4": 3
      }
    },
    "error_count": 0,
    "filename": "hour.csv",
    "success_count": 17379,
    "success_rate": 100.0,
    "total_records": 17379
  },
  "message": "Dataset caricato con successo!",
  "success": true
}

```

### 3. Analisi Pattern Orari

```bash
curl -X GET http://localhost:5001/api/analytics/mean-rental-by-hour
```

**Risposta:**
```json
{
  "hourly_patterns": [
    {
      "hour": 0,
      "avg_rentals": 55.67,
      "max_rentals": 331,
      "min_rentals": 1,
      "total_rentals": 40285,
      "sample_count": 724
    },
    ...
  ],
  "summary": {
    "peak_hour": {"hour": 8, "avg_rentals": 359.52},
    "low_hour": {"hour": 4, "avg_rentals": 8.32}
  }
}
```

### 4. Confronto Weekday vs Weekend

```bash
curl -X GET http://localhost:5001/api/analytics/weekday-vs-weekend
```

**Risposta:**
```json
{
  "comparison": {
    "Weekday": {
      "avg_rentals": 191.35,
      "max_rentals": 977,
      "total_rentals": 2396126,
      "sample_count": 12516
    },
    "Weekend": {
      "avg_rentals": 202.72,
      "max_rentals": 977,
      "total_rentals": 986441,
      "sample_count": 4863
    }
  },
  "summary": {
    "percentage_difference": 5.94,
    "weekend_vs_weekday": "higher"
  }
}
```

### 5. Training Modello ML

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"model_type": "random_forest"}' \
  http://localhost:5001/api/prediction/train-peak-model
```

**Risposta:**
```json
{
  "accuracy": 0.883199079401611,
  "confusion_matrix": [
    [
      2418,
      364
    ],
    [
      42,
      652
    ]
  ],
  "f1_score": 0.7625730994152047,
  "negative_samples": 2782,
  "positive_samples": 694,
  "pr_auc": 0.9012461968234616,
  "precision": 0.6417322834645669,
  "recall": 0.9394812680115274,
  "roc_auc": 0.9706869189955187,
  "test_samples": 3476
}
```

### 6. Predizione Picchi di Domanda

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": {
      "season": 1,
      "yr": 0,
      "mnth": 1,
      "hr": 8,
      "holiday": 0,
      "weekday": 1,
      "workingday": 1,
      "weathersit": 1,
      "temp": 0.24,
      "atemp": 0.28,
      "hum": 0.81,
      "windspeed": 0.0
    }
  }' \
  http://localhost:5001/api/prediction/predict-peak-demand
```

**Risposta:**
```json
{
  "prediction": {
    "features_used": [
      "season",
      "yr",
      "mnth",
      "hr",
      "holiday",
      "weekday",
      "workingday",
      "weathersit",
      "temp",
      "atemp",
      "hum",
      "windspeed"
    ],
    "is_peak": false,
    "model_type": "random_forest",
    "peak_probability": 0.06422551258220652,
    "peak_threshold": 321.0
  }
}
```

## 🤖 Machine Learning

### Modelli Disponibili

1. **Peak Demand Predictor**: Classifica se un'ora sarà di picco
   - Modelli: Random Forest, Logistic Regression, Decision Tree
   - Target: Binario (picco/non picco)

2. **Rental Count Predictor**: Predice il numero esatto di noleggi
   - Modelli: Random Forest, Linear Regression, Gradient Boosting
   - Target: Continuo (numero noleggi)

3. **Weather Impact Predictor**: Analizza l'impatto del meteo
   - Modelli: Random Forest, SVM
   - Target: Categorie di impatto meteo

### Features Utilizzate

```python
features = [
    'season',      # Stagione (1-4)
    'yr',          # Anno (0: 2011, 1: 2012)
    'mnth',        # Mese (1-12)
    'hr',          # Ora (0-23)
    'holiday',     # Festivo (0/1)
    'weekday',     # Giorno settimana (0-6)
    'workingday',  # Giorno lavorativo (0/1)
    'weathersit',  # Condizione meteo (1-4)
    'temp',        # Temperatura normalizzata
    'atemp',       # Temperatura percepita
    'hum',         # Umidità
    'windspeed'    # Velocità vento
]
```

## 🗃️ Database

### Modello Dati Unificato

La tabella `bike_records` contiene tutti i dati con schema:

```sql
CREATE TABLE bike_records (
    id INTEGER PRIMARY KEY,
    instant INTEGER,
    dteday DATE,
    season INTEGER,
    yr INTEGER,
    mnth INTEGER,
    hr INTEGER,
    holiday BOOLEAN,
    weekday INTEGER,
    workingday BOOLEAN,
    weathersit INTEGER,
    temp FLOAT,
    atemp FLOAT,
    hum FLOAT,
    windspeed FLOAT,
    casual INTEGER,
    registered INTEGER,
    cnt INTEGER
);
```

### Posizione Database

Il database SQLite viene salvato in: `instance/bike_sharing.db`

## 🔧 Troubleshooting

### Problemi Comuni

#### 1. Errore "File not found"
```bash
# Verificare che il server sia in esecuzione
curl -X GET http://localhost:5001/
```

#### 2. Errore "No module named..."
```bash
# Reinstallare dipendenze
pip install -r requirements.txt
```

#### 3. Database vuoto
```bash
# Caricare dataset prima delle analisi
curl -X POST -F "file=@dataset.csv" http://localhost:5001/api/data/load
```

#### 4. Modello non trovato
```bash
# Addestrare modello prima delle predizioni
curl -X POST -H "Content-Type: application/json" \
  -d '{"model_type": "random_forest"}' \
  http://localhost:5001/api/prediction/train-peak-model
```

### Log e Debug

I log dell'applicazione vengono stampati sulla console durante l'esecuzione. Per maggiori dettagli, controllare:

- Messaggi di avvio del server
- Errori di caricamento dati
- Metriche di training dei modelli
- Errori di predizione

## 📝 Note

- Il dataset deve essere in formato CSV con le colonne specificate nel modello
- I modelli ML vengono salvati in `machine_learning/weights/`
- Tutti gli endpoint restituiscono JSON con gestione errori standardizzata
