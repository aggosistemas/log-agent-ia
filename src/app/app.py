from flask import Flask, request, jsonify, render_template_string
from app.log_processor import process_log_entry
from app.firestore_client import salvar_log
from firestore.consultar_sumarios import buscar_sumarios_recentes
from llm.responder import responder_ia

app = Flask(__name__)

# HTML simples para interação com o chat
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>IA Log Agent</title>
</head>
<body>
  <h1>Chat com o Agente de IA</h1>
  <form method="post" action="/chat">
    <input type="text" name="mensagem" placeholder="Digite sua pergunta" style="width: 300px;" />
    <button type="submit">Enviar</button>
  </form>
  {% if resposta %}
    <p><strong>Resposta:</strong> {{ resposta }}</p>
  {% endif %}
</body>
</html>
"""

@app.route("/logs", methods=["POST"])
def receive_log():
    try:
        log_entry = request.get_json()
        processed_log = process_log_entry(log_entry)
        salvar_log(processed_log)
        return jsonify({"status": "Log processed and stored"}), 201
    except Exception as e:
        app.logger.error(f"Erro ao processar o log: {e}")
        return jsonify({"error": "Erro interno"}), 500

@app.route("/chat", methods=["POST"])
def chat_post():
    try:
        if request.is_json:
            data = request.get_json()
            pergunta = data.get("mensagem", "")
        else:
            pergunta = request.form.get("mensagem", "")

        if not pergunta:
            return jsonify({"erro": "Campo 'mensagem' é obrigatório"}), 400

        contexto = buscar_sumarios_recentes()
        resposta = responder_ia(pergunta, contexto)

        if request.is_json:
            return jsonify({"resposta": resposta})
        else:
            return render_template_string(HTML_PAGE, resposta=resposta)
    except Exception as e:
        app.logger.error(f"Erro no chat: {e}")
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
