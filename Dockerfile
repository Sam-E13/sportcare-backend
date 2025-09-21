FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando CORREGIDO y DEFINITIVO
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT SportCareIdet.wsgi:application"]