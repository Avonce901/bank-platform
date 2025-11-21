"""
Main Flask Application - Financial Banking API
"""

import logging
import os
from datetime import datetime

from flask import Flask, jsonify, request, g
from flask_cors import CORS

from src.config.config import get_config, Config
from src.database.schema import Database
from src.integrations.billcom_routes import billcom_bp
from src.integrations.intuit_routes import intuit_bp
from src.utils.utilities import (
    rate_limit, ResponseFormatter, RateLimiter, MetricsCollector
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def create_app(config=None):
    """Create and configure Flask application"""
    
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    
    app.config.from_object(config)
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
    
    # Initialize database
    try:
        db = Database(app.config['DATABASE_PATH'])
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Enable CORS
    cors_origins = app.config.get('CORS_ORIGINS', ['*'])
    CORS(app, resources={r"/api/*": {"origins": cors_origins}})
    
    # Register Bill.com integration
    app.register_blueprint(billcom_bp)
    logger.info("Bill.com integration registered")
    
    # Register Intuit/QuickBooks integration
    app.register_blueprint(intuit_bp)
    logger.info("Intuit/QuickBooks integration registered")
    
    # Request hooks
    @app.before_request
    def before_request():
        """Before request hook"""
        g.start_time = datetime.now()
        g.request_id = request.headers.get('X-Request-ID', 'unknown')
        
        # Log request
        logger.info(f"Request: {request.method} {request.path} - ID: {g.request_id}")
    
    @app.after_request
    def after_request(response):
        """After request hook"""
        if hasattr(g, 'start_time'):
            duration = (datetime.now() - g.start_time).total_seconds()
            logger.info(f"Response: {response.status_code} - Duration: {duration:.3f}s")
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler"""
        return ResponseFormatter.error('Endpoint not found', 404)
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler"""
        logger.error(f"Internal server error: {error}")
        return ResponseFormatter.error('Internal server error', 500)
    
    @app.errorhandler(403)
    def forbidden(error):
        """403 error handler"""
        return ResponseFormatter.error('Forbidden', 403)
    
    @app.errorhandler(401)
    def unauthorized(error):
        """401 error handler"""
        return ResponseFormatter.error('Unauthorized', 401)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Application health check"""
        return jsonify({
            'status': 'healthy',
            'service': 'financial-api',
            'environment': app.config['ENV'],
            'timestamp': datetime.now().isoformat()
        }), 200
    
    # Configuration endpoint
    @app.route('/config', methods=['GET'])
    def get_configuration():
        """Get application configuration (safe values only)"""
        return jsonify(app.config.get('to_dict', lambda: {})()), 200
    
    # Metrics endpoint
    @app.route('/metrics', methods=['GET'])
    def get_metrics():
        """Get application metrics"""
        return jsonify({
            'metrics': MetricsCollector.get_metrics(),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    # API status endpoint
    @app.route('/api/status', methods=['GET'])
    @rate_limit(limit=100, window=3600)
    def api_status():
        """API status endpoint"""
        return ResponseFormatter.success({
            'service': 'financial-api',
            'version': '1.0.0',
            'status': 'operational',
            'features': {
                'plaid': app.config.get('ENABLE_PLAID', False),
                'stripe': app.config.get('ENABLE_STRIPE', False),
                'webhooks': app.config.get('ENABLE_WEBHOOK', False),
            }
        })
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint"""
        return ResponseFormatter.success({
            'message': 'Financial Banking API',
            'version': '1.0.0',
            'docs': '/docs',
            'health': '/health',
            'status': '/api/status'
        })
    
    logger.info(f"Flask application created - Environment: {app.config['ENV']}")
    
    return app


# Create the application at module level for gunicorn
app = create_app()


if __name__ == '__main__':
    app = create_app()
    
    config = get_config()
    
    logger.info(f"Starting application on {config.HOST}:{config.PORT}")
    
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=False,
        use_reloader=False
    )
