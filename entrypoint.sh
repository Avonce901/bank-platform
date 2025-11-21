#!/usr/bin/env bash
set -e

# Optional: attempt DB migrations if flask/migrate are set up (tolerate failures)
if command -v flask >/dev/null 2>&1 && [ -n "$FLASK_APP" ]; then
  echo "Attempting to run database migrations (if configured)..."
  flask db upgrade || true
fi

# Start gunicorn binding to the Railway-provided $PORT, fallback to 5000
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" \
  --workers "${WEB_CONCURRENCY:-4}" \
  --timeout 120 \
  src.app:app
