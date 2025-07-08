import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from google.cloud import firestore

os.environ['GCP_PROJECT_ID'] = 'vm-projeto-tf'  # Configuração global para todos os testes

# Importações
from src.app import app
from app.firestore_client import salvar_log

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('app.firestore_client.firestore.Client')
def test_log_endpoint(mock_firestore_client, client):
    # Configuração completa do mock
    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_add = MagicMock(return_value=(None, 'abc123'))
    
    mock_client.collection.return_value = mock_collection
    mock_collection.add.return_value = mock_add
    mock_firestore_client.return_value = mock_client

    payload = {
        "repo": "teste-api",
        "status": "success",
        "log_summary": "Execução bem sucedida"
    }

    response = client.post('/log', json=payload)
    
    assert response.status_code == 201
    assert response.json == {
        "message": "Log salvo com sucesso",
        "doc_id": "abc123"
    }
    mock_client.collection.assert_called_once_with("logs_pipeline")

def test_log_endpoint_error_handling(client):
    response = client.post('/log', json={})
    assert response.status_code == 400
    assert "error" in response.json
    assert "Payload ausente ou inválido" in response.json["error"]

@patch('app.firestore_client.firestore.Client')
def test_log_endpoint_server_error(mock_firestore_client, client):
    # Configuração para simular erro
    mock_client = MagicMock()
    mock_client.collection.side_effect = Exception("Firestore error")
    mock_firestore_client.return_value = mock_client
    
    response = client.post('/log', json={"test": "data"})
    assert response.status_code == 500
    assert "error" in response.json
    assert "Firestore error" in response.json["error"]