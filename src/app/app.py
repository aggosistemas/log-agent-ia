from flask import Flask
from app.chat_controller import chat_bp
from app.log_processor import process_log_entry
from app.firestore_client import salvar_log
from flask import request, jsonify

app = Flask(__name__)
app.register_blueprint(chat_bp)


@app.route("/logs", methods=["POST"])
def receber_log():
    try:
        log_entry = request.get_json()
        processed_log = process_log_entry(log_entry)
        salvar_log(processed_log)
        return jsonify({"status": "Log processed and stored"}), 201
    except Exception as e:
        app.logger.error(f"Erro ao processar o log: {e}", exc_info=True)
        return jsonify({"error": "Erro interno"}), 500


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
