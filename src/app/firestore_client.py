import os
import json
from google.cloud import firestore
from google.oauth2 import service_account

# Caminho para as credenciais da service account (pode ser alterado conforme o ambiente)
CREDENTIALS_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-sa-key.json")
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "seu-projeto-id")

# Inicializa o cliente Firestore com as credenciais
def get_firestore_client():
    # No GKE, o Client já usa as credenciais do workload identity
    return firestore.Client(project=os.getenv('GCP_PROJECT_ID'))

# Função para salvar um log no Firestore
def salvar_log(data: dict):
    client = get_firestore_client()
    data["created_at"] = firestore.SERVER_TIMESTAMP
    doc_ref = client.collection("logs_pipeline").add(data)
    return doc_ref[1].id

    # Adiciona campo de timestamp
    data["created_at"] = firestore.SERVER_TIMESTAMP

    doc_ref = collection_ref.add(data)
    print(f"Documento criado com ID: {doc_ref[1].id}")
    return doc_ref[1].id
