# Bank Platform - Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [Production Considerations](#production-considerations)

---

## Local Development

### Prerequisites
- Python 3.10+
- pip
- Virtual environment

### Setup

```bash
# Clone repository
git clone https://github.com/Avonce901/bank-platform.git
cd bank_platform

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
python -c "from src.database.service import init_database; init_database()"

# Run the application
python src/api/main.py
```

**API will be available at:** `http://localhost:5000`

### Database

**Default:** SQLite (for development)
```
DATABASE_URL=sqlite:///./bank_platform.db
```

**PostgreSQL (Recommended for production):**
```
DATABASE_URL=postgresql://user:password@localhost:5432/bank_platform
```

---

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start containers
docker-compose up --build

# Access the application
# API: http://localhost:5000
# Admin Panel: http://localhost:8501
```

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/bank_platform

# API
API_HOST=0.0.0.0
API_PORT=5000

# Redis
REDIS_URL=redis://redis:6379

# Admin Panel
STREAMLIT_SERVER_PORT=8501
```

### Docker Build Only

```bash
# Build image
docker build -t bank-platform:latest .

# Run container
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://... \
  bank-platform:latest
```

### Stop Containers

```bash
docker-compose down
```

---

## AWS Deployment

### Option 1: AWS Elastic Beanstalk

**Prerequisites:**
- AWS Account
- AWS CLI installed
- Docker

**Setup:**

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p docker bank-platform

# Create environment
eb create bank-platform-prod

# Deploy
eb deploy

# View logs
eb logs

# Get URL
eb open
```

**Environment Variables:**

In AWS Console:
1. Go to Elastic Beanstalk → Environments → Your Environment
2. Click Configuration
3. Add environment variables under "Software"

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Option 2: AWS RDS + ECS

**1. Create RDS Database:**

```bash
aws rds create-db-instance \
  --db-instance-identifier bank-platform-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123 \
  --allocated-storage 20
```

**2. Create ECR Repository:**

```bash
aws ecr create-repository --repository-name bank-platform

# Get login token
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

# Build and push image
docker build -t bank-platform:latest .
docker tag bank-platform:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/bank-platform:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/bank-platform:latest
```

**3. Create ECS Cluster:**

```bash
aws ecs create-cluster --cluster-name bank-platform-cluster
```

**4. Update docker-compose.yml for AWS:**

```yaml
version: '3.8'
services:
  api:
    image: 123456789.dkr.ecr.us-east-1.amazonaws.com/bank-platform:latest
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://admin:pwd@bank-platform-db.xxx.us-east-1.rds.amazonaws.com:5432/bank_platform
      REDIS_URL: redis://elasticache-endpoint:6379
    depends_on:
      - postgres
```

---

## Heroku Deployment

### Prerequisites
- Heroku Account
- Heroku CLI installed
- Git repository

### Setup

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create bank-platform

# Add Procfile (already in repo)
# Contents: web: gunicorn src.api.main:app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis addon
heroku addons:create heroku-redis:premium-0

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# View logs
heroku logs --tail

# Get app URL
heroku open
```

### Scaling

```bash
# View current dyos
heroku ps

# Scale web dynos
heroku ps:scale web=2

# Scale worker dynos (if needed)
heroku ps:scale worker=1

# Monitor
heroku logs --tail
```

---

## Production Considerations

### 1. Security

**Environment Variables:**
```bash
# Use strong secret key
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(50))')

# Store in secure location (AWS Secrets Manager, HashiCorp Vault, etc.)
```

**HTTPS/SSL:**
```bash
# Use Let's Encrypt for free SSL
# Cloudflare for DNS + SSL

# In production, ensure:
- SSL_REDIRECT=True
- HSTS headers enabled
- CORS configured properly
```

**Database Security:**
```bash
# Use strong passwords
# Enable SSL for database connections
# Use VPC for database isolation
# Enable encryption at rest

# In connection string:
postgresql+psycopg2://user:pwd@host/db?sslmode=require
```

### 2. Database Optimization

**Backups:**
```bash
# PostgreSQL backup
pg_dump bank_platform > backup.sql

# Restore
psql bank_platform < backup.sql

# For AWS RDS - Enable automated backups
aws rds modify-db-instance \
  --db-instance-identifier bank-platform-db \
  --backup-retention-period 7
```

**Connection Pooling:**
```python
# In config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### 3. Monitoring & Logging

**Application Logs:**
```bash
# View application logs
docker logs bank_platform_api

# Send to CloudWatch
# Add to docker-compose.yml:
logging:
  driver: awslogs
  options:
    awslogs-group: /ecs/bank-platform
    awslogs-region: us-east-1
```

**Database Monitoring:**
```bash
# Enable slow query logs
# Monitor connections
# Set up alerts for resource usage
```

### 4. Performance Optimization

**Caching:**
```python
# Use Redis for session caching
# Cache API responses
# Cache database queries

# In routes:
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/api/v1/status')
@cache.cached(timeout=60)
def status():
    return jsonify({'status': 'ok'})
```

**Rate Limiting:**
```python
# Use Flask-Limiter
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: g.user_id)

@api_bp.route('/transfer', methods=['POST'])
@limiter.limit("5 per minute")
def transfer():
    # ...
```

### 5. Disaster Recovery

**Backup Strategy:**
- Daily automated backups
- Weekly full backups
- Test restore procedures
- Geographic redundancy (cross-region)

**High Availability:**
```yaml
# Use multiple instances
version: '3.8'
services:
  api-1:
    image: bank-platform:latest
    ports: ["5001:5000"]
  api-2:
    image: bank-platform:latest
    ports: ["5002:5000"]
  
  # Load balancer
  nginx:
    image: nginx:latest
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

### 6. Compliance & Auditing

**Audit Trail:**
- Log all transactions
- Track user actions
- Store in separate ledger table
- Enable database auditing

**Data Privacy:**
- Encrypt sensitive fields
- Implement data retention policies
- GDPR compliance (right to be forgotten)
- PCI DSS for payment handling

### 7. Testing Before Production

```bash
# Run all tests
pytest --cov=src

# Load testing
# Use locust or Apache JMeter
locust -f locustfile.py --host=http://localhost:5000

# Security testing
# Use OWASP ZAP or Burp Suite
```

---

## Troubleshooting

### API won't start
```bash
# Check logs
docker logs bank_platform_api

# Verify database connection
flask db migrate
flask db upgrade

# Check environment variables
printenv | grep DATABASE_URL
```

### Database connection errors
```bash
# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql postgresql://user:password@host:5432/db

# Check Django connections
python -c "from src.database.service import get_db_service; db = get_db_service(); db.init_db()"
```

### Performance issues
```bash
# Monitor resource usage
docker stats

# Check database slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

# Profile application
python -m cProfile -s cumtime src/api/main.py
```

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review logs for errors
- Check database size
- Monitor API performance

**Monthly:**
- Review security patches
- Test backups
- Update dependencies

**Quarterly:**
- Full security audit
- Load testing
- Disaster recovery drill

---

## Support

- GitHub Issues: https://github.com/Avonce901/bank-platform/issues
- Documentation: https://github.com/Avonce901/bank-platform/wiki
- Email: support@bankplatform.com

