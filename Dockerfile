FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PORT=5000 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies for building packages and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with verbose output for debugging
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

# Expose port (Railway will override with $PORT)
EXPOSE 5000

# Use entrypoint script to handle $PORT and start gunicorn
CMD ["sh", "-c", "./entrypoint.sh"]
