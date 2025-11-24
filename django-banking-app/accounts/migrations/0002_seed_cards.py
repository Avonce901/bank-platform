# Generated data migration - seed 9 virtual cards on first boot
from django.db import migrations
from django.contrib.auth.models import User
from decimal import Decimal


def seed_cards(apps, schema_editor):
    """Create 9 virtual cards if they don't exist"""
    Account = apps.get_model('accounts', 'Account')
    VirtualCard = apps.get_model('accounts', 'VirtualCard')
    
    # Only seed if no cards exist
    if VirtualCard.objects.exists():
        return
    
    # Create admin user if needed
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={'is_staff': True, 'is_superuser': True}
    )
    
    # Create admin account
    admin_account, _ = Account.objects.get_or_create(
        user=admin_user,
        account_number='1000-ADMIN',
        defaults={
            'name': 'Test Admin',
            'account_type': 'checking',
            'balance': Decimal('50000.00'),
            'is_active': True,
        }
    )
    
    # Card 1: Test Admin
    VirtualCard.objects.get_or_create(
        account=admin_account,
        card_number='4532-1234-5678-9010',
        defaults={
            'cardholder_name': 'Test Admin',
            'expiry_date': '12/27',
            'cvv': '123',
            'status': 'active',
            'daily_limit': Decimal('1000.00'),
            'monthly_limit': Decimal('10000.00'),
            'spent_today': Decimal('0.00'),
            'spent_this_month': Decimal('0.00'),
        }
    )
    
    # Create user accounts and cards
    user_data = [
        ('acct_user1', 'Test User 1', '5096'),
        ('acct_user2', 'Test User 2', '4099'),
        ('acct_user3', 'Test User 3', '3642'),
    ]
    
    for i, (username, name, suffix) in enumerate(user_data, start=2):
        user, _ = User.objects.get_or_create(username=username)
        account, _ = Account.objects.get_or_create(
            user=user,
            account_number=f'2000-{username.upper()}',
            defaults={
                'name': name,
                'account_type': 'checking',
                'balance': Decimal('25000.00'),
                'is_active': True,
            }
        )
        VirtualCard.objects.get_or_create(
            account=account,
            card_number=f'4532-1234-5678-{suffix}',
            defaults={
                'cardholder_name': name,
                'expiry_date': '12/27',
                'cvv': '123',
                'status': 'active',
                'daily_limit': Decimal('1000.00'),
                'monthly_limit': Decimal('10000.00'),
                'spent_today': Decimal('0.00'),
                'spent_this_month': Decimal('0.00'),
            }
        )
    
    # Create Test Users 1-5
    for i in range(1, 6):
        user, _ = User.objects.get_or_create(username=f'testuser{i}')
        account, _ = Account.objects.get_or_create(
            user=user,
            account_number=f'3000-TEST-USER-{i}',
            defaults={
                'name': f'Test User {i}',
                'account_type': 'checking',
                'balance': Decimal('15000.00'),
                'is_active': True,
            }
        )
        card_suffix = str(4858 + i).zfill(4)[-4:]
        VirtualCard.objects.get_or_create(
            account=account,
            card_number=f'4532-1234-5678-{card_suffix}',
            defaults={
                'cardholder_name': f'Test User {i}',
                'expiry_date': '12/27',
                'cvv': '123',
                'status': 'active',
                'daily_limit': Decimal('1000.00'),
                'monthly_limit': Decimal('10000.00'),
                'spent_today': Decimal('0.00'),
                'spent_this_month': Decimal('0.00'),
            }
        )


def reverse_seed(apps, schema_editor):
    """Delete seeded cards"""
    VirtualCard = apps.get_model('accounts', 'VirtualCard')
    VirtualCard.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_cards, reverse_seed),
    ]
