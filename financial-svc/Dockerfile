FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
RUN pip install --no-cache-dir pika

# Copiar código
COPY app.py .

# Comando para ejecutar el servicio
CMD ["python", "app.py"]
