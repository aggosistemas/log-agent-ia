# Imagem base leve com Python
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Copia as dependências
COPY src/requirements.txt .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copia todo o código-fonte para o contêiner
COPY src/ ./src/

# Define variáveis de ambiente
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src.app.app

# Expõe a porta padrão para Cloud Run
EXPOSE 8080

# Comando de inicialização com Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.app:app"]
