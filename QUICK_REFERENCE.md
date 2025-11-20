# Bank Platform - Quick Reference Card

## 🚀 Start the API

```bash
cd C:\Users\antho\bank_platform
python src/api/main.py
```
**Access:** http://localhost:5000

---

## 🔐 Quick Authentication

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@test.com","password":"pass123"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass123"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:5000/api/v1/banking/accounts
```

---

## 💳 Banking API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/banking/accounts` | List accounts |
| POST | `/api/v1/banking/transfer` | Send money |
| POST | `/api/v1/banking/deposit` | Deposit |
| POST | `/api/v1/banking/withdrawal` | Withdraw |
| GET | `/api/v1/banking/statement/ID` | Export statement |

---

## 📊 Business Operations

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/extract-pdf` | Extract from PDF |
| POST | `/api/v1/generate-excel` | Create report |
| POST | `/api/v1/calculate-takeoff` | Calculate costs |

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_api.py

# With coverage
pytest --cov=src

# Quick module test
python test_api.py
```

---

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker logs bank_platform_api

# Access inside container
docker exec -it bank_platform_api bash
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/api/main.py` | Flask application |
| `src/api/routes.py` | Core endpoints |
| `src/api/banking_routes.py` | Banking workflows |
| `src/api/auth_routes.py` | Authentication |
| `src/database/models.py` | Database schema |
| `admin_panel.py` | Dashboard UI |
| `.env.example` | Environment config |

---

## 🔧 Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

---

## 📚 Documentation

- `README.md` - Project overview
- `QUICK_START.md` - Getting started
- `API_DOCUMENTATION.md` - Full API reference
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `IMPLEMENTATION_SUMMARY.md` - Complete feature list

---

## 🎯 Common Tasks

### Create a new account
```bash
curl -X POST http://localhost:5000/api/v1/banking/accounts \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"account_type":"CHECKING","currency":"USD"}'
```

### Transfer money
```bash
curl -X POST http://localhost:5000/api/v1/banking/transfer \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from_account_id":1,
    "to_account_id":2,
    "amount":500,
    "description":"Payment"
  }'
```

### Generate report
```bash
curl -X POST http://localhost:5000/api/v1/generate-excel \
  -H "Content-Type: application/json" \
  -d '{
    "data":[{"Name":"John","Amount":1000}],
    "title":"Report"
  }' \
  -o report.xlsx
```

### Calculate project cost
```bash
curl -X POST http://localhost:5000/api/v1/calculate-takeoff \
  -H "Content-Type: application/json" \
  -d '{
    "project_name":"Building",
    "markup_percentage":15,
    "tax_rate":0.08,
    "line_items":[
      {"description":"Labor","quantity":100,"unit":"ft","unit_price":50}
    ]
  }'
```

---

## 🐛 Troubleshooting

**API won't start?**
```bash
pip install -r requirements.txt
```

**Port 5000 already in use?**
```bash
# Change port in src/api/main.py or .env
export FLASK_PORT=5001
```

**Database connection error?**
```bash
# Check DATABASE_URL in .env
# Ensure PostgreSQL is running
docker-compose up postgres
```

**Import errors?**
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
```

---

## 📊 GitHub Repository

**URL:** https://github.com/Avonce901/bank-platform

**Features:**
- ✅ Public repository
- ✅ GitHub Actions CI/CD
- ✅ Branch protection
- ✅ Complete documentation
- ✅ Test coverage
- ✅ Ready for collaboration

---

## 🎓 Learning Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- JWT Auth: https://pyjwt.readthedocs.io/
- Docker: https://docs.docker.com/
- PostgreSQL: https://www.postgresql.org/docs/

---

**Last Updated:** 2025-01-19
**Status:** ✅ Production Ready
**Version:** 1.0.0

