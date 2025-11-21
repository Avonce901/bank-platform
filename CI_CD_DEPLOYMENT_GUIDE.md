# CI/CD Pipeline & Production Deployment Guide

## Current Setup: Railway.app (Recommended for this project)

Your banking platform uses **Railway.app** for deployment, which provides:
- ✅ **Automatic builds** from git push to main
- ✅ **Built-in Docker support** (no registry needed)
- ✅ **Managed PostgreSQL & Redis**
- ✅ **Automatic HTTPS/TLS**
- ✅ **Environment variable management**
- ✅ **Auto-redeploy on variable changes**
- ✅ **Zero-downtime deployments**

---

## Deployment Flow (Current)

```
1. Developer pushes to GitHub (main branch)
   ↓
2. Railway webhook detects push
   ↓
3. Railway pulls latest code
   ↓
4. Railway builds Docker image using Dockerfile
   ↓
5. Railway runs health checks
   ↓
6. If healthy, Railway deploys new container
   ↓
7. App goes live (zero downtime)
```

---

## Your Dockerfile (Production-Optimized)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, wheel BEFORE installing requirements
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Production web server with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "src.app:app"]
```

**Why this works:**
- ✅ Python 3.11-slim = small, fast image
- ✅ System deps installed before pip (builds faster)
- ✅ Pip upgraded first (prevents version conflicts)
- ✅ Requirements cached efficiently
- ✅ Gunicorn properly configured for production (4 workers)
- ✅ Entry point correct: `src.app:app` (module:app_object)

---

## Your Current CI/CD Status

| Component | Status | Details |
|-----------|--------|---------|
| **Git Integration** | ✅ Active | Railway auto-deploys on main push |
| **Docker Build** | ✅ Ready | Optimized Dockerfile in place |
| **Unit Tests** | ⏳ Optional | No tests required to deploy |
| **Linting** | ⏳ Optional | Can add as GitHub Actions |
| **Security Scan** | ✅ Active | GitHub secret scanning enabled |
| **Environment Secrets** | ✅ Secure | Stored in Railway (not in code) |
| **Database Migrations** | ✅ Auto | SQLAlchemy handles schema |
| **Zero-downtime Deploy** | ✅ Built-in | Railway handles load balancing |

---

## Optional: GitHub Actions for Testing (Advanced)

If you want automated testing before Railway builds, add `.github/workflows/test.yml`:

```yaml
name: Test & Deploy

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Lint with flake8
        run: |
          # Stop the build if there are Python syntax errors or undefined names
          flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
          # exit-zero treats all errors as warnings
          flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
        run: |
          pytest tests/ -v --tb=short
      
      - name: Generate coverage report
        if: success()
        run: |
          pytest tests/ --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        if: success()
```

---

## Deployment Checklist

Before going to production, verify:

```
PRE-DEPLOYMENT
[ ] Code committed and pushed to main
[ ] Dockerfile builds successfully locally: docker build -t bank-platform .
[ ] Requirements.txt has no errors: pip install -r requirements.txt
[ ] No hardcoded secrets in code (GitHub scanning enabled)
[ ] All environment variables documented

PRODUCTION SETUP
[ ] Railway project created and connected to GitHub
[ ] PostgreSQL database provisioned on Railway
[ ] Redis cache provisioned on Railway
[ ] DEPLOYMENT_MODE=production set in Railway Variables
[ ] STRIPE_API_KEY=sk_live_* set in Railway Variables
[ ] STRIPE_WEBHOOK_SECRET=whsec_live_* set in Railway Variables

POST-DEPLOYMENT
[ ] Railway dashboard shows green checkmark (build success)
[ ] Application responds to GET /health with 200 OK
[ ] Stripe test charge goes through in production mode
[ ] Bill.com integration shows live data
[ ] Logs show no errors in Railway dashboard
```

---

## Rollback Procedure

If something goes wrong in production:

**Option 1: Revert Git Commit (Fastest)**
```bash
git revert <bad-commit-hash>
git push origin main
# Railway auto-redeploys old version (2-3 minutes)
```

**Option 2: Use Railway Deployments Tab**
- Go to Railway dashboard → Deployments
- Click on previous successful deployment
- Click "Redeploy"
- Railway instantly switches to that version

**Option 3: Update Environment Variables**
- If issue is config-related, update Railway Variables
- Railway auto-redeploys (30 seconds)

---

## Monitoring & Observability

### Railway Built-in Monitoring
- ✅ **Logs:** Railway dashboard shows real-time logs
- ✅ **Metrics:** CPU, memory, network visible in dashboard
- ✅ **Healthchecks:** Automatic container restarts if unhealthy

### View Logs in Railway
1. Go to Railway dashboard
2. Click your project → "Logs" tab
3. Filter by time or search by keyword

### Example Log Commands
```bash
# From local machine (if Railway CLI installed)
railway logs

# View last 100 lines
railway logs --tail 100
```

---

## Database Backup & Recovery

### Automatic Backups (Railway PostgreSQL)
Railway automatically backs up your database. To restore:

1. Go to Railway dashboard → PostgreSQL service
2. Click "..." menu → Backups
3. Select backup date → Restore

### Manual Backup
```bash
# Export database locally
pg_dump DATABASE_URL > backup_$(date +%s).sql

# Restore from backup
psql DATABASE_URL < backup_timestamp.sql
```

---

## Performance Optimization

### Current Gunicorn Configuration
```
workers: 4          (good for small to medium traffic)
timeout: 120s       (handles slow requests)
bind: 0.0.0.0:5000  (listens on all interfaces)
```

### Scale Up if Needed
Increase workers for more traffic:
```dockerfile
# For high traffic
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "120", "src.app:app"]
```

Then rebuild and deploy (git push).

---

## Next Steps

1. ✅ **Verify Railway build succeeded** (check dashboard for green checkmark)
2. ✅ **Add 3 environment variables** to Railway
3. ✅ **Wait for auto-redeploy** (2-3 minutes)
4. ✅ **Test production** (run check_railway_readiness.py)
5. ✅ **Execute live transaction** to verify Stripe integration

---

## Key Differences: Railway vs Self-Hosted

| Aspect | Railway | Self-Hosted (e.g., AWS EC2) |
|--------|---------|---------------------------|
| **Build** | Automatic on git push | Manual or CI/CD tool required |
| **Secrets** | Dashboard variables | Environment files / Vault |
| **Database** | Managed | Self-managed backups |
| **Scaling** | Click a button | Infrastructure as code |
| **Cost** | Predictable ($20/mo) | Variable (pay as you go) |
| **Complexity** | Low | High |
| **Best for** | MVP, Small projects | Large scale apps |

Railway is perfect for your use case! 🚀

