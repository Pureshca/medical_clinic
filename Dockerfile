FROM python:3.11-slim

WORKDIR /app

# Установка ВСЕХ необходимых системных зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    make \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Обновление pip
RUN pip install --upgrade pip setuptools wheel

# Копирование requirements.txt
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остального кода
COPY . .

# Создание директории для логов
RUN mkdir -p logs

EXPOSE 5000

CMD ["python", "app.py"]