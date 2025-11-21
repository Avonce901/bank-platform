"""Intuit integration routes"""
from flask import Blueprint

intuit_bp = Blueprint('intuit', __name__, url_prefix='/api/intuit')

@intuit_bp.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}
