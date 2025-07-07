# Usar imagem oficial do Python
FROM python:3.10-slim

# Diretório de trabalho
WORKDIR /app

# Copiar todos os arquivos
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta usada pelo Flask
EXPOSE 5000

# Executar diretamente o app com Python
CMD ["python", "app/app.py"]