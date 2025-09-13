#!/bin/bash

echo "🔧 Setup rapido per Bike Sharing API"
echo "====================================="

# Vai nella directory del progetto
cd /Users/gabriele/Desktop/Altro/MoveSolution-Job-Interviews-Project

# Crea ambiente virtuale se non esiste
if [ ! -d "venv" ]; then
    echo "📦 Creazione ambiente virtuale..."
    python3 -m venv venv
fi

# Attiva ambiente virtuale
echo "🔄 Attivazione ambiente virtuale..."
source venv/bin/activate

# Installa dipendenze essenziali
echo "📥 Installazione dipendenze..."
pip install --upgrade pip
pip install Flask==2.3.3 Flask-SQLAlchemy==3.0.5 python-dotenv==1.0.0 pandas==2.1.1 scikit-learn==1.3.0 requests==2.31.0 joblib==1.3.2

# Crea directory necessarie
echo "📁 Creazione directory..."
mkdir -p data ml_models

echo ""
echo "✅ Setup completato!"
echo ""
echo "Per avviare l'app:"
echo "1. source venv/bin/activate"
echo "2. python run.py"
