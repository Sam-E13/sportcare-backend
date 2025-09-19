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

# Comando corregido para Render
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT SportCareIdet.SportCareIdet.wsgi:application"]
