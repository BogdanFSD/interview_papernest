#!/bin/bash

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
