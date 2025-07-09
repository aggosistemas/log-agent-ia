import os
from google.cloud import firestore

def buscar_sumarios_recentes(limit=5):
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("GCP_PROJECT_ID não configurado")

    client = firestore.Client(project=project_id)
    docs = client.collection("logs_sumarios") \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .limit(limit) \
        .stream()

    return [doc.to_dict() for doc in docs]
