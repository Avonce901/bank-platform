"""
WSGI entry point for production deployment
"""
import os
from src.api.main import create_app

# Set production config
os.environ.setdefault('FLASK_ENV', 'production')

app = create_app()

if __name__ == '__main__':
    app.run()
