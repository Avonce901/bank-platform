"""Bill.com integration routes"""
from flask import Blueprint

billcom_bp = Blueprint('billcom', __name__, url_prefix='/api/billcom')

@billcom_bp.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}
