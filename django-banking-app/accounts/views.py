"""
Django REST Framework Views
Account Management, Transfers, Deposits, Virtual Cards
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db import transaction, models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal
import stripe
import logging

from .models import Account, Transaction, VirtualCard, CardTransaction, Transfer
from .serializers import (
    AccountSerializer, AccountDetailedSerializer, TransactionSerializer,
    VirtualCardSerializer, TransferSerializer, TransferCreateSerializer,
    DepositSerializer, VirtualCardCreateSerializer, StripeDepositSerializer
)
# Celery tasks disabled - using synchronous operations only

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.ModelViewSet):
    """Account management endpoints"""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        """Return accounts for current user"""
        return Account.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AccountDetailedSerializer
        return AccountSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's accounts"""
        accounts = self.get_queryset()
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def balance(self, request, pk=None):
        """Get account balance"""
        account = self.get_object()
        return Response({
            'id': account.id,
            'name': account.name,
            'account_number': account.account_number,
            'balance': str(account.balance),
            'updated_at': account.updated_at
        })
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer funds to another account"""
        sender_account = self.get_object()
        serializer = TransferCreateSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                receiver_account = serializer.validated_data['receiver_account']
                amount = serializer.validated_data['amount']
                description = serializer.validated_data.get('description', '')
                
                # Deduct from sender
                sender_account.balance -= amount
                sender_account.save()
                
                # Add to receiver
                receiver_account.balance += amount
                receiver_account.save()
                
                # Create transfer record
                transfer = Transfer.objects.create(
                    sender=sender_account,
                    receiver=receiver_account,
                    amount=amount,
                    description=description,
                    status='completed'
                )
                transfer.completed_at = timezone.now()
                transfer.save()
                
                # Create transactions
                Transaction.objects.create(
                    account=sender_account,
                    transaction_type='transfer',
                    status='completed',
                    amount=-amount,
                    description=(
                        f"Transfer to {receiver_account.name}"
                    ),
                    related_account=receiver_account,
                    balance_after=sender_account.balance
                )
                
                Transaction.objects.create(
                    account=receiver_account,
                    transaction_type='transfer',
                    status='completed',
                    amount=amount,
                    description=(
                        f"Transfer from {sender_account.name}"
                    ),
                    related_account=sender_account,
                    balance_after=receiver_account.balance
                )
                
                # Send notifications asynchronously (disabled - Celery not installed)
                # send_transfer_notification.delay(
                #     transfer_id=transfer.id,
                #     sender_email=sender_account.user.email,
                #     receiver_email=receiver_account.user.email
                # )
                
                transfer_serializer = TransferSerializer(transfer)
                return Response(transfer_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Transfer error: {str(e)}")
            return Response(
                {'error': 'Transfer failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """Manual deposit to account"""
        account = self.get_object()
        serializer = DepositSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                amount = serializer.validated_data['amount']
                deposit_method = serializer.validated_data['deposit_method']
                description = serializer.validated_data.get('description', '')
                
                # Add to account
                account.balance += amount
                account.save()
                
                # Create transaction
                transaction_obj = Transaction.objects.create(
                    account=account,
                    transaction_type='deposit',
                    status='completed',
                    amount=amount,
                    description=f"Deposit via {deposit_method}: {description}",
                    balance_after=account.balance
                )
                
                # Send notification (disabled - Celery not installed)
                # send_deposit_notification.delay(
                #     account_id=account.id,
                #     amount=str(amount),
                #     user_email=account.user.email
                # )
                
                tx_serializer = TransactionSerializer(transaction_obj)
                return Response(tx_serializer.data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Deposit error: {str(e)}")
            return Response(
                {'error': 'Deposit failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def stripe_deposit(self, request, pk=None):
        """Deposit using Stripe payment"""
        account = self.get_object()
        serializer = StripeDepositSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            from django.conf import settings
            stripe.api_key = getattr(
                settings, 'STRIPE_SECRET_KEY', ''
            )
            amount = serializer.validated_data['amount']
            stripe_token = serializer.validated_data['stripe_token']
            description = serializer.validated_data.get('description', '')
            
            # Create Stripe charge
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # Convert to cents
                currency='usd',
                source=stripe_token,
                description=f"Deposit for {account.name}"
            )
            
            if charge.status == 'succeeded':
                with transaction.atomic():
                    account.balance += amount
                    account.save()
                    
                    transaction_obj = Transaction.objects.create(
                        account=account,
                        transaction_type='deposit',
                        status='completed',
                        amount=amount,
                        description=f"Stripe deposit: {description}",
                        balance_after=account.balance
                    )
                    
                    # send_deposit_notification.delay(disabled - Celery not installed)
                    # send_deposit_notification.delay(
                    #     account_id=account.id,
                    #     amount=str(amount),
                    #     user_email=account.user.email
                    # )
                    
                    tx_serializer = TransactionSerializer(transaction_obj)
                    return Response(tx_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Stripe charge failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except stripe.error.CardError as e:
            logger.error(f"Stripe card error: {e.user_message}")
            return Response(
                {'error': e.user_message},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Stripe deposit error: {str(e)}")
            return Response(
                {'error': 'Stripe deposit failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get account transactions"""
        account = self.get_object()
        transactions = account.transactions.all()
        
        # Filter by type
        tx_type = request.query_params.get('type')
        if tx_type:
            transactions = transactions.filter(transaction_type=tx_type)
        
        # Pagination
        limit = int(request.query_params.get('limit', 20))
        transactions = transactions[:limit]
        
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class VirtualCardViewSet(viewsets.ModelViewSet):
    """Virtual card management endpoints"""
    serializer_class = VirtualCardSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        """Return virtual cards for current user's accounts"""
        return VirtualCard.objects.filter(account__user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_card(self, request):
        """Create new virtual card"""
        serializer = VirtualCardCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get user's primary account
            account = Account.objects.get(user=request.user, is_active=True)
            
            card = VirtualCard.objects.create(
                account=account,
                cardholder_name=serializer.validated_data['cardholder_name'],
                daily_limit=serializer.validated_data.get('daily_limit', Decimal('1000.00')),
                monthly_limit=serializer.validated_data.get('monthly_limit', Decimal('10000.00'))
            )
            
            card_serializer = VirtualCardSerializer(card)
            return Response(card_serializer.data, status=status.HTTP_201_CREATED)
        
        except Account.DoesNotExist:
            return Response(
                {'error': 'No active account found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Card creation error: {str(e)}")
            return Response(
                {'error': 'Card creation failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def lock_card(self, request, pk=None):
        """Lock virtual card"""
        card = self.get_object()
        card.is_locked = True
        card.save()
        return Response(
            {'message': 'Card locked', 'card': VirtualCardSerializer(card).data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def unlock_card(self, request, pk=None):
        """Unlock virtual card"""
        card = self.get_object()
        card.is_locked = False
        card.save()
        return Response(
            {'message': 'Card unlocked', 'card': VirtualCardSerializer(card).data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def cancel_card(self, request, pk=None):
        """Cancel virtual card"""
        card = self.get_object()
        card.status = 'cancelled'
        card.save()
        return Response(
            {'message': 'Card cancelled', 'card': VirtualCardSerializer(card).data},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Get card transactions"""
        card = self.get_object()
        transactions = card.card_transactions.all()
        
        limit = int(request.query_params.get('limit', 20))
        transactions = transactions[:limit]
        
        from .serializers import CardTransactionSerializer
        serializer = CardTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


class TransferViewSet(viewsets.ReadOnlyModelViewSet):
    """Transfer history endpoints"""
    serializer_class = TransferSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        """Return transfers for current user"""
        user = self.request.user
        return Transfer.objects.filter(
            models.Q(sender__user=user) | models.Q(receiver__user=user)
        ).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get sent transfers"""
        transfers = Transfer.objects.filter(sender__user=request.user).order_by('-created_at')
        serializer = self.get_serializer(transfers, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def received(self, request):
        """Get received transfers"""
        transfers = Transfer.objects.filter(receiver__user=request.user).order_by('-created_at')
        serializer = self.get_serializer(transfers, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """Transaction history endpoints"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        """Return transactions for current user's accounts"""
        return Transaction.objects.filter(account__user=self.request.user).order_by('-created_at')


# Card Provisioning Views

from django.http import JsonResponse, Http404
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_GET
def get_wallet_payload(request, card_id):
    """
    DEV endpoint: return a simulated wallet provisioning payload for a given VirtualCard.
    In production this would be a token or pass signed by the tokenization provider.
    
    GET /api/cards/<card_id>/wallet_payload/
    
    Response:
    {
        "card_id": 1,
        "cardholder_name": "John Doe",
        "last4": "1234",
        "exp_month": 11,
        "exp_year": 2028,
        "provisioning_token": "sim-token-...",
        "wallet_instructions": "Add to Apple Pay, Google Pay, Samsung Pay, etc."
    }
    """
    try:
        card = VirtualCard.objects.get(pk=card_id)
    except VirtualCard.DoesNotExist:
        raise Http404("Card not found")

    # Simulated wallet payload - replace with actual provider payload in prod
    payload = {
        "card_id": card.id,
        "cardholder_name": getattr(card, "cardholder_name", str(card.account.user) if hasattr(card, "account") else "Unknown"),
        "last4": getattr(card, "last4", "0000"),
        "exp_month": getattr(card, "exp_month", 12),
        "exp_year": getattr(card, "exp_year", 2025),
        "provisioning_token": getattr(card, "provisioning_token", "sim-token-placeholder"),
        "status": getattr(card, "status", "active"),
        "wallet_instructions": "This is a simulated payload. Use real provider tokens for real wallets (Apple Pay, Google Pay, Samsung Pay).",
    }
    return JsonResponse(payload)


@csrf_exempt
@require_GET
def list_wallet_cards(request):
    """
    DEV endpoint: List all provisioned virtual cards ready for wallet
    
    GET /api/cards/wallet_list/
    
    Response:
    {
        "cards": [
            {"id": 1, "last4": "1234", "cardholder_name": "John Doe", "status": "active"},
            ...
        ],
        "count": 3
    }
    """
    try:
        cards = VirtualCard.objects.filter(status="active", provisioned=True).values(
            "id", "last4", "cardholder_name", "status"
        )
        return JsonResponse({
            "cards": list(cards),
            "count": len(cards)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
