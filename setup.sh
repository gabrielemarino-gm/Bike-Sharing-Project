#!/bin/bash

# Script di setup per il progetto Bike Sharing API

echo "🚀 Setup Bike Sharing API Project"
echo "=================================="

# Controlla se Python è installato
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 non trovato. Installa Python 3.9 o superiore."
    exit 1
fi

echo "✅ Python trovato: $(python3 --version)"

# Crea ambiente virtuale se non esiste
if [ ! -d "venv" ]; then
    echo "📦 Creazione ambiente virtuale..."
    python3 -m venv venv
fi

# Attiva ambiente virtuale
echo "🔄 Attivazione ambiente virtuale..."
source venv/bin/activate

# Installa dipendenze
echo "📥 Installazione dipendenze..."
pip install --upgrade pip
pip install -r requirements.txt

# Crea file .env se non esiste
if [ ! -f ".env" ]; then
    echo "⚙️  Creazione file di configurazione .env..."
    cp .env.example .env
    echo "📝 Modifica il file .env con le tue configurazioni"
fi

# Crea directory se non esistono
mkdir -p data ml_models

echo ""
echo "🎉 Setup completato!"
echo ""
echo "Per avviare l'applicazione:"
echo "1. Attiva l'ambiente virtuale: source venv/bin/activate"
echo "2. Avvia l'app: python run.py"
echo ""
echo "L'API sarà disponibile su: http://localhost:5000"
echo ""
echo "Endpoints principali:"
echo "- POST /api/data/load - Carica dataset"
echo "- GET /api/analytics/hourly - Statistiche orarie"
echo "- POST /api/prediction/train - Addestra modello ML"
echo "- POST /api/prediction/predict - Effettua predizioni"
