FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comandos de diagnóstico
RUN echo "=== DIAGNÓSTICO DE ESTRUCTURA ===" && \
    echo "=== Directorio actual: ===" && \
    pwd && \
    echo "=== Contenido de /app: ===" && \
    ls -la && \
    echo "=== Buscando archivos críticos: ===" && \
    find . -name "manage.py" -o -name "wsgi.py" -o -name "settings.py" | head -10 && \
    echo "=== Contenido de carpeta SportCareIdet (si existe): ===" && \
    ls -la SportCareIdet/ 2>/dev/null || echo "Carpeta SportCareIdet no encontrada" && \
    echo "=== Verificando wsgi.py: ===" && \
    find . -name "wsgi.py" -exec ls -la {} \; -exec head -5 {} \; && \
    echo "=== Verificando manage.py: ===" && \
    find . -name "manage.py" -exec ls -la {} \; -exec head -5 {} \; && \
    echo "=== DIAGNÓSTICO COMPLETADO ==="

# Establecer PYTHONPATH explícitamente
ENV PYTHONPATH=/app

# Comando de diagnóstico temporal (descomenta para debug)
CMD ["sh", "-c", "echo '=== DIAGNÓSTICO FINAL ==='; echo 'PYTHONPATH: $PYTHONPATH'; echo 'Directorio actual:'; pwd; echo 'Contenido:'; ls -la; echo 'Buscando wsgi.py:'; find . -name wsgi.py; echo '=== Esperando 300 segundos para revisión ==='; sleep 300"]

# Comando de producción (comenta la línea de arriba y descomenta esta cuando funcione)
#CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:$PORT SportCareIdet.wsgi:application"]