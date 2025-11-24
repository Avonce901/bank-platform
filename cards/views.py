from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET

# Best-effort import; adjust if your project places VirtualCard elsewhere
try:
    from cards.models import VirtualCard
except Exception:
    VirtualCard = None

@require_GET
def get_wallet_payload(request, card_id):
    """
    DEV endpoint: return a simulated wallet provisioning payload for a given VirtualCard.
    In production this would be a token or pass signed by the tokenization provider.
    """
    if VirtualCard is None:
        return JsonResponse({"error": "VirtualCard model not found. Update import path."}, status=500)

    try:
        card = VirtualCard.objects.get(pk=card_id)
    except VirtualCard.DoesNotExist:
        raise Http404("Card not found")

    payload = {
        "card_id": card.id,
        "cardholder_name": getattr(card, "cardholder_name", str(card.account.owner)),
        "last4": getattr(card, "last4", None),
        "exp_month": getattr(card, "exp_month", None),
        "exp_year": getattr(card, "exp_year", None),
        "provisioning_token": getattr(card, "provisioning_token", "sim-token-placeholder"),
        "wallet_instructions": "This is a simulated payload. Use real provider tokens for real wallets.",
    }
    return JsonResponse(payload)
