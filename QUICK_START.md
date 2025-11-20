# Bank Platform - Quick Start Guide

## What You Have

✅ **Complete Banking Platform** with:
- Flask REST API
- PDF extraction module
- Excel generation module
- Takeoff calculator
- Streamlit admin dashboard
- Comprehensive test suite
- Docker containerization
- GitHub repository with CI/CD
- Sample data (accounts, transactions, users)

---

## Quick Start Commands

### 1. Run the API Server
```powershell
cd $env:USERPROFILE\bank_platform
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m src.api.main
```
**Access:** http://localhost:5000

### 2. Run Admin Dashboard (separate terminal)
```powershell
cd $env:USERPROFILE\bank_platform
.\venv\Scripts\Activate.ps1
streamlit run admin_panel.py
```
**Access:** http://localhost:8501

### 3. Run Tests
```powershell
pytest
pytest --cov=src  # With coverage report
```

### 4. Run with Docker
```powershell
docker-compose up --build
```

### 5. Initialize Sample Data
```powershell
python init_data.py
```

---

## Project Locations

**Local:** `C:\Users\antho\bank_platform`

**GitHub:** https://github.com/Avonce901/bank-platform

**Zip Archive:** `C:\Users\antho\bank_platform.zip`

---

## GitHub Features Enabled

✅ Project description and topics
✅ CI/CD pipeline (.github/workflows/ci-cd.yml)
✅ Branch protection on main
✅ Automated testing on push
✅ Docker build verification

---

## What Each Module Does

| Module | Purpose | Files |
|--------|---------|-------|
| API | Flask REST server | src/api/main.py, routes.py |
| PDF Extractor | Extract data from PDFs | src/modules/pdf_extractor/ |
| Excel Generator | Create Excel reports | src/modules/excel_generator/ |
| Takeoff Calculator | Calculate project takeoffs | src/modules/takeoff_calculator/ |
| Admin Panel | Streamlit dashboard | admin_panel.py |
| Tests | Unit & integration tests | tests/ |

---

## Next Steps - Choose One

### For Development:
1. Make changes to `src/` modules
2. Write tests in `tests/`
3. Run `pytest` to validate
4. `git push` to trigger CI/CD

### For Deployment:
1. Set up Docker (if not installed)
2. Configure `.env` for production
3. Run `docker-compose up`
4. Deploy to cloud (AWS, Azure, GCP, etc.)

### For Collaboration:
1. Invite collaborators on GitHub
2. Create issues and milestones
3. Set up pull request templates
4. Configure branch protection rules

### For Documentation:
1. Update README.md
2. Add API documentation
3. Create wiki pages on GitHub
4. Set up GitHub Pages

---

## Useful Commands

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run API
python -m src.api.main

# Run admin panel
streamlit run admin_panel.py

# Run all tests
pytest

# Run specific test
pytest tests/test_api.py::TestHealthCheck

# Generate coverage report
pytest --cov=src --cov-report=html

# Git commands
git status
git log --oneline
git push origin main
git pull origin main

# Docker commands
docker-compose up --build
docker-compose down
docker logs bank_platform_api
```

---

## Support Files

- **README.md** - Full project documentation
- **GITHUB_PUSH_GUIDE.md** - GitHub setup instructions
- **POWERSHELL_CLEANUP.md** - PowerShell profile cleanup
- **.env.example** - Environment variable template
- **requirements.txt** - Python dependencies

---

## Still Need Help?

1. Check the README.md in your project
2. Review the GitHub Actions page for CI/CD status
3. Look at test examples in tests/
4. Review src/api/routes.py for API endpoints

**Happy coding!** 🚀
