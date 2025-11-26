from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AccountViewSet,
    VirtualCardViewSet,
    TransferViewSet,
    TransactionViewSet,
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='accounts')
router.register(r'cards', VirtualCardViewSet, basename='cards')
router.register(r'transfers', TransferViewSet, basename='transfers')
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    path('', include(router.urls)),
]