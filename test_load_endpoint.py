"""
Test per l'endpoint di caricamento dataset
"""

import requests
import json

def test_load_endpoint():
    """Test dell'endpoint POST /load con file CSV"""
    
    # URL dell'endpoint (assumendo Flask in sviluppo)
    url = "http://localhost:5000/load"
    
    # Crea un CSV di test semplice
    test_csv_content = """instant,dteday,season,yr,mnth,hr,holiday,weekday,workingday,weathersit,temp,atemp,hum,windspeed,casual,registered,cnt
1,2011-01-01,1,0,1,0,0,6,0,1,0.24,0.2879,0.81,0.0,3,13,16
2,2011-01-01,1,0,1,1,0,6,0,1,0.22,0.2727,0.80,0.0,8,32,40
3,2011-01-01,1,0,1,2,0,6,0,1,0.22,0.2727,0.80,0.0,5,27,32
"""

    try:
        # Prepara il file
        files = {'file': ('test_dataset.csv', test_csv_content, 'text/csv')}
        data = {'batch_size': '100'}
        
        # Invia richiesta
        print("🚀 Invio richiesta di caricamento...")
        response = requests.post(url, files=files, data=data)
        
        # Analizza risposta
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("✅ Test riuscito!")
        else:
            print("❌ Test fallito!")
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Errore di connessione: {e}")
        print("💡 Assicurati che Flask sia in esecuzione su localhost:5000")
    except Exception as e:
        print(f"❌ Errore: {e}")

def test_curl_example():
    """Mostra esempio di comando curl"""
    print("\n🔧 ESEMPIO COMANDO CURL:")
    print("curl -X POST \\")
    print("  -F 'file=@bike_sharing_dataset.csv' \\")
    print("  -F 'batch_size=1000' \\")
    print("  http://localhost:5000/load")

if __name__ == "__main__":
    print("🧪 TEST ENDPOINT CARICAMENTO DATASET")
    print("=" * 40)
    test_load_endpoint()
    test_curl_example()
