FROM python:3.10-slim

WORKDIR /app

# Usa o requirements.txt correto da raiz
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

EXPOSE 8080

CMD ["python", "-m", "app.app"]
