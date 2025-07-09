FROM python:3.10-slim

WORKDIR /app

# Copiar dependências primeiro para aproveitar cache
COPY src/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copiar todo o código da aplicação
COPY src/ ./src/

# Variáveis de ambiente
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src.app.app

# Porta usada pelo Cloud Run
EXPOSE 8080

# Comando para produção
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.app:app"]

# Healthcheck (opcional, mas boa prática)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1
