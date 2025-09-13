def test_data_status_endpoint(client):
    """Test dell'endpoint di status dei dati"""
    response = client.get('/api/data/status')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'total_records' in data

def test_sample_data_endpoint(client, sample_data):
    """Test dell'endpoint per i dati di esempio"""
    response = client.get('/api/data/sample?limit=5')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'sample_data' in data
    assert 'count' in data

def test_load_default_dataset(client):
    """Test del caricamento del dataset di default"""
    response = client.post('/api/data/load')
    assert response.status_code == 200
    
    data = response.get_json()
    assert 'message' in data
    assert 'records_loaded' in data
