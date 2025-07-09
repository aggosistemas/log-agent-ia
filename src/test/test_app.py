from app.app import app as flask_app
import app.log_processor as log_processor_module
import app.firestore_client as firestore_module
import json

def test_health_check():
    client = flask_app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.data == b"OK"

def test_logs_valid_payload(monkeypatch):
    client = flask_app.test_client()

    # Mocks
    def mock_process_log_entry(log_entry):
        return log_entry

    def mock_salvar_log(log_entry):
        return "mocked_id"

    # Aplica o monkeypatch diretamente nos módulos corretos
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
    assert response.json == {"status": "Log processed and stored"}

def test_logs_invalid_payload():
    client = flask_app.test_client()

    response = client.post("/logs",
                           data="not a json",
                           content_type="application/json")

    assert response.status_code == 500
    assert "error" in response.json
