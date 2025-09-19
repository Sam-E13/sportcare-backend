FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Agregar ruta al módulo
ENV PYTHONPATH="${PYTHONPATH}:/app/SportCareIdet"

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:$PORT SportCareIdet.SportCareIdet.wsgi:application"]
