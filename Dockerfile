FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq5 \
    curl \
    wget \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY pyproject.toml .
COPY requirements.txt .

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем папку для логов
RUN mkdir -p logs

# Используем gunicorn для запуска
CMD ["gunicorn","--bind", "0.0.0.0:5000","--workers", "2","--threads", \
    "2","--worker-class", "gthread","--max-requests", "300","--max-requests-jitter", \
    "50","--timeout", "90","app:app"]