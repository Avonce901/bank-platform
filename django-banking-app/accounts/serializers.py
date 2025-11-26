"""Serializers for the accounts models."""
from rest_framework import serializers

from .models import (
    Account,
    Transaction,
    VirtualCard,
    Transfer,
    CardTransaction,
    StripeCustomer,
    PaymentMethod,
    StripePayment,
)


class AccountSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Account
        fields = (
            'id', 'user', 'account_number', 'account_type', 'balance',
            'status', 'name', 'is_active', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class AccountDetailedSerializer(AccountSerializer):
    transaction_count = serializers.IntegerField(source='transactions.count', read_only=True)
    card_count = serializers.IntegerField(source='virtual_cards.count', read_only=True)

    class Meta(AccountSerializer.Meta):
        fields = AccountSerializer.Meta.fields + ('transaction_count', 'card_count',)


class VirtualCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = VirtualCard
        fields = (
            'id', 'account', 'cardholder_name', 'card_number', 'status',
            'daily_limit', 'monthly_limit', 'expiry_date', 'exp_month', 'exp_year',
            'cvv', 'is_locked', 'provisioned', 'last4', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'card_number', 'created_at', 'updated_at', 'last4')


class VirtualCardCreateSerializer(serializers.Serializer):
    cardholder_name = serializers.CharField(max_length=128)
    daily_limit = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    monthly_limit = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)
    exp_month = serializers.IntegerField(required=False)
    exp_year = serializers.IntegerField(required=False)


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    related_account_name = serializers.CharField(source='related_account.name', read_only=True)

    class Meta:
        model = Transaction
        fields = (
            'id', 'account', 'account_name', 'transaction_type', 'amount',
            'balance_after', 'status', 'description', 'related_account',
            'related_account_name', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'balance_after', 'created_at', 'updated_at')


class TransferSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    receiver_name = serializers.CharField(source='receiver.name', read_only=True)

    class Meta:
        model = Transfer
        fields = (
            'id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'amount',
            'description', 'status', 'created_at', 'completed_at'
        )
        read_only_fields = ('id', 'created_at', 'completed_at')


class TransferCreateSerializer(serializers.Serializer):
    receiver_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_receiver_account_id(self, value):
        if not Account.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Receiver account does not exist')
        return value

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero')
        return value

    def validate(self, attrs):
        sender_account = self.context.get('sender_account')
        if sender_account and attrs.get('receiver_account_id') == sender_account.pk:
            raise serializers.ValidationError('Cannot transfer to the same account')
        return super().validate(attrs)

    @property
    def validated_data(self):
        data = super().validated_data
        data['receiver_account'] = Account.objects.get(pk=data['receiver_account_id'])
        return data


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    deposit_method = serializers.ChoiceField(choices=['bank_transfer', 'check', 'cash', 'wire'])
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero')
        return value


class StripeDepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    stripe_token = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero')
        return value


class CardTransactionSerializer(serializers.ModelSerializer):
    card_holder = serializers.CharField(source='card.cardholder_name', read_only=True)

    class Meta:
        model = CardTransaction
        fields = (
            'id', 'card', 'card_holder', 'amount', 'merchant', 'status', 'description', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serialize Stripe payment method."""
    class Meta:
        model = PaymentMethod
        fields = (
            'id', 'stripe_payment_method_id', 'payment_type', 'last4', 'brand',
            'is_default', 'created_at'
        )
        read_only_fields = ('id', 'stripe_payment_method_id', 'created_at')


class StripePaymentSerializer(serializers.ModelSerializer):
    """Serialize Stripe payment record."""
    payment_method = PaymentMethodSerializer(read_only=True)

    class Meta:
        model = StripePayment
        fields = (
            'id', 'stripe_payment_intent_id', 'stripe_charge_id', 'amount', 'currency',
            'status', 'description', 'receipt_url', 'payment_method', 'created_at'
        )
        read_only_fields = (
            'id', 'stripe_payment_intent_id', 'stripe_charge_id', 'receipt_url', 'created_at'
        )


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Create Stripe payment intent."""
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    payment_method_id = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero')
        return value


class StripeCustomerSerializer(serializers.ModelSerializer):
    """Serialize Stripe customer link."""
    payment_methods = PaymentMethodSerializer(many=True, read_only=True)

    class Meta:
        model = StripeCustomer
        fields = ('id', 'stripe_customer_id', 'payment_methods', 'created_at')
        read_only_fields = ('id', 'stripe_customer_id', 'created_at')
