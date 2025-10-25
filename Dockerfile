FROM ubuntu:22.04

WORKDIR /app

# Установка Python и зависимостей
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создание симлинка для python
RUN ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p logs

EXPOSE 5000
CMD ["python3", "app.py"]