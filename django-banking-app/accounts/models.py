"""
Django Models for Banking Application
Accounts, Transactions, Virtual Cards, Transfers
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class Account(models.Model):
    """User bank account"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    account_number = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, default='checking')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), validators=[MinValueValidator(Decimal('0.00'))])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.account_number}"


class VirtualCard(models.Model):
    """Virtual debit/credit card"""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('locked', 'Locked'),
        ('cancelled', 'Cancelled'),
    )
    
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='virtual_cards')
    cardholder_name = models.CharField(max_length=100)
    card_number = models.CharField(max_length=19, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1000.00'))
    monthly_limit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10000.00'))
    expiry_date = models.CharField(max_length=5, default='12/25')
    cvv = models.CharField(max_length=4, default='000')
    is_locked = models.BooleanField(default=False)
    provisioned = models.BooleanField(default=False)
    last4 = models.CharField(max_length=4, blank=True)
    exp_month = models.IntegerField(default=12)
    exp_year = models.IntegerField(default=2025)
    provisioning_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.cardholder_name} - {self.card_number[-4:]}"
    
    def save(self, *args, **kwargs):
        if not self.last4:
            self.last4 = self.card_number[-4:]
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Account transaction record"""
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
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    related_account = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='related_transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.account.account_number} - {self.transaction_type} - {self.amount}"


class Transfer(models.Model):
    """Fund transfer between accounts"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transfers_sent')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transfers_received')
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transfer from {self.sender.account_number} to {self.receiver.account_number} - {self.amount}"


class CardTransaction(models.Model):
    """Transaction on virtual card"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    )
    
    card = models.ForeignKey(VirtualCard, on_delete=models.CASCADE, related_name='card_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    merchant = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Card transaction - {self.card.cardholder_name} - {self.amount}"
