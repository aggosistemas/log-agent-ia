import logging
from flask import Flask, request, jsonify
from firestore_client import save_pipeline_log

# Configuração do logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("pequi-logs")

app = Flask(__name__)

@app.route("/logs", methods=["POST"])
def ingest_logs():
    try:
        payload = request.get_json()
        logger.debug(f"Payload recebido: {payload}")

        if not payload:
            logger.error("Payload vazio ou inválido")
            return jsonify({"status": "error", "reason": "invalid_payload"}), 400

        # Agora grava todos os status (success, failure, cancelled, etc.)
        status, info = save_pipeline_log(payload)
        logger.info(f"Log gravado com sucesso no Firestore: {info}")

        return jsonify({"status": status, "doc_id": info}), 202

    except Exception as e:
        logger.exception("Erro ao processar /logs")
        return jsonify({"status": "error", "reason": str(e)}), 500


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
