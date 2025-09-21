FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para cachear
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=SportCareIdet.settings_production

# Puerto expuesto
EXPOSE $PORT

# Comando para Render
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 SportCareIdet.wsgi:application"]