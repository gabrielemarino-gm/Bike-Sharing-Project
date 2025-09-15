"""
Script per la riconfigurazione del progetto con nuova architettura
"""

import os
import sys

def display_new_structure():
    """Mostra la nuova struttura del progetto"""
    structure = """
🏗️ NUOVA ARCHITETTURA PROGETTO - SEPARAZIONE DATABASE & ML

📂 MoveSolution-Job-Interviews-Project/
├── 🗄️ database/                          # MODULO DATABASE
│   ├── __init__.py                       # Setup SQLAlchemy
│   ├── models/                           # Modelli Database
│   │   ├── __init__.py
│   │   ├── temporal_context.py           # Dati temporali
│   │   ├── weather_condition.py          # Dati meteo
│   │   └── sharing_record.py             # Record sharing
│   ├── migrations/                       # Script migrazione
│   └── utils/                           # Utility database
│
├── 🤖 machine_learning/                  # MODULO MACHINE LEARNING
│   ├── __init__.py                      # Setup ML environment
│   ├── models/                          # Modelli ML
│   │   ├── __init__.py
│   │   ├── rental_count_predictor.py    # Predizione noleggi
│   │   ├── peak_demand_predictor.py     # Predizione picchi
│   │   └── weather_impact_predictor.py  # Impatto meteo
│   ├── pipelines/                       # Pipeline ML
│   └── utils/
│       └── data_provider.py             # Provider dati per ML
│
├── 📱 app/                              # APPLICAZIONE FLASK
│   ├── __init__.py                      # Flask app (aggiornato)
│   ├── models/                          # Modelli Legacy (deprecati)
│   ├── routes/                          # API endpoints
│   ├── services/                        # Business logic
│   └── utils/                           # Utility app
│
├── 🗃️ data/                             # Dataset
├── 💾 ml_models/                        # Modelli salvati
├── 🧪 tests/                            # Test
└── 📄 migrate_database.py               # Script migrazione

✨ VANTAGGI NUOVA ARCHITETTURA:
• 🔄 Separazione clara responsabilità Database/ML
• 📊 Database normalizzato (3 tabelle invece di 1)
• 🚀 Performance migliorate con indici ottimizzati
• 🧹 Codice più maintainabile e testabile
• 📈 Scalabilità migliorata
• 🔧 ML indipendente da logica database
"""
    print(structure)

def verify_migration():
    """Verifica che la migrazione sia completa"""
    print("🔍 Verifica migrazione struttura...")
    
    # Controlla esistenza cartelle principali
    required_dirs = [
        'database',
        'database/models', 
        'machine_learning',
        'machine_learning/models',
        'machine_learning/utils'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Cartelle mancanti:")
        for missing in missing_dirs:
            print(f"   - {missing}")
        return False
    
    # Controlla file chiave
    required_files = [
        'database/__init__.py',
        'database/models/__init__.py',
        'machine_learning/__init__.py',
        'machine_learning/models/__init__.py',
        'machine_learning/utils/data_provider.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ File mancanti:")
        for missing in missing_files:
            print(f"   - {missing}")
        return False
    
    print("✅ Migrazione struttura completata correttamente!")
    return True

def update_imports_guide():
    """Guida per aggiornare gli import"""
    guide = """
📚 GUIDA AGGIORNAMENTO IMPORT

🔄 VECCHI IMPORT (da aggiornare):
from app.models.bike_record import BikeRecord
from app.models.ml.rental_count_predictor import RentalCountPredictor

✅ NUOVI IMPORT (raccomandati):
# Database models
from database.models import TemporalContext, WeatherCondition, SharingRecord

# ML models  
from machine_learning.models import RentalCountPredictor, PeakDemandPredictor
from machine_learning.utils.data_provider import MLDataProvider

# Shortcut per ML
from machine_learning import create_model, train_all_models

📋 ESEMPI UTILIZZO NUOVA ARCHITETTURA:

# 1. Accesso dati database
from database.models import SharingRecord
records = SharingRecord.get_complete_data(limit=100)

# 2. Training modelli ML
from machine_learning import train_all_models
results = train_all_models(save_models=True)

# 3. Predizioni
from machine_learning import predict_scenario
prediction = predict_scenario(
    temporal_features={'hr': 17, 'season': 2},
    weather_features={'temp': 0.7, 'weathersit': 1}
)

# 4. Data provider per ML
from machine_learning.utils.data_provider import MLDataProvider
ml_data = MLDataProvider.get_training_dataset()
"""
    print(guide)

def migration_steps():
    """Passi successivi per completare la migrazione"""
    steps = """
🚀 PROSSIMI PASSI PER COMPLETARE LA MIGRAZIONE:

1️⃣ MIGRAZIONE DATABASE
   python migrate_database.py migrate

2️⃣ AGGIORNA IMPORT NEI SERVIZI
   - app/services/data_service.py
   - app/services/analytics_service.py  
   - app/services/prediction_service.py

3️⃣ TEST NUOVA ARCHITETTURA
   python -c "from machine_learning import setup_ml_environment; setup_ml_environment()"

4️⃣ TRAINING MODELLI CON NUOVA STRUTTURA
   python -c "from machine_learning import train_all_models; train_all_models()"

5️⃣ AGGIORNA TEST
   pytest tests/ --new-structure

🎯 COMPATIBILITÀ LEGACY:
I vecchi modelli in app/models/ml/ sono ancora disponibili per retrocompatibilità.
Migra gradualmente usando i nuovi import.

⚠️  BREAKING CHANGES:
- Import database: da app.models.* → database.models.*
- Import ML: da app.models.ml.* → machine_learning.models.*
- Configurazione database: ora in database/__init__.py
"""
    print(steps)

if __name__ == "__main__":
    print("🏗️ RICONFIGURAZIONE PROGETTO COMPLETATA")
    print("=" * 60)
    
    display_new_structure()
    
    if verify_migration():
        update_imports_guide()
        migration_steps()
    else:
        print("\n❌ Migrazione incompleta. Controllare i file mancanti.")
        sys.exit(1)
    
    print("\n🎉 Riconfigurazione completata con successo!")
    print("   Ora hai un'architettura separata Database/ML più maintainabile!")
