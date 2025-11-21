"""
Banking Platform - Flask Application
Minimal production-ready entry point for Railway deployment
"""

import os
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'healthy', 'service': 'banking-platform'})
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({'message': 'Banking Platform API', 'version': '1.0.0'})
    
    # Status endpoint
    @app.route('/status', methods=['GET'])
    def status():
        return jsonify({
            'status': 'running',
            'environment': os.getenv('DEPLOYMENT_MODE', 'development'),
            'version': '1.0.0'
        })
    
    logger.info("Flask application created successfully")
    return app


# Create app at module level for gunicorn
app = create_app()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=False)
