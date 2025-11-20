#!/usr/bin/env python3
"""
Bank Platform Generator - Automated setup for bank_platform project
Creates directory structure, config files, requirements, and Docker setup
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and report status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def create_directory_structure():
    """Create the project directory structure"""
    print("\n📁 Creating directory structure...")
    
    dirs = [
        "src/api",
        "src/modules/pdf_extractor",
        "src/modules/excel_generator",
        "src/modules/takeoff_calculator",
        "src/config",
        "src/utils",
        "tests/unit",
        "tests/integration",
        "docs",
        "docker",
        "scripts",
        "data/input",
        "data/output",
        ".github/workflows"
    ]
    
    for dir_path in dirs:
        full_path = Path(dir_path)
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {dir_path}")

def create_requirements_txt():
    """Create requirements.txt with dependencies"""
    requirements = """# Core API
flask==2.3.2
flask-cors==4.0.0
flask-restx==0.5.1

# PDF Processing
PyPDF2==3.0.1
pdfplumber==0.9.0
reportlab==4.0.4

# Excel Processing
openpyxl==3.1.2
pandas==2.0.2
xlsxwriter==3.1.2

# Data Processing
numpy==1.24.3
scipy==1.11.1

# Database
sqlalchemy==2.0.19
psycopg2-binary==2.9.6

# Testing
pytest==7.3.1
pytest-cov==4.1.0
pytest-mock==3.11.1

# Code Quality
black==23.7.0
flake8==6.0.0
mypy==1.4.1
pylint==2.17.4

# Utilities
python-dotenv==1.0.0
requests==2.31.0
pydantic==1.10.12
loguru==0.7.0
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements)
    print("Created requirements.txt")

def create_dockerfile():
    """Create Dockerfile for containerization"""
    dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run application
CMD ["python", "-m", "src.api.main"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile)
    print("✓ Created Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml"""
    docker_compose = """version: '3.8'

services:
  db:
    image: postgres:15-alpine
    container_name: bank_platform_db
    environment:
      POSTGRES_USER: ${DB_USER:-bankuser}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      POSTGRES_DB: ${DB_NAME:-bank_platform}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-bankuser}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: bank_platform_cache
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: bank_platform_api
    environment:
      FLASK_ENV: ${FLASK_ENV:-development}
      DATABASE_URL: postgresql://${DB_USER:-bankuser}:${DB_PASSWORD:-changeme}@db:5432/${DB_NAME:-bank_platform}
      REDIS_URL: redis://redis:6379/0
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    command: python -m src.api.main

volumes:
  postgres_data:
"""
    
    with open("docker-compose.yml", "w") as f:
        f.write(docker_compose)
    print("✓ Created docker-compose.yml")

def create_env_files():
    """Create .env and .env.example"""
    env_example = """# Database Configuration
DB_USER=bankuser
DB_PASSWORD=changeme
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bank_platform

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# File Processing
MAX_PDF_SIZE=50000000
MAX_EXCEL_SIZE=50000000
UPLOAD_FOLDER=data/input
OUTPUT_FOLDER=data/output

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
"""
    
    with open(".env.example", "w") as f:
        f.write(env_example)
    print("✓ Created .env.example")
    
    # Create .env if it doesn't exist
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write(env_example)
        print("✓ Created .env")

def create_main_files():
    """Create main Python files"""
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/api/__init__.py",
        "src/modules/__init__.py",
        "src/modules/pdf_extractor/__init__.py",
        "src/modules/excel_generator/__init__.py",
        "src/modules/takeoff_calculator/__init__.py",
        "src/config/__init__.py",
        "src/utils/__init__.py",
        "tests/__init__.py",
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
    print("✓ Created __init__.py files")
    
    # Create main API entry point
    main_api = '''"""
Bank Platform API - Main Entry Point
"""
from flask import Flask
from flask_cors import CORS
from src.config import Config
from src.api.routes import register_routes

def create_app(config_class=Config):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    register_routes(app)
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return {'status': 'healthy'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['API_HOST'],
        port=app.config['API_PORT'],
        debug=app.config['DEBUG']
    )
'''
    
    with open("src/api/main.py", "w") as f:
        f.write(main_api)
    print("✓ Created src/api/main.py")
    
    # Create routes module
    routes = '''"""
API Routes Definition
"""
from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/status', methods=['GET'])
def get_status():
    """Get API status"""
    return jsonify({'status': 'running'}), 200

@api_bp.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    """Extract data from PDF"""
    # TODO: Implement PDF extraction
    return jsonify({'message': 'PDF extraction endpoint'}), 200

@api_bp.route('/generate-excel', methods=['POST'])
def generate_excel():
    """Generate Excel file"""
    # TODO: Implement Excel generation
    return jsonify({'message': 'Excel generation endpoint'}), 200

@api_bp.route('/calculate-takeoff', methods=['POST'])
def calculate_takeoff():
    """Calculate takeoff"""
    # TODO: Implement takeoff calculation
    return jsonify({'message': 'Takeoff calculation endpoint'}), 200

def register_routes(app):
    """Register all API blueprints"""
    app.register_blueprint(api_bp)
'''
    
    with open("src/api/routes.py", "w") as f:
        f.write(routes)
    print("✓ Created src/api/routes.py")
    
    # Create config module
    config = '''"""
Application Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = os.getenv('FLASK_DEBUG', False)
    TESTING = False
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///bank_platform.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # File Processing
    MAX_PDF_SIZE = int(os.getenv('MAX_PDF_SIZE', 50000000))
    MAX_EXCEL_SIZE = int(os.getenv('MAX_EXCEL_SIZE', 50000000))
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/input')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'data/output')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
'''
    
    with open("src/config/config.py", "w") as f:
        f.write(config)
    print("✓ Created src/config/config.py")

def create_gitignore():
    """Create .gitignore"""
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
dist/
build/
*.egg-info/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.env.local
.env.*.local

# Data
data/input/*
data/output/*
*.pdf
*.xlsx
*.xls

# Docker
docker-compose.override.yml

# OS
Thumbs.db
.DS_Store
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore)
    print("✓ Created .gitignore")

def create_readme():
    """Create README.md"""
    readme = """# Bank Platform

A comprehensive banking simulation platform with API, PDF extraction, and Excel generation capabilities.

## Features

- **RESTful API**: Flask-based API for platform operations
- **PDF Processing**: Extract and process PDF documents
- **Excel Generation**: Generate formatted Excel reports
- **Takeoff Calculator**: Calculate and manage project takeoffs
- **Database**: PostgreSQL for data persistence
- **Caching**: Redis for performance optimization
- **Docker Support**: Full containerization for easy deployment

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional)
- PostgreSQL 15+ (optional if using Docker)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bank_platform
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   # or
   source venv/bin/activate      # Linux/macOS
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python -m src.api.main
   ```

### Docker Setup

```bash
docker-compose up --build
```

Access the API at `http://localhost:5000`

## Project Structure

```
bank_platform/
├── src/
│   ├── api/              # Flask API application
│   ├── modules/          # Feature modules
│   │   ├── pdf_extractor/
│   │   ├── excel_generator/
│   │   └── takeoff_calculator/
│   ├── config/           # Configuration management
│   └── utils/            # Utility functions
├── tests/                # Unit and integration tests
├── docs/                 # Documentation
├── docker/               # Docker configurations
├── scripts/              # Helper scripts
├── data/                 # Data directories
│   ├── input/            # Input files
│   └── output/           # Output files
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker image definition
└── docker-compose.yml    # Docker Compose configuration
```

## API Endpoints

### Health Check
- `GET /health` - Check API health status

### API v1
- `GET /api/v1/status` - Get API status
- `POST /api/v1/extract-pdf` - Extract data from PDF
- `POST /api/v1/generate-excel` - Generate Excel file
- `POST /api/v1/calculate-takeoff` - Calculate takeoff

## Development

### Running Tests
```bash
pytest
pytest --cov=src  # With coverage
```

### Code Quality
```bash
black src/        # Format code
flake8 src/       # Lint code
mypy src/         # Type checking
```

## Configuration

See `.env.example` for all available configuration options:
- Database credentials
- Flask settings
- File size limits
- Logging configuration

## Troubleshooting

### Database Connection Issues
Ensure PostgreSQL is running and credentials in `.env` are correct.

### Port Already in Use
Change `API_PORT` in `.env` or use `python -m src.api.main --port 5001`

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

[Your License Here]
"""
    
    with open("README.md", "w") as f:
        f.write(readme)
    print("✓ Created README.md")

def main():
    """Main setup orchestration"""
    print("""
╔════════════════════════════════════════════════════════════╗
║        Bank Platform Generator - Setup Automation          ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Create directory structure
        create_directory_structure()
        
        # Create configuration files
        print("\n📝 Creating configuration files...")
        create_requirements_txt()
        create_dockerfile()
        create_docker_compose()
        create_env_files()
        create_gitignore()
        
        # Create main application files
        print("\n📄 Creating application files...")
        create_main_files()
        create_readme()
        
        print("""
╔════════════════════════════════════════════════════════════╗
║                    ✅ Setup Complete!                      ║
╚════════════════════════════════════════════════════════════╝

📋 Next Steps:

1. Review configuration in .env
   
2. Install dependencies:
   python -m venv venv
   venv\\Scripts\\activate
   pip install -r requirements.txt

3. Run locally:
   python -m src.api.main

4. Or run with Docker:
   docker-compose up --build

5. Access API at http://localhost:5000
   Health check: http://localhost:5000/health

📚 Documentation: See README.md for more details

🚀 Happy coding!
        """)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
