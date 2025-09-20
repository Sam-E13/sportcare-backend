FROM python:3.10-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece explícitamente la ruta de Python
ENV PYTHONPATH /app

# Copia e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# ---> PASO DE DIAGNÓSTICO <---
# Lista todos los archivos en el directorio de trabajo.
# Revisa el log de construcción de Render para ver esta salida.
RUN echo "Verificando la estructura de archivos en /app:" && ls -lR /app

# Comando para ejecutar la aplicación
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT SportCareIdet.SportCareIdet.wsgi:application"]