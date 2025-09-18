FROM python:3.11-slim-buster

# Establecer variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python PRIMERO (para mejor caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn  # ← ¡Importante! Servidor para producción

# Copiar el proyecto DESPUÉS de instalar dependencias
COPY . .

# Colectar archivos estáticos (necesario para producción)
RUN python manage.py collectstatic --noinput

# Puerto expuesto
EXPOSE 8000

# Comando para PRODUCCIÓN (usando Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "SportCareIdet.wsgi:application"]