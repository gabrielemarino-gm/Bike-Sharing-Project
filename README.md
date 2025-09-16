# 🚴‍♂️ Bike Sharing API - Analisi e Predizione Dati

Un'API REST completa per l'analisi e la predizione dei dati di bike sharing, costruita con Flask e tecnologie di Machine Learning.

## 📋 Indice

- [Caratteristiche](#-caratteristiche)
- [Installazione](#-installazione)
  - [Installazione Locale](#-installazione-locale)
  - [Installazione con Docker](#-installazione-con-docker)
- [Avvio del Server](#-avvio-del-server)
  - [Avvio Locale](#-avvio-locale)
  - [Avvio con Docker](#-avvio-con-docker)
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

### 🏠 Installazione Locale

#### Prerequisiti
- Python 3.8+
- pip

#### Setup Ambiente

```bash
# Clone del repository
git clone <repository-url>
cd Bike-Sharing-Project

# Creazione ambiente virtuale (raccomandato)
python -m venv venv

# Attivazione ambiente virtuale
# Su macOS/Linux:
source venv/bin/activate
# Su Windows:
# venv\Scripts\activate

# Installazione dipendenze
pip install -r requirements.txt
```

#### Struttura Directory
```
Bike-Sharing-Project/
├── venv/                          # Ambiente virtuale
├── instance/                      # Database SQLite
├── app/                           # Codice applicazione
├── database/                      # Moduli database
├── machine_learning/              # Modelli ML
└── run.py                         # Entry point
```

#### 🐳 Setup con Docker

```bash
# Clone del repository
git clone <repository-url>
cd Bike-Sharing-Project

# Crea i file necessari (vedi sezione File di Configurazione)
# Poi build dell'immagine Docker
docker build -t bike-sharing-api .
```

## 🚀 Avvio del Server

### 🏠 Avvio Locale

```bash
# Assicurati che l'ambiente virtuale sia attivo
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Avvio dell'applicazione
python run.py
```

Il server sarà disponibile su: `http://localhost:5001`

### 🐳 Avvio con Docker

#### Comando Docker Run Raccomandato:

```bash
# Comando completo raccomandato per l'avvio
docker run -d \
  --name bike-sharing-api \
  -p 5001:5001 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/machine_learning/weights:/app/machine_learning/weights \
  --restart unless-stopped \
  -e FLASK_ENV=production \
  bike-sharing-api
```

**Per test rapido senza volumi:**
```bash
# Test veloce senza persistenza dati
docker run --rm -p 5001:5001 bike-sharing-api
```



## 📡 API Endpoints

### 📊 **Status Database**
Verifica lo stato del database e le informazioni sui dati caricati.

```bash
curl http://localhost:5001/api/data/status
```

### 📤 **Caricamento Dataset**
Carica un file CSV contenente i dati di bike sharing nel database con batch size configurabile.

```bash
curl -F "file=@path/you/file.csv" -F "batch_size=<Your-Batch>" http://localhost:5001/api/data/load
```

### 🕒 **Analisi Pattern Orari**
Analizza la varie metriche di aggregazione oraria, come per esempio il numero medio di noleggi per ora.

```bash
curl -X GET http://localhost:5001/api/analytics/mean-rental-by-hour
```

### 📅 **Analisi Weekday vs Weekend**
Confronta le metriche aggregate distinguendo tra giorni feriali e weekend.

```bash
curl -X GET http://localhost:5001/api/analytics/weekday-vs-weekend
```

### 🌤️ **Analisi Impatto Meteo**
Analizza l'influenza delle condizioni meteorologiche sui noleggi.

```bash
curl -X GET http://localhost:5001/api/analytics/weather-impact
```

### 🤖 **Training Modello Picchi di Domanda**
Addestra il modello di machine learning per la previsione dei picchi di domanda.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"model_type": "logistic_regression"}' \
  http://localhost:5001/api/prediction/train-peak-model
```

### 📈 **Training Modello Conteggio Noleggi**
Addestra il modello di machine learning per la predizione del numero di noleggi.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"model_type": "random_forest"}' \
  http://localhost:5001/api/prediction/train-rental-model
```

### 🌦️ **Training Modello Impatto Meteo**
Addestra il modello di machine learning per l'analisi dell'impatto delle condizioni meteorologiche.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"model_type": "random_forest"}' \
  http://localhost:5001/api/prediction/train-weather-model
```

### 🔮 **Predizione Picchi di Domanda**
Predice se ci sarà un picco di domanda basandosi sui parametri forniti.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"input_data": {
    "season": 1,
    "yr": 0,
    "mnth": 1,
    "hr": 0,
    "holiday": 0,
    "weekday": 6,
    "workingday": 0,
    "weathersit": 1,
    "temp": 0.24,
    "atemp": 0.2879,
    "hum": 0.81,
    "windspeed": 0.0
  }}' \
  http://localhost:5001/api/prediction/predict-peak-demand

  # I valori usati sono di esempio
```

### 🌡️ **Predizione Impatto Meteo**
Predice l'impatto delle condizioni meteorologiche sui noleggi.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"input_data": {
    "season": 1,
    "yr": 0,
    "mnth": 1,
    "hr": 0,
    "holiday": 0,
    "weekday": 6,
    "workingday": 0,
    "weathersit": 1,
    "temp": 0.24,
    "atemp": 0.2879,
    "hum": 0.81,
    "windspeed": 0.0
  }}' \
  http://localhost:5001/api/prediction/predict-weather-impact

  # I valori usati sono di esempio
```

### 🚴 **Predizione Conteggio Noleggi**
Predice il numero esatto di noleggi per le condizioni specificate.

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"input_data": {
    "season": 1,
    "yr": 0,
    "mnth": 1,
    "hr": 0,
    "holiday": 0,
    "weekday": 6,
    "workingday": 0,
    "weathersit": 1,
    "temp": 0.24,
    "atemp": 0.2879,
    "hum": 0.81,
    "windspeed": 0.0
  }}' \
  http://localhost:5001/api/prediction/predict-rental-count

  # I valori usati sono di esempio
```

## 📝 Parametri di Input per le Predizioni

### Parametri Comuni:
- **season**: Stagione (1=primavera, 2=estate, 3=autunno, 4=inverno)
- **yr**: Anno (0=2011, 1=2012)
- **mnth**: Mese (1-12)
- **hr**: Ora (0-23)
- **holiday**: Festivo (0=no, 1=sì)
- **weekday**: Giorno settimana (0=domenica, 6=sabato)
- **workingday**: Giorno lavorativo (0=no, 1=sì)
- **weathersit**: Condizioni meteo (1=sereno, 2=nuvoloso, 3=pioggia leggera, 4=pioggia forte)
- **temp**: Temperatura normalizzata (0-1)
- **atemp**: Temperatura percepita normalizzata (0-1)
- **hum**: Umidità normalizzata (0-1)
- **windspeed**: Velocità vento normalizzata (0-1)

### Modelli di Machine Learning Supportati:
E' possibile allenare e poi utilizzare i seguenti modelli ML:
- **Picchi di Domanda**: `logistic_regression`, `random_forest`, `svm`
- **Impatto Meteo**: `random_forest`, `linear_regression`, `gradient_boosting`
- **Conteggio Noleggi**: `linear_regression`, `random_forest`, `gradient_boosting`

## 📝 Note
- Non è possibile eseguire una predizione senza aver prima allenato il modello corrispondente.
- Il database SQLite viene salvato in `instance/bike_sharing.db`
- I modelli ML vengono salvati in `machine_learning/weights/`


## Credits
Sviluppato da [Gabriele Marino](https://github.com/gabrielemarino-gm)