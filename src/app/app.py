# app.py
from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from flask import Flask, jsonify, request

from firestore_client import save_pipeline_log

app = Flask(__name__)
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("pequi-logs")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ensure_stack_hash(payload: Dict[str, Any]) -> None:
    """Gera stack_hash se não vier no payload."""
    if payload.get("stack_hash"):
        return
    repo = payload.get("repo", "")
    workflow = payload.get("workflow", "")
    job = payload.get("job", "")
    status = payload.get("status", "")
    git_sha = str(payload.get("git_sha", ""))[:8]
    base = f"{repo}|{workflow}|{job}|{status}|{git_sha}"
    payload["stack_hash"] = _sha256(base)


def _ensure_defaults(payload: Dict[str, Any]) -> None:
    """Campos padrão amistosos para o contrato."""
    payload.setdefault("service", "github-actions")
    payload.setdefault("mensagem_curta", f"Execução {payload.get('status','').lower()} em {payload.get('workflow','')}/{payload.get('job','')}")
    payload.setdefault("tipo_erro", "BUILD")

    # timestamp de origem (informativo)
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "pequi-logs-bridge"}), 200


@app.post("/logs")
def ingest_logs():
    """
    Recebe um JSON (objeto) com dados do pipeline.
    - Gera stack_hash se faltar.
    - Completa defaults do contrato.
    - Persiste em Firestore somente quando status == 'failure'.
    Respostas:
      * 201 -> persistido (OK)
      * 202 -> ignorado (não-falha)
      * 400 -> payload inválido
      * 500 -> erro interno
    """
    try:
        if not request.data:
            return jsonify({"error": "payload vazio"}), 400

        try:
            payload = request.get_json(force=True, silent=False)
        except Exception:
            # loga amostra para debugging
            sample = request.data[:200].decode("utf-8", errors="ignore")
            logger.exception("JSON inválido recebido. Amostra=%s", sample)
            return jsonify({"error": "JSON inválido"}), 400

        if not isinstance(payload, dict):
            return jsonify({"error": "esperado objeto JSON"}), 400

        # Enriquecimento leve no bridge
        _ensure_stack_hash(payload)
        _ensure_defaults(payload)

        status, info = save_pipeline_log(payload)

        if status == "IGNORED":
            # Não é falha → não persiste (mas retorna 202 para não quebrar a pipeline)
            return jsonify({"status": "ignored", "reason": info}), 202

        # Persistido
        return jsonify({"status": "ok", "doc_id": info}), 201

    except Exception as e:
        logger.exception("Erro ao processar /logs: %s", e)
        return jsonify({"error": "erro_interno", "detail": str(e)}), 500


if __name__ == "__main__":
    # Para rodar local: `python app.py`
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
