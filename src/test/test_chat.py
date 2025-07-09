import json
import pytest
from src.app.app import app as flask_app
from src.firestore import consultar_sumarios
from src.llm import responder

@pytest.fixture
def client():
    return flask_app.test_client()

def test_chat_sem_mensagem(client):
    response = client.post("/chat", data=json.dumps({}), content_type="application/json")
    assert response.status_code == 400
    assert "erro" in response.json

def test_chat_com_mock(monkeypatch, client):
    # Mock Firestore
    def mock_buscar_sumarios_recentes(limit=5):
        return [{
            "servico": "api-x",
            "sumario": "Falha no serviço de API.",
            "timestamp": "2025-07-09T10:00:00Z"
        }]

    # Mock LLM
    def mock_responder_ia(pergunta, contexto):
        return f"Resposta simulada para: {pergunta}"

    monkeypatch.setattr(consultar_sumarios, "buscar_sumarios_recentes", mock_buscar_sumarios_recentes)
    monkeypatch.setattr(responder, "responder_ia", mock_responder_ia)
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-key")
    monkeypatch.setenv("GCP_PROJECT_ID", "dummy-project")

    payload = {"mensagem": "O que aconteceu com a API?"}
    response = client.post("/chat", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    assert "resposta" in response.json
