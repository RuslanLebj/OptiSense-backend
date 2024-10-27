FROM python:3.12

# Устанавливаем системные зависимости для psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && apt-get clean

COPY pyproject.toml poetry.lock /opt/app/

WORKDIR /opt/app

RUN pip install poetry==1.8.3 && poetry config virtualenvs.create false && poetry install

VOLUME ["/opt/app"]
EXPOSE 8000
