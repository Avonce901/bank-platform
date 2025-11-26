# 🚀 Bank Platform - Automated Setup Guide

## Quick Start (Choose One)

### ⚡ Option 1: Bash Quick Setup (Recommended)
**Best for:** Linux/Mac developers, fastest setup

```bash
chmod +x quick-setup.sh
./quick-setup.sh
```

**What it does:**
- ✅ Creates virtual environment
- ✅ Installs dependencies
- ✅ Creates .env file
- ✅ Runs database migrations
- ✅ Creates test data
- ✅ Ready to run locally in ~2 minutes

---

### 🐍 Option 2: Python Automated Setup
**Best for:** Cross-platform compatibility, detailed logging

```bash
python3 setup-automated.py
```

**What it does:**
- ✅ Checks all prerequisites
- ✅ Creates virtual environment with detailed status
- ✅ Installs all dependencies
- ✅ Configures environment
- ✅ Runs migrations
- ✅ Creates test data with token info
- ✅ Verifies entire setup
- ✅ Shows next steps

---

### 🐳 Option 3: Docker Setup
**Best for:** Containerized deployment, no local Python needed

```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

**What it does:**
- ✅ Builds Docker image
- ✅ Runs container with all services
- ✅ Applies migrations
- ✅ Creates test data
- ✅ App immediately available at http://localhost:8000

**Requires:** Docker Desktop installed

---

## Setup Scripts Features

### `quick-setup.sh` (Bash)
| Feature | Status |
|---------|--------|
| Speed | ⚡ Fastest |
| Platform Support | Linux, Mac, WSL2 |
| Error Recovery | ✅ Yes |
| Logging | Standard |
| Python Version Check | ✅ Yes |
| Dependency Installation | ✅ Pip |

### `setup-automated.py` (Python)
| Feature | Status |
|---------|--------|
| Speed | Standard |
| Platform Support | All (Windows, Linux, Mac) |
| Error Recovery | ✅ Detailed |
| Logging | ✅ Detailed |
| Python Version Check | ✅ Yes |
| Test Data Creation | ✅ Django ORM |

### `docker-setup.sh` (Docker)
| Feature | Status |
|---------|--------|
| Speed | Depends on internet |
| Platform Support | All (requires Docker) |
| Error Recovery | ✅ Container restart |
| Logging | ✅ Docker logs |
| Isolation | ✅ Full |
| Production Ready | ✅ Yes |

---

## Manual Setup (If Scripts Don't Work)

### Step 1: Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# or
.venv\Scripts\activate  # Windows
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Environment Configuration
```bash
cp .env.example .env
# Edit .env and set DEBUG=True for development
```

### Step 4: Database Setup
```bash
cd django-banking-app
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Test Data
```bash
python manage.py shell
```

Then in Python shell:
```python
from django.contrib.auth import get_user_model
from accounts.models import Account
from rest_framework.authtoken.models import Token
from decimal import Decimal

User = get_user_model()

# Create users and accounts...
```

### Step 6: Run Server
```bash
python manage.py runserver
```

---

## After Setup - What's Running

### Local Development
```
Django API: http://localhost:8000/api/
Admin Panel: http://localhost:8000/admin/
Database: SQLite (db.sqlite3)
```

### Test Credentials
```
User 1: sender_test / password123
Token: (shown in setup output)

User 2: receiver_test / password123
Token: (shown in setup output)
```

### Available Endpoints
```
GET    /api/accounts/                    - List accounts
POST   /api/accounts/<id>/transfer/      - Transfer funds
POST   /api/payments/create_payment_intent/ - Create Stripe payment
POST   /api/payments/confirm_payment/    - Confirm payment
GET    /api/payments/list_payments/      - Payment history
```

---

## Troubleshooting

### "Python not found"
**Solution:** Install Python 3.8+ from https://python.org

### "Permission denied" on script
```bash
chmod +x quick-setup.sh
./quick-setup.sh
```

### "No module named 'django'"
```bash
source .venv/bin/activate  # Activate venv first
pip install -r requirements.txt
```

### "Database locked"
```bash
rm django-banking-app/db.sqlite3
# Then re-run the setup script
```

### Docker container exits immediately
```bash
docker logs <container-id>
# Check the error, then:
docker run -it bank-platform:latest bash
```

---

## Deployment After Setup

### Deploy to Railway
Once local setup is complete:

1. Visit https://railway.app/dashboard
2. Create New Project → Deploy from GitHub
3. Select: Avonce901/bank-platform
4. Branch: copilot/devfixdeploy
5. Add Stripe environment variables
6. Deploy!

### Deploy to Docker Hub
```bash
docker build -t username/bank-platform:latest .
docker push username/bank-platform:latest
```

### Deploy to AWS/GCP/Azure
See individual platform docs - our Dockerfile handles all standard deployments

---

## What Each Setup Script Installs

### Core Dependencies
- Django 4.2.7
- Django REST Framework 3.14.0
- djangorestframework-simplejwt (auth)
- Stripe Python SDK
- Python-dotenv (environment config)
- Gunicorn (production WSGI)
- PostgreSQL driver (psycopg2)

### Dev Dependencies
- pytest (testing)
- flake8 (linting)
- black (formatting)

### Included Features
- ✅ Token authentication
- ✅ Account management
- ✅ Fund transfers
- ✅ Stripe payments
- ✅ Transaction history
- ✅ Virtual cards
- ✅ Migrations
- ✅ Admin panel
- ✅ API documentation

---

## Performance Notes

| Setup Method | Time | Disk Space |
|--------------|------|-----------|
| Bash Script | 2-3 min | ~500MB |
| Python Script | 2-3 min | ~500MB |
| Docker Script | 5-7 min | ~1GB |

*Times vary based on internet speed and system resources*

---

## Support

If setup fails:

1. Check requirements.txt exists
2. Verify Python 3.8+ installed
3. Check internet connection for pip packages
4. Run with verbose output: `./quick-setup.sh 2>&1 | tee setup.log`
5. Share logs in issues

---

## Next Steps After Setup

✅ **Setup complete!** Now:

1. **Start development:**
   ```bash
   cd django-banking-app
   python manage.py runserver
   ```

2. **Test locally:**
   ```bash
   curl http://localhost:8000/api/accounts/
   ```

3. **Make payments:**
   ```bash
   curl -X POST http://localhost:8000/api/payments/create_payment_intent/
   ```

4. **Deploy to production:**
   - Visit Railway dashboard
   - Add Stripe live keys
   - Go live in 5 minutes!

---

Generated: November 26, 2025
Repository: Avonce901/bank-platform
Branch: copilot/devfixdeploy
