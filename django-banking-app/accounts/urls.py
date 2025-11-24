"""
Django URL Configuration for accounts API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, VirtualCardViewSet, TransferViewSet, TransactionViewSet,
    get_wallet_payload, list_wallet_cards
)

app_name = 'accounts'

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'cards', VirtualCardViewSet, basename='card')
router.register(r'transfers', TransferViewSet, basename='transfer')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('cards/<int:card_id>/wallet_payload/', get_wallet_payload, name='wallet_payload'),
    path('cards/wallet_list/', list_wallet_cards, name='wallet_list'),
]
