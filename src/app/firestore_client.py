import logging
from google.cloud import firestore
from datetime import datetime
import os

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pequi-logs")

def get_firestore_client():
    """Inicializa e retorna o cliente Firestore."""
    project_id = os.getenv("GCP_PROJECT_ID")
    database_id = os.getenv("FIRESTORE_DATABASE_ID", "(default)")

    logger.debug(f"Conectando ao Firestore - Project: {project_id}, Database: {database_id}")
    return firestore.Client(project=project_id, database=database_id)

def save_pipeline_log(payload):
    """
    Salva o log no Firestore independentemente do status.
    Retorna uma tupla (status, doc_id).
    """
    try:
        client = get_firestore_client()

        # Nome da coleção
        collection_name = "pipeline_logs"

        logger.debug(f"Salvando log na coleção '{collection_name}': {payload}")

        # Adiciona timestamp de gravação
        payload["received_at"] = datetime.utcnow().isoformat() + "Z"

        # Garante que campos essenciais existam
        payload.setdefault("service", "unknown")
        payload.setdefault("repo", "unknown")
        payload.setdefault("workflow", "unknown")
        payload.setdefault("job", "unknown")
        payload.setdefault("status", "unknown")
        payload.setdefault("branch", "unknown")
        payload.setdefault("autor", "unknown")
        payload.setdefault("git_sha", "unknown")
        payload.setdefault("run_id", "unknown")
        payload.setdefault("mensagem_curta", "")
        payload.setdefault("tipo_erro", "")
        payload.setdefault("stack_hash", "")

        # Salva no Firestore
        doc_ref = client.collection(collection_name).add(payload)
        doc_id = doc_ref[1].id  # Segundo elemento do tuple é o DocumentReference

        logger.info(f"Log gravado no Firestore com ID: {doc_id}")
        return "ok", doc_id

    except Exception as e:
        logger.exception("Erro ao salvar log no Firestore")
        return "error", str(e)
