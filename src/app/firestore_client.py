from google.cloud import firestore
import os

def get_firestore_client():
    """Retorna um cliente do Firestore configurado"""
    project_id = os.getenv('GCP_PROJECT_ID')
    if not project_id:
        raise ValueError("Variável GCP_PROJECT_ID não configurada")
    return firestore.Client(project=project_id)

def salvar_log(data: dict) -> str:
    """Salva um documento no Firestore e retorna o ID gerado"""
    if not data or not isinstance(data, dict):
        raise ValueError("Dados inválidos para o log")
    
    try:
        client = get_firestore_client()
        data["created_at"] = firestore.SERVER_TIMESTAMP
        doc_ref = client.collection("logs_pipeline").add(data)
        return doc_ref[1].id
    except Exception as e:
        raise  # Repassa a exceção original sem modificação