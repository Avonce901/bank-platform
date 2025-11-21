#!/usr/bin/env bash
set -e

echo "Starting Banking Platform..."

# Use PORT from Railway or default to 5000
PORT=${PORT:-5000}
WEB_CONCURRENCY=${WEB_CONCURRENCY:-4}

echo "Running on port $PORT with $WEB_CONCURRENCY workers"

# Start gunicorn - bind to Railway-provided $PORT
exec gunicorn \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  src.app:app
