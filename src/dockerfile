# Usar imagem oficial do Python
FROM python:3.10-slim

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta da aplicação Flask
EXPOSE 5000

# Definir variável de ambiente do flask
ENV FLASK_APP=app.app

# Comando para iniciar a aplicação Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]