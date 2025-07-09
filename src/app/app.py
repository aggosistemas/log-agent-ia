from flask import Flask
from app.chat_controller import chat_bp


app = Flask(__name__)

# Rotas registradas via Blueprint
app.register_blueprint(chat_bp)

# Rota de verificação de saúde
@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
