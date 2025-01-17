#!/bin/bash
set -e

export PYTHONPATH=/sample1

echo "Listing the directory structure, excluding 'venv' directories..."
find /sample1 -type d -name "venv" -prune -o -print


echo "Waiting for database to be ready..."
until pg_isready -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB; do
  sleep 1
done
echo "Partitioning and loading data into the database..."
python /sample1/partition_and_load.py

echo "Running tests..."
pytest /sample1/test || echo "Tests failed or directory not found"

echo "Starting the Flask server..."
flask run --host=0.0.0.0 --port=5000
