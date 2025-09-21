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

# Copiar todo el proyecto
COPY . .

# Variables de entorno
ENV PYTHONPATH=/app

# Crear settings para producción
RUN echo "from .settings import *\n\
import os\n\
import dj_database_url\n\
\n\
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)\n\
DEBUG = os.environ.get('DEBUG', 'False') == 'True'\n\
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')\n\
\n\
DATABASE_URL = os.environ.get('DATABASE_URL')\n\
if DATABASE_URL:\n\
    DATABASES = {\n\
        'default': dj_database_url.config(\n\
            default=DATABASE_URL,\n\
            conn_max_age=600,\n\
            ssl_require=True\n\
        )\n\
    }\n\
\n\
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')\n\
" > SportCareIdet/settings_production.py

# Para producción
ENV DJANGO_SETTINGS_MODULE=SportCareIdet.settings_production

# Comando para Render
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 SportCareIdet.wsgi:application"]