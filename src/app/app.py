import logging
logging.basicConfig(level=logging.INFO)

from flask import Flask, request, jsonify
from app.firestore_client import salvar_log
from app.log_processor import process_log_entry

app = Flask(__name__)

@app.route("/logs", methods=["POST"])
def receive_log():
    try:
        log_entry = request.get_json()
        processed_log = process_log_entry(log_entry)
        salvar_log(processed_log)
        return jsonify({"status": "Log processed and stored"}), 201
    except Exception as e:
        logging.exception("Erro ao processar o log:")
        return jsonify({"error": "Erro interno"}), 500

# ✅ Rota de verificação de saúde
@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
