FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn dj-database-url

# Copiar todo el proyecto (incluyendo settings_production.py)
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=SportCareIdet.settings_production

# Comando para Render
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 SportCareIdet.wsgi:application"]