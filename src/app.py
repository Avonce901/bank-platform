"""
Banking Platform - Flask Application
Production-ready minimal entry point with Stripe integration verification
"""

import os
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================================
# STRIPE CONFIGURATION VERIFICATION
# ============================================================================
def verify_stripe_config():
    """Verify Stripe API key configuration at startup"""
    deployment_mode = os.getenv('DEPLOYMENT_MODE', 'development')
    stripe_key = os.getenv('STRIPE_API_KEY', '')
    
    logger.info(f"🔧 Deployment Mode: {deployment_mode}")
    
    if not stripe_key:
        logger.warning("⚠️  STRIPE_API_KEY not set - Stripe features will be disabled")
        return False
    
    # Log key prefix for verification (first 6 chars)
    key_prefix = stripe_key[:6]
    logger.info(f"✓ Stripe API Key detected: {key_prefix}...")
    
    # Verify key type matches deployment mode
    if deployment_mode == 'production':
        if stripe_key.startswith('sk_live_'):
            logger.info("✅ Production mode with LIVE Stripe key detected - READY FOR PRODUCTION")
            return True
        elif stripe_key.startswith('sk_test_'):
            logger.error("❌ DANGER: Production mode but TEST Stripe key detected!")
            logger.error("   This will process FAKE transactions in production!")
            return False
        else:
            logger.error("❌ Invalid Stripe key format")
            return False
    else:
        if stripe_key.startswith('sk_test_'):
            logger.info("✓ Development mode with TEST Stripe key")
            return True
        elif stripe_key.startswith('sk_live_'):
            logger.warning("⚠️  Development mode with LIVE key - transactions are REAL")
            return True
        else:
            logger.error("❌ Invalid Stripe key format")
            return False

# Initialize Stripe at app startup
stripe_ready = verify_stripe_config()

# ============================================================================
# REGISTER DEV-ONLY BLUEPRINTS
# ============================================================================
try:
    import sys
    from pathlib import Path
    # Add project root to path for cards blueprint
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    from cards.flask_views import cards_bp
    app.register_blueprint(cards_bp)
    logger.info("✓ Registered dev-only cards blueprint at /cards/*")
except Exception as e:
    logger.warning(f"⚠️  Could not register cards blueprint: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'deployment_mode': os.getenv('DEPLOYMENT_MODE', 'unknown'),
        'stripe_configured': stripe_ready
    })

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        'message': 'Banking Platform API',
        'version': '1.0.0',
        'deployment_mode': os.getenv('DEPLOYMENT_MODE', 'development'),
        'endpoints': [
            '/health - Health check',
            '/status - Service status',
            '/config - Configuration status'
        ]
    })

@app.route('/status', methods=['GET'])
def status():
    """Service status endpoint"""
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'deployment_mode': os.getenv('DEPLOYMENT_MODE', 'development'),
        'stripe_ready': stripe_ready
    })

@app.route('/config', methods=['GET'])
def config():
    """Configuration status endpoint"""
    deployment_mode = os.getenv('DEPLOYMENT_MODE', 'unknown')
    stripe_key = os.getenv('STRIPE_API_KEY', '')
    
    return jsonify({
        'deployment_mode': deployment_mode,
        'stripe_key_type': 'live' if stripe_key.startswith('sk_live_') else ('test' if stripe_key.startswith('sk_test_') else 'not_set'),
        'stripe_key_prefix': stripe_key[:6] if stripe_key else 'N/A',
        'stripe_configured': bool(stripe_key),
        'stripe_ready': stripe_ready
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
