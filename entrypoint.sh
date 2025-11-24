#!/usr/bin/env bash
set -e

# Change to Django app directory
cd django-banking-app

# Optional: attempt Django migrations if manage.py exists (tolerate failures)
if [ -f "manage.py" ]; then
  echo "Attempting to run Django database migrations (if configured)..."
  python manage.py migrate --noinput || true
fi

# Start gunicorn binding to the Railway-provided $PORT, fallback to 5000
# Use WEB_CONCURRENCY from environment or default to 4 workers
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-4}" \
  --timeout 120 \
  banking.wsgi:application
