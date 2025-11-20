"""
Bank Platform API - Main Entry Point
"""
from flask import Flask
from flask_cors import CORS
from src.config.config import Config
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
