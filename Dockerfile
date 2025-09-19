FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Puerto dinámico (Render usa variable de entorno)
# NO uses EXPOSE con $PORT, mejor manejarlo solo en el CMD

# Comando que usa la variable PORT de Render
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT --workers 3 SportCareIdet.wsgi:application"]