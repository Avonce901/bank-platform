# Generated data migration - seed 9 virtual cards on first boot
from django.db import migrations
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


def seed_cards(apps, schema_editor):
    """Create 9 virtual cards if they don't exist"""
    Account = apps.get_model('accounts', 'Account')
    VirtualCard = apps.get_model('accounts', 'VirtualCard')
    
    # Only seed if no cards exist
    if VirtualCard.objects.exists():
        return
    
    # Create admin user if needed
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_staff': True, 
            'is_superuser': True,
            'last_login': timezone.now(),
        }
    )
    
    # Create admin account
    admin_account, created = Account.objects.get_or_create(
        user_id=admin_user.id,
        defaults={
            'account_number': '1000-ADMIN',
            'name': 'Test Admin',
            'account_type': 'checking',
            'balance': Decimal('50000.00'),
            'is_active': True,
        }
    )
    
    # Card 1: Test Admin
    VirtualCard.objects.create(
        account_id=admin_account.id,
        card_number='4532-1234-5678-9010',
        cardholder_name='Test Admin',
        expiry_date='12/27',
        cvv='123',
        status='active',
        daily_limit=Decimal('1000.00'),
        monthly_limit=Decimal('10000.00'),
    )
    
    # Create user accounts and cards
    user_data = [
        ('acct_user1', 'Test User 1', '5096'),
        ('acct_user2', 'Test User 2', '4099'),
        ('acct_user3', 'Test User 3', '3642'),
    ]
    
    for username, name, suffix in user_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'last_login': timezone.now()}
        )
        account, created = Account.objects.get_or_create(
            user_id=user.id,
            defaults={
                'account_number': f'2000-{username.upper()}',
                'name': name,
                'account_type': 'checking',
                'balance': Decimal('25000.00'),
                'is_active': True,
            }
        )
        VirtualCard.objects.create(
            account_id=account.id,
            card_number=f'4532-1234-5678-{suffix}',
            cardholder_name=name,
            expiry_date='12/27',
            cvv='123',
            status='active',
            daily_limit=Decimal('1000.00'),
            monthly_limit=Decimal('10000.00'),
        )
    
    # Create Test Users 1-5
    for i in range(1, 6):
        user, created = User.objects.get_or_create(
            username=f'testuser{i}',
            defaults={'last_login': timezone.now()}
        )
        account, created = Account.objects.get_or_create(
            user_id=user.id,
            defaults={
                'account_number': f'3000-TEST-USER-{i}',
                'name': f'Test User {i}',
                'account_type': 'checking',
                'balance': Decimal('15000.00'),
                'is_active': True,
            }
        )
        card_suffix = str(4858 + i).zfill(4)[-4:]
        VirtualCard.objects.create(
            account_id=account.id,
            card_number=f'4532-1234-5678-{card_suffix}',
            cardholder_name=f'Test User {i}',
            expiry_date='12/27',
            cvv='123',
            status='active',
            daily_limit=Decimal('1000.00'),
            monthly_limit=Decimal('10000.00'),
        )


def reverse_seed(apps, schema_editor):
    """Delete seeded data"""
    VirtualCard = apps.get_model('accounts', 'VirtualCard')
    Account = apps.get_model('accounts', 'Account')
    User = apps.get_model('auth', 'User')
    
    # Delete all virtual cards
    VirtualCard.objects.all().delete()
    
    # Delete test accounts
    Account.objects.filter(account_number__in=[
        '1000-ADMIN',
        '2000-ACCT_USER1',
        '2000-ACCT_USER2',
        '2000-ACCT_USER3',
        '3000-TEST-USER-1',
        '3000-TEST-USER-2',
        '3000-TEST-USER-3',
        '3000-TEST-USER-4',
        '3000-TEST-USER-5',
    ]).delete()
    
    # Delete test users
    User.objects.filter(username__in=[
        'admin',
        'acct_user1',
        'acct_user2',
        'acct_user3',
        'testuser1',
        'testuser2',
        'testuser3',
        'testuser4',
        'testuser5',
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_cards, reverse_seed),
    ]
