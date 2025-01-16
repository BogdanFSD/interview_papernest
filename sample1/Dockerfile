FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl postgresql-client && \
    apt-get clean

COPY . /app/

# Ensure /app is a package by adding __init__.py
RUN touch /app/__init__.py

ENV PYTHONPATH=/app:/app/sample1

RUN pip install --no-cache-dir -r requirements.txt


CMD ["bash", "/app/entrypoint.sh"]
