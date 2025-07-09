FROM python:3.10-slim

WORKDIR /app

# Copia os requirements
COPY src/requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Copia o código da aplicação
COPY src/ ./src/

# Define o caminho do módulo
ENV PYTHONPATH=/app/src

# Expõe a porta que o app escuta
EXPOSE 8080

# Usa gunicorn como servidor de produção
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.app:app"]

# Verifica a saúde da aplicação a cada 30s
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1
