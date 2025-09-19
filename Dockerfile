FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema operativo para psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "SportCareIdet.wsgi:application"]