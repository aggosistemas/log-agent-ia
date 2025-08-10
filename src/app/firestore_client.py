from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple, Any

from google.cloud import firestore

logger = logging.getLogger("pequi-logs")


def _to_utc_dt(value) -> datetime:
    """
    Converte uma string ISO 8601 (com 'Z' ou offset) em datetime tz-aware UTC.
    Se já for datetime tz-aware, normaliza para UTC.
    Se vier None, retorna agora UTC.
    """
    if value is None:
        return datetime.now(timezone.utc)

    if isinstance(value, datetime):
        return value.astimezone(timezone.utc)

    if isinstance(value, str):
        iso = value.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(iso)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

    return datetime.now(timezone.utc)


def get_firestore_client() -> firestore.Client:
    """
    Retorna o cliente do Firestore configurado para o database correto.
    - GCP_PROJECT_ID: ID do projeto (obrigatório)
    - FIRESTORE_DATABASE_ID: id do database ('(default)' ou 'agent-ia-active', etc.)
    """
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise ValueError("Variável GCP_PROJECT_ID não configurada")

    database_id = os.getenv("FIRESTORE_DATABASE_ID", "(default)")
    return firestore.Client(project=project_id, database=database_id)


def _normalize_add_return(result: Any):
    """
    Normaliza o retorno de collection.add(data) para sempre devolver (DocumentReference, write_time|None).
    Algumas versões retornam (DocumentReference, write_time),
    outras podem retornar (write_time, DocumentReference) ou apenas DocumentReference.
    """
    # Caso padrão mais comum: tupla de 2 valores
    if isinstance(result, tuple) and len(result) == 2:
        a, b = result
        # Se o primeiro tem .id, é o DocumentReference
        if hasattr(a, "id"):
            return a, b
        # Se o segundo tem .id, inverte
        if hasattr(b, "id"):
            return b, a
        # Nenhum tem .id? Retorna primeiro e None (deixa erro mais legível adiante)
        return a, None

    # Algumas versões podem retornar só o DocumentReference
    if hasattr(result, "id"):
        return result, None

    # Forma inesperada: devolve como veio para erro explicativo
    return result, None


def save_pipeline_log(data: Dict) -> Tuple[str, str]:
    """
    Salva um documento em logs_pipeline e retorna (status, id_documento).

    Regras:
      - Apenas status == 'failure' vai para Firestore (DRP).
      - anexa analisado=false, ttl_hot (agora+TTL_DAYS), created_at/updated_at.

    Retornos:
      - ("IGNORED", motivo) quando não persiste (ex.: status != failure)
      - ("OK", id_documento) quando gravou com sucesso
    """
    if not isinstance(data, dict):
        raise ValueError("Payload inválido: esperado JSON objeto")

    status = str(data.get("status", "")).lower().strip()
    if status != "failure":
        return ("IGNORED", "status_nao_failure")

    client = get_firestore_client()

    # Defaults do lado do servidor
    data.setdefault("analisado", False)

    ttl_days = int(os.getenv("TTL_DAYS", "300"))
    ttl_dt = _to_utc_dt(data.get("ttl_hot")) or datetime.now(timezone.utc)
    if ttl_dt <= datetime.now(timezone.utc):
        ttl_dt = datetime.now(timezone.utc) + timedelta(days=ttl_days)
    data["ttl_hot"] = ttl_dt

    if "timestamp" in data:
        data["timestamp"] = _to_utc_dt(data["timestamp"])

    # Server timestamps
    data["created_at"] = firestore.SERVER_TIMESTAMP
    data["updated_at"] = firestore.SERVER_TIMESTAMP

    # Grava
    coll = client.collection("logs_pipeline")
    result = coll.add(data)

    # Normaliza retorno para compatibilidade entre versões
    ref, write_time = _normalize_add_return(result)

    if not hasattr(ref, "id"):
        # Loga para diagnóstico e gera um erro claro
        logger.error("Retorno inesperado de Firestore add(): %r (type=%s)", result, type(result))
        raise TypeError(f"Retorno inesperado de Firestore add(): {type(result)}")

    logger.debug("Gravou doc %s em %s", ref.id, getattr(write_time, "isoformat", lambda: None)())
    return ("OK", ref.id)
