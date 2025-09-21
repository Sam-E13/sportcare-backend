FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ESTABLECER PYTHONPATH EXPLÍCITAMENTE
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=SportCareIdet.settings

# COMANDO DEFINITIVO - Usar directamente gunicorn sin sh
CMD gunicorn --bind 0.0.0.0:${PORT:-8000} --chdir /app SportCareIdet.wsgi:application