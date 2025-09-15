# Usa Python 3.11 slim come base
FROM python:3.11-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file requirements per ottimizzare la cache Docker
COPY requirements.txt .

# Installa le dipendenze Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del progetto
COPY . .

# Crea le cartelle necessarie
RUN mkdir -p machine_learning/weights instance

# Espone la porta 5001
EXPOSE 5001

# Imposta variabili d'ambiente
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando per avviare l'applicazione
CMD ["python", "run.py"]