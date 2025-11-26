"""Banking models representing accounts, transfers, cards, and transactions."""
from decimal import Decimal
from django.conf import settings
from django.db import models


class Account(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='accounts')
    account_number = models.CharField(max_length=32, unique=True)
    account_type = models.CharField(max_length=32, default='checking')
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active')
    name = models.CharField(max_length=128, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account_number} ({self.user.username})"


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
        ('card_charge', 'Card Charge'),
        ('refund', 'Refund'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=32, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    balance_after = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    related_account = models.ForeignKey(
        Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='related_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"


class Transfer(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_transfers')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_transfers')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transfer {self.amount} from {self.sender.account_number}"


class VirtualCard(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('locked', 'Locked'),
        ('cancelled', 'Cancelled'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='virtual_cards')
    cardholder_name = models.CharField(max_length=128)
    card_number = models.CharField(max_length=19, unique=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='active')
    daily_limit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('1000.00'))
    monthly_limit = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('10000.00'))
    expiry_date = models.CharField(max_length=5, default='12/25')
    exp_month = models.IntegerField(default=12)
    exp_year = models.IntegerField(default=2026)
    cvv = models.CharField(max_length=4, default='000')
    is_locked = models.BooleanField(default=False)
    provisioned = models.BooleanField(default=False)
    last4 = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.last4 and self.card_number:
            self.last4 = self.card_number[-4:]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cardholder_name} • {self.card_number[-4:]}"


class CardTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    card = models.ForeignKey(VirtualCard, on_delete=models.CASCADE, related_name='card_transactions')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    merchant = models.CharField(max_length=128)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='completed')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.merchant} - {self.amount}"


class StripeCustomer(models.Model):
    """Link between Django user and Stripe customer ID."""
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='stripe_customer')
    stripe_customer_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Stripe: {self.stripe_customer_id}"


class PaymentMethod(models.Model):
    """Store Stripe payment method references."""
    TYPE_CHOICES = (
        ('card', 'Card'),
        ('bank_account', 'Bank Account'),
        ('apple_pay', 'Apple Pay'),
        ('google_pay', 'Google Pay'),
    )

    stripe_customer = models.ForeignKey(StripeCustomer, on_delete=models.CASCADE, related_name='payment_methods')
    stripe_payment_method_id = models.CharField(max_length=255, unique=True)
    payment_type = models.CharField(max_length=32, choices=TYPE_CHOICES, default='card')
    last4 = models.CharField(max_length=4, blank=True)
    brand = models.CharField(max_length=32, blank=True)  # visa, mastercard, amex, etc.
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand} •••• {self.last4}"


class StripePayment(models.Model):
    """Record of payments processed via Stripe."""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='stripe_payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_charge_id = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    receipt_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Stripe {self.stripe_charge_id or self.stripe_payment_intent_id} - {self.amount}"