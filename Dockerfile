FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=5000

WORKDIR /app

# Install system dependencies for building packages and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose port (Railway will override with $PORT)
EXPOSE 5000

# Use entrypoint script to handle $PORT and start gunicorn
CMD ["sh", "-c", "./entrypoint.sh"]
