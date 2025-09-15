#!/bin/bash
# filepath: /Users/gabriele/Desktop/Altro/MoveSolution-Job-Interviews-Project/quick_setup.sh

echo "🚴‍♂️ Bike Sharing API - Quick Setup"
echo "=================================="

# Controlla se Python è installato
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trovato. Installalo prima di continuare."
    exit 1
fi

echo "✅ Python3 trovato"

# Installa dipendenze
echo "📦 Installazione dipendenze..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Dipendenze installate"
else
    echo "❌ Errore installazione dipendenze"
    exit 1
fi

# Crea cartelle necessarie
echo "📁 Creazione cartelle..."
mkdir -p machine_learning/weights
mkdir -p instance
echo "✅ Cartelle create"

# Avvia il server
echo "🚀 Avvio server..."
echo "Server disponibile su: http://localhost:5001"
echo "Premi Ctrl+C per fermare il server"
echo ""

python3 run.py