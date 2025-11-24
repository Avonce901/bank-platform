"""
Cards API Routes
DEV endpoint for wallet provisioning payloads
"""
from flask import Blueprint, jsonify, request
from src.database.service import get_db_service

# Best-effort import; adjust if your project places VirtualCard elsewhere
try:
    from src.database.models import VirtualCard
except Exception:
    VirtualCard = None

cards_bp = Blueprint('cards', __name__, url_prefix='/api/v1/cards')
db_service = get_db_service()


@cards_bp.route('/<card_id>/wallet_payload', methods=['GET'])
def get_wallet_payload(card_id):
    """
    DEV endpoint: return a simulated wallet provisioning payload for a given VirtualCard.
    In production this would be a token or pass signed by the tokenization provider.
    """
    if VirtualCard is None:
        return jsonify({
            "error": "VirtualCard model not found. Update import path."
        }), 500

    try:
        session = db_service.session
        card = session.query(VirtualCard).filter(VirtualCard.id == card_id).first()
        
        if not card:
            return jsonify({
                "error": "Card not found"
            }), 404

        payload = {
            "card_id": card.id,
            "cardholder_name": getattr(card, "cardholder_name", "Unknown"),
            "last4": getattr(card, "last4", None),
            "exp_month": getattr(card, "exp_month", None),
            "exp_year": getattr(card, "exp_year", None),
            "provisioning_token": getattr(card, "provisioning_token", "sim-token-placeholder"),
            "wallet_instructions": "This is a simulated payload. Use real provider tokens for real wallets.",
        }
        return jsonify(payload), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to fetch wallet payload: {str(e)}"
        }), 500
