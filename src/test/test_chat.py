import json
import pytest
from app.app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_chat_sem_mensagem(client):
    response = client.post("/chat", json={})
    assert response.status_code == 400
    assert "mensagem" in response.get_json()["erro"]

def test_chat_com_mock(monkeypatch, client):
    # Mock do Firestore
    def mock_buscar_sumarios_recentes(limit=5):
        return [{
            "servico": "api-x",
            "sumario": "Falha no serviço de API.",
            "timestamp": "2025-07-09T10:00:00Z"
        }]

    # Mock do LLM
    def mock_responder_ia(pergunta, contexto):
        return f"Resposta simulada para: {pergunta}"

    monkeypatch.setattr("firestore.consultar_sumarios.buscar_sumarios_recentes", mock_buscar_sumarios_recentes)
    monkeypatch.setattr("llm.responder.responder_ia", mock_responder_ia)

    payload = {"mensagem": "O que aconteceu com a API?"}
    response = client.post("/chat", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    assert "resposta" in response.get_json()
    assert "simulada" in response.get_json()["resposta"]
