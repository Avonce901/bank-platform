web: cd django-banking-app && python manage.py collectstatic --noinput --clear 2>/dev/null || true; gunicorn banking.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --max-requests 100
