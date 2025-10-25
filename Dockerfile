FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    postgresql-server-dev-all

# Проверяем что pg_config установлен
RUN which pg_config || echo "pg_config not found"
RUN pg_config --version || echo "pg_config not working"

COPY requirements.txt .
RUN pip install --upgrade pip

# Пробуем установить psycopg2 разными способами
RUN pip install psycopg2-binary==2.9.7 || \
    pip install psycopg2==2.9.7 || \
    echo "Failed to install psycopg2"

COPY . .
RUN mkdir -p logs

EXPOSE 5000
CMD ["python", "app.py"]