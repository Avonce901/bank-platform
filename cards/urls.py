from django.urls import path
from .views import get_wallet_payload

urlpatterns = [
    path('cards/<int:card_id>/wallet_payload/', get_wallet_payload, name='card-wallet-payload'),
]
