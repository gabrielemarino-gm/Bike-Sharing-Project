# Endpoint di Caricamento Dataset - Documentazione

## 🚀 Endpoint `/load`

L'endpoint permette di caricare un dataset CSV nel database del sistema.

### 📋 Specifiche

- **URL**: `POST /load`
- **Content-Type**: `multipart/form-data`
- **Parametri**:
  - `file` (required): File CSV con il dataset
  - `batch_size` (optional): Dimensione batch per caricamento (default: 1000)

### 📊 Formato CSV Richiesto

Il file CSV deve contenere le seguenti colonne (stesso formato del dataset UCI Bike Sharing):

```csv
instant,dteday,season,yr,mnth,hr,holiday,weekday,workingday,weathersit,temp,atemp,hum,windspeed,casual,registered,cnt
1,2011-01-01,1,0,1,0,0,6,0,1,0.24,0.2879,0.81,0.0,3,13,16
2,2011-01-01,1,0,1,1,0,6,0,1,0.22,0.2727,0.80,0.0,8,32,40
...
```

### 🔧 Esempi di Utilizzo

#### Con curl:
```bash
curl -X POST \
  -F 'file=@bike_sharing_dataset.csv' \
  -F 'batch_size=1000' \
  http://localhost:5000/load
```

#### Con Python requests:
```python
import requests

url = "http://localhost:5000/load"
files = {'file': open('bike_sharing_dataset.csv', 'rb')}
data = {'batch_size': '1000'}

response = requests.post(url, files=files, data=data)
print(response.json())
```

#### Con HTML Form:
```html
<form action="/load" method="post" enctype="multipart/form-data">
  <input type="file" name="file" accept=".csv" required>
  <input type="number" name="batch_size" value="1000" min="1">
  <input type="submit" value="Carica Dataset">
</form>
```

### ✅ Risposta di Successo

```json
{
  "success": true,
  "message": "Dataset caricato con successo!",
  "data": {
    "filename": "bike_sharing_dataset.csv",
    "total_records": 17379,
    "success_count": 17379,
    "error_count": 0,
    "success_rate": 100.0,
    "batch_size": 1000,
    "database_stats": {
      "total_records": 17379,
      "date_range": {
        "min_date": "2011-01-01",
        "max_date": "2012-12-31"
      },
      "weather_distribution": {
        "weather_1": 11413,
        "weather_2": 4544,
        "weather_3": 1419,
        "weather_4": 3
      },
      "seasonal_distribution": {
        "season_1": 4242,
        "season_2": 4409,
        "season_3": 4496,
        "season_4": 4232
      }
    }
  }
}
```

### ❌ Risposta di Errore

```json
{
  "success": false,
  "error": "Formato file non supportato. Usa file CSV."
}
```

### 🔍 Validazioni

L'endpoint esegue le seguenti validazioni:

1. **Presenza del file**: Verifica che sia presente il campo `file`
2. **Nome del file**: Verifica che il file abbia un nome valido
3. **Estensione**: Verifica che l'estensione sia `.csv`
4. **Contenuto**: Verifica che il CSV sia leggibile e abbia le colonne corrette
5. **Dati**: Valida i tipi di dati durante il caricamento

### 🗄️ Comportamento del Database

- **Pulizia**: Prima del caricamento, tutti i record esistenti vengono eliminati
- **Batch Processing**: I dati vengono caricati in batch per ottimizzare le performance
- **Transazioni**: Ogni batch è gestito in una transazione separata
- **Rollback**: In caso di errore, la transazione del batch viene annullata

### 📈 Monitoraggio

L'endpoint fornisce statistiche dettagliate:
- Numero totale di record nel file
- Record caricati con successo
- Record con errori
- Percentuale di successo
- Statistiche finali del database

### 🛡️ Gestione Errori

Possibili errori:
- `400`: File mancante, nome vuoto, formato non valido
- `500`: Errori di database, problemi di parsing CSV, errori del server
