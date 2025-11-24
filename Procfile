web: cd django-banking-app && python manage.py migrate --noinput 2>/dev/null || true; gunicorn banking.wsgi:application --bind 0.0.0.0:$PORT --workers 1
