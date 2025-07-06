from flask import Flask, request, jsonify
from app.firestore_client import salvar_log

app = Flask(__name__)

@app.route("/log", methods=["POST"])
def receber_log():
    try:
        log_data = request.get_json()
        if not log_data:
            return jsonify({"error": "Payload ausente ou inválido"}), 400

        doc_id = salvar_log(log_data)
        return jsonify({"message": "Log salvo com sucesso", "doc_id": doc_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
