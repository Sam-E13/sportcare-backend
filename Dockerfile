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

# Comando para Render (SIMPLE y FUNCIONA)
CMD python manage.py migrate && python manage.py collectstatic --noinput && python create_superuser.py && gunicorn SportCareIdet.wsgi:application --bind 0.0.0.0:$PORT