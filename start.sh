#!/bin/bash
set -e

cd django-banking-app

echo "Running Django migrations..."
python manage.py migrate --noinput || true

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Starting gunicorn..."
gunicorn banking.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120
