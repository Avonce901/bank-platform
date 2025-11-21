FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps needed to build packages / talk to Postgres if used
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Make entrypoint executable (entrypoint.sh below)
RUN chmod +x /app/entrypoint.sh

# EXPOSE is informational; container must bind to $PORT at runtime
EXPOSE 5000

# Run a shell entrypoint so $PORT is expanded at runtime
CMD ["sh", "-c", "./entrypoint.sh"]
