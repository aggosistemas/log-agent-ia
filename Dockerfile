FROM python:3.10-slim

WORKDIR /app

# Copia apenas o necessário
COPY src/requirements.txt .
COPY src/ ./src/

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn  # Recomendado para produção

ENV FLASK_APP=src.app.app
ENV PYTHONPATH=/app

EXPOSE 5000

# Usando gunicorn para produção
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app.app:app"]

# Adicione isso no final para saúde do container
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:5000/health || exit 1

# Garanta que o requirements.txt está correto
RUN pip install flask gunicorn google-cloud-firestore