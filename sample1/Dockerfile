FROM python:3.11-slim

WORKDIR /sample1

RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl postgresql-client && \
    apt-get clean

COPY . /sample1/

# Ensure /app is a package by adding __init__.py
RUN touch /sample1/__init__.py

ENV PYTHONPATH=/sample1

RUN pip install --no-cache-dir -r requirements.txt


CMD ["bash", "/app/entrypoint.sh"]
