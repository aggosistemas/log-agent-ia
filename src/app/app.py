from flask import Flask, request, jsonify
from src.app.firestore_client import salvar_log

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def receber_log():
    try:
        data = request.get_json()
        doc_id = salvar_log(data)
        return jsonify({"message": "Log salvo com sucesso", "doc_id": doc_id}), 201
    except Exception as e:
        print(f"Erro interno: {e}")
        return jsonify({"error": "Erro interno"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

