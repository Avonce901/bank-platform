"""
Django Admin Configuration
"""
from django.contrib import admin
from .models import Account, VirtualCard, Transaction, Transfer, CardTransaction


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'user', 'balance', 'status', 'created_at')
    list_filter = ('status', 'account_type', 'created_at')
    search_fields = ('account_number', 'user__username', 'name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VirtualCard)
class VirtualCardAdmin(admin.ModelAdmin):
    list_display = ('cardholder_name', 'card_number', 'status', 'daily_limit', 'monthly_limit', 'created_at')
    list_filter = ('status', 'is_locked', 'created_at')
    search_fields = ('cardholder_name', 'card_number', 'account__account_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at')
    search_fields = ('account__account_number', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__account_number', 'receiver__account_number')
    readonly_fields = ('created_at',)


@admin.register(CardTransaction)
class CardTransactionAdmin(admin.ModelAdmin):
    list_display = ('card', 'amount', 'merchant', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('card__cardholder_name', 'merchant', 'description')
    readonly_fields = ('created_at',)
