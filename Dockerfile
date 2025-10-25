FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей для psycopg2
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Обновление pip
RUN pip install --upgrade pip setuptools wheel

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .
RUN mkdir -p logs

EXPOSE 5000
CMD ["python", "app.py"]