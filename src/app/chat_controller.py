from flask import Blueprint, request, jsonify
from src.firestore.consultar_sumarios import buscar_sumarios_recentes
from src.llm.responder import responder_ia

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/chat", methods=["POST"])
def responder_chat():
    try:
        dados = request.get_json()
        pergunta = dados.get("mensagem")

        if not pergunta:
            return jsonify({"erro": "Mensagem não fornecida"}), 400

        sumarios = buscar_sumarios_recentes(limit=5)
        contexto = "\n".join([f"{s['timestamp']}: {s['sumario']}" for s in sumarios])

        resposta = responder_ia(pergunta, contexto)
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500
