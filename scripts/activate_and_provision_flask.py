#!/usr/bin/env python
"""
Flask-compatible script to:
- Activate (enable) three existing accounts or create them with $1,000,000 balance
- Create a VirtualCard record for each account with test data and a simulated provisioning token

USAGE:
    python scripts/activate_and_provision_flask.py

This script is safe for development/test only. It includes protective checks and clear error messages.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import uuid
import datetime
from decimal import Decimal

# Best-effort imports
try:
    from src.database.models import Account, User, VirtualCard
    from src.database.service import get_db_service
except Exception as e:
    print(f"ERROR: Could not import required modules: {e}")
    print("Make sure you're running from the project root and dependencies are installed.")
    sys.exit(1)

def activate_and_provision():
    """Main provisioning function"""
    print("\n" + "="*60)
    print("🏦 ACCOUNT ACTIVATION & VIRTUAL CARD PROVISIONING")
    print("="*60)
    print("⚠️  Development/Test Only - DO NOT USE IN PRODUCTION\n")
    
    # Initialize database connection
    try:
        db_service = get_db_service()
        db_service.init_db()  # Ensure tables exist, including VirtualCard
        session = db_service.get_session()
    except Exception as e:
        print(f"ERROR: Could not initialize database: {e}")
        sys.exit(1)
    
    try:
        # Try to find accounts by usernames first
        usernames = ["acct_user1", "acct_user2", "acct_user3"]
        accounts = []
        
        print(f"🔍 Looking for accounts with usernames: {', '.join(usernames)}...")
        # Query accounts directly without triggering User relationships
        all_accounts = session.query(Account).all()
        for u in usernames:
            for acc in all_accounts:
                if hasattr(acc, 'owner') and hasattr(acc.owner, 'username'):
                    if acc.owner.username == u:
                        accounts.append(acc)
                        print(f"  ✓ Found account for {u}: {acc.account_number}")
                        break
        
        # If not found by username, fallback to accounts with balance >= 1,000,000
        if len(accounts) < 3:
            print(f"\n🔍 Looking for accounts with balance >= $1,000,000...")
            for acc in all_accounts:
                if acc.balance >= 1000000.0 and acc not in accounts:
                    accounts.append(acc)
                    print(f"  ✓ Found account: {acc.account_number} (balance: ${acc.balance:,.2f})")
                    if len(accounts) >= 3:
                        break
        
        # If still fewer than 3, create placeholder users/accounts (dev only)
        i = 1
        while len(accounts) < 3:
            print(f"\n📝 Creating placeholder account {i}...")
            uname = f"acct_user{i}"
            
            # Check if user exists
            user = session.query(User).filter(User.username == uname).first()
            if not user:
                # Create user
                from werkzeug.security import generate_password_hash
                user = User(
                    username=uname,
                    email=f"{uname}@example.com",
                    password_hash=generate_password_hash("TestPassword123!"),
                    first_name=f"Test{i}",
                    last_name="User",
                    is_active=True
                )
                session.add(user)
                session.flush()
                print(f"  ✓ Created user: {uname}")
            
            # Check if account exists for this user
            acc = session.query(Account).filter(Account.owner_id == user.id).first()
            if not acc:
                # Generate unique account number
                account_number = f"ACC{uuid.uuid4().hex[:12].upper()}"
                acc = Account(
                    account_number=account_number,
                    account_name=f"Test Account {i}",
                    owner_id=user.id,
                    balance=1000000.0,
                    available_balance=1000000.0,
                    is_active=True
                )
                session.add(acc)
                session.flush()
                print(f"  ✓ Created account: {account_number} with $1,000,000 balance")
            
            accounts.append(acc)
            i += 1
        
        # Activate all accounts and create virtual cards
        created_cards = []
        print(f"\n💳 Creating virtual cards for {len(accounts)} accounts...")
        
        for idx, acc in enumerate(accounts, start=1):
            # Activate the account
            try:
                if hasattr(acc, 'is_active'):
                    acc.is_active = True
                    session.add(acc)
                    print(f"\n  [{idx}] Activated account: {acc.account_number}")
            except Exception as e:
                print(f"  ! Failed to activate account {acc.id}: {e}")
            
            # Create a virtual card for this account
            now = datetime.date.today()
            exp_month = now.month
            exp_year = now.year + 3
            token = f"sim-token-{uuid.uuid4().hex}"
            last4 = ("0000" + str(1000 + idx))[-4:]
            
            try:
                # Check if card already exists for this account
                existing_card = session.query(VirtualCard).filter(
                    VirtualCard.account_id == acc.id
                ).first()
                
                if existing_card:
                    # Update existing card
                    existing_card.status = "active"
                    existing_card.provisioning_token = token
                    existing_card.provisioned = True
                    existing_card.updated_at = datetime.datetime.utcnow()
                    vc = existing_card
                    print(f"      Updated existing virtual card (ID: {vc.id})")
                else:
                    # Create new card
                    cardholder_name = f"{acc.owner.first_name} {acc.owner.last_name}".strip() if acc.owner.first_name else acc.owner.username
                    vc = VirtualCard(
                        account_id=acc.id,
                        cardholder_name=cardholder_name,
                        last4=last4,
                        exp_month=exp_month,
                        exp_year=exp_year,
                        status="active",
                        provisioning_token=token,
                        provisioned=True,
                    )
                    session.add(vc)
                    print(f"      Created new virtual card")
                
                session.flush()
                created_cards.append(vc)
                
                print(f"      Card ID: {vc.id}")
                print(f"      Cardholder: {vc.cardholder_name}")
                print(f"      Last 4: {vc.last4}")
                print(f"      Expiry: {vc.exp_month:02d}/{vc.exp_year}")
                print(f"      Token: {token[:20]}...")
                
            except Exception as e:
                print(f"  ! Error creating virtual card for account {acc.id}: {e}")
                import traceback
                traceback.print_exc()
        
        # Commit all changes
        session.commit()
        
        print(f"\n" + "="*60)
        print(f"✅ SUCCESS!")
        print(f"="*60)
        print(f"Processed {len(accounts)} accounts")
        print(f"Created/updated {len(created_cards)} virtual cards")
        print(f"\n⚠️  Note: Tokens are simulated. Real wallet provisioning requires")
        print(f"   a tokenization provider (Stripe Issuing, Visa MDES, etc.)")
        print(f"\n🔗 Test the API endpoint:")
        for card in created_cards:
            print(f"   curl http://localhost:8000/cards/{card.id}/wallet_payload/")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    activate_and_provision()
