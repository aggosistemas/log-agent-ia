import json
import pytest
from src.app.app import app as flask_app
from src.app import log_processor as log_processor_module
from src.app import firestore_client as firestore_module

@pytest.fixture
def client():
    return flask_app.test_client()

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data.decode("utf-8") == "OK"

def test_logs_valid_payload(monkeypatch, client):
    # Mocks
    def mock_process_log_entry(log_entry):
        return log_entry

    def mock_salvar_log(log_entry):
        return "mocked_id"

    # Aplica mocks nos módulos reais
    monkeypatch.setattr(log_processor_module, "process_log_entry", mock_process_log_entry)
    monkeypatch.setattr(firestore_module, "salvar_log", mock_salvar_log)

    payload = {
        "timestamp": "2025-07-09T14:45:00Z",
        "nivel": "INFO",
        "mensagem": "teste via pytest",
        "servico": "api-test"
    }

    response = client.post("/logs",
                           data=json.dumps(payload),
                           content_type="application/json")

    assert response.status_code == 201
    assert response.json.get("status") == "Log processed and stored"

def test_logs_invalid_payload(client):
    response = client.post("/logs",
                           data="not a json",
                           content_type="application/json")
    assert response.status_code == 500
    assert "error" in response.json
