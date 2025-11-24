"""
Flask blueprint for virtual card wallet provisioning endpoints.
Development/test only - provides simulated wallet provisioning payloads.
"""

from flask import Blueprint, jsonify
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Best-effort import
try:
    from src.database.models import VirtualCard
    from src.database.service import get_db_service
except Exception:
    VirtualCard = None
    get_db_service = None

# Create blueprint
cards_bp = Blueprint('cards', __name__, url_prefix='/cards')

@cards_bp.route('/<card_id>/wallet_payload/', methods=['GET'])
def get_wallet_payload(card_id):
    """
    DEV endpoint: return a simulated wallet provisioning payload for a given VirtualCard.
    In production this would be a token or pass signed by the tokenization provider.
    
    Returns:
        JSON payload with card details and simulated provisioning token
    """
    if VirtualCard is None or get_db_service is None:
        return jsonify({
            "error": "VirtualCard model or database session not available. Check imports."
        }), 500
    
    session = None
    try:
        db_service = get_db_service()
        session = db_service.get_session()
        card = session.query(VirtualCard).filter(VirtualCard.id == card_id).first()
        
        if not card:
            return jsonify({"error": "Card not found"}), 404
        
        payload = {
            "card_id": card.id,
            "cardholder_name": getattr(card, "cardholder_name", "Unknown"),
            "last4": getattr(card, "last4", None),
            "exp_month": getattr(card, "exp_month", None),
            "exp_year": getattr(card, "exp_year", None),
            "provisioning_token": getattr(card, "provisioning_token", "sim-token-placeholder"),
            "provisioned": getattr(card, "provisioned", False),
            "status": getattr(card, "status", "unknown"),
            "wallet_instructions": "This is a simulated payload. Use real provider tokens for real wallets.",
        }
        
        return jsonify(payload), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch card: {str(e)}"}), 500
    finally:
        if session:
            session.close()


@cards_bp.route('/list/', methods=['GET'])
def list_cards():
    """
    DEV endpoint: list all virtual cards.
    For development/testing only.
    """
    if VirtualCard is None or get_db_service is None:
        return jsonify({
            "error": "VirtualCard model or database session not available."
        }), 500
    
    session = None
    try:
        db_service = get_db_service()
        session = db_service.get_session()
        cards = session.query(VirtualCard).all()
        
        cards_list = []
        for card in cards:
            cards_list.append({
                "id": card.id,
                "account_id": card.account_id,
                "cardholder_name": card.cardholder_name,
                "last4": card.last4,
                "exp_month": card.exp_month,
                "exp_year": card.exp_year,
                "status": card.status,
                "provisioned": card.provisioned,
            })
        
        return jsonify({
            "count": len(cards_list),
            "cards": cards_list
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to list cards: {str(e)}"}), 500
    finally:
        if session:
            session.close()


# Integration instructions comment
"""
TO INTEGRATE THIS BLUEPRINT INTO YOUR FLASK APP:

1. Import the blueprint in your main app file:
   from cards.flask_views import cards_bp

2. Register the blueprint:
   app.register_blueprint(cards_bp)

3. The endpoints will be available at:
   - GET /cards/<card_id>/wallet_payload/
   - GET /cards/list/
"""
