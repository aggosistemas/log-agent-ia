from flask import Blueprint, request, jsonify
from firestore.consultar_sumarios import buscar_sumarios_recentes
from llm.responder import responder_ia

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        pergunta = data.get("mensagem")

        if not pergunta:
            return jsonify({"erro": "Campo 'mensagem' é obrigatório"}), 400

        sumarios = buscar_sumarios_recentes(limit=5)
        resposta = responder_ia(pergunta, sumarios)

        return jsonify({"resposta": resposta}), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
