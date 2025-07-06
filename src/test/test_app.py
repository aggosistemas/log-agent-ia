import pytest
from unittest.mock import patch
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.salvar_log')
def test_log_endpoint(mock_salvar_log, client):
    mock_salvar_log.return_value = 'abc123'
    
    payload = {
        "repo": "teste-api",
        "status": "success",
        "log_summary": "Execução bem sucedida"
    }

    response = client.post('/log', json=payload)
    assert response.status_code == 200
    assert response.json['doc_id'] == 'abc123'
    assert response.json['message'] == 'Log salvo com sucesso'
    mock_salvar_log.assert_called_once_with(payload)
