from rest_framework import serializers
from .models import Account, Transaction

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'account_type', 'balance', 'created_at']
        read_only_fields = ['id', 'account_number', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'from_account', 'to_account', 'amount', 'transaction_type', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class TransferSerializer(serializers.Serializer):
    receiver_account = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=['apple_pay', 'bank_transfer', 'wire'])
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value
    
    def validate_receiver_account(self, value):
        # Add your validation logic here
        if not value:
            raise serializers.ValidationError("Receiver account is required")
        return value
