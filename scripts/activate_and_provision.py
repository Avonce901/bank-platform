#!/usr/bin/env python
"""
Flask CLI script to:
- Activate (enable) three existing accounts (acct_user1..acct_user3 or accounts with >= $1,000,000)
- Create a VirtualCard record for each account with test data and a simulated provisioning token

USAGE:
    python scripts/activate_and_provision.py

This script is safe for development/test only. It will do existence checks for models and will not crash 
if models aren't present; instead it prints explanatory errors.
"""
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
import datetime
from decimal import Decimal

# Best-effort imports; if the project uses different module names adjust after the PR
try:
    from src.database.models import Base, User, Account, VirtualCard
    from src.database.service import get_db_service
except Exception as e:
    print(f"ERROR: Failed to import required modules: {e}")
    print("Update import paths in this script if models are in different locations.")
    sys.exit(1)


def activate_and_provision():
    """Main function to activate accounts and create virtual cards"""
    
    try:
        db_service = get_db_service()
        session = db_service.session
    except Exception as e:
        print(f"ERROR: Failed to get database service: {e}")
        sys.exit(1)

    # Try to find accounts by usernames first
    usernames = ["acct_user1", "acct_user2", "acct_user3"]
    accounts = []
    
    for u in usernames:
        try:
            acc = session.query(Account).join(User).filter(User.username == u).first()
            if acc:
                accounts.append(acc)
        except Exception:
            # fallback: try account with a user having that username
            pass

    # If not found by username, fallback to accounts with balance >= 1,000,000
    if len(accounts) < 3:
        try:
            qs = session.query(Account).filter(Account.balance >= 1000000.0).order_by(Account.id).all()
            for acc in qs:
                if acc not in accounts:
                    accounts.append(acc)
                if len(accounts) >= 3:
                    break
        except Exception as e:
            print(f"WARNING: Failed to query accounts by balance: {e}")

    # If still fewer than 3, create placeholder users/accounts (dev only)
    i = 1
    while len(accounts) < 3:
        uname = f"acct_user{i}"
        try:
            user = session.query(User).filter(User.username == uname).first()
            if not user:
                # Create new user
                user = User(
                    id=str(uuid.uuid4()),
                    username=uname,
                    email=f"{uname}@example.com",
                    password_hash="dev_only_hash",  # Not for real authentication
                    first_name=f"Test",
                    last_name=f"User{i}",
                    is_active=True
                )
                session.add(user)
                session.flush()
            
            # Create account if none exists for user
            acc = session.query(Account).filter(Account.owner_id == user.id).first()
            if not acc:
                acc = Account(
                    id=str(uuid.uuid4()),
                    account_number=f"ACC{str(uuid.uuid4().hex[:12]).upper()}",
                    account_name=f"Dev Account {i}",
                    owner_id=user.id,
                    balance=1000000.0,
                    available_balance=1000000.0,
                    is_active=True
                )
                session.add(acc)
                session.flush()
            
            accounts.append(acc)
        except Exception as e:
            print(f"ERROR: Failed to create user/account for {uname}: {e}")
        
        i += 1

    # Commit any created users/accounts
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"ERROR: Failed to commit user/account changes: {e}")
        sys.exit(1)

    created_cards = []
    for idx, acc in enumerate(accounts, start=1):
        # Activate the account
        try:
            if hasattr(acc, 'is_active'):
                acc.is_active = True
            elif hasattr(acc, 'active'):
                setattr(acc, 'active', True)
            elif hasattr(acc, 'enabled'):
                setattr(acc, 'enabled', True)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"WARNING: Failed to activate account id={acc.id}: {e}")

        # Create a virtual card for this account
        now = datetime.date.today()
        exp_month = now.month
        exp_year = now.year + 3
        token = f"sim-token-{uuid.uuid4().hex}"

        last4 = ("0000" + str(1000 + idx))[-4:]

        try:
            # Check if card already exists
            existing_card = session.query(VirtualCard).filter(VirtualCard.account_id == acc.id).first()
            
            if existing_card:
                # Update existing card
                existing_card.status = "active"
                existing_card.provisioning_token = token
                existing_card.provisioned = True
                existing_card.updated_at = datetime.datetime.utcnow()
                vc = existing_card
                action = "Updated"
            else:
                # Create new card
                cardholder_name = f"{acc.owner.first_name or ''} {acc.owner.last_name or ''}".strip()
                if not cardholder_name:
                    cardholder_name = acc.owner.username
                
                vc = VirtualCard(
                    id=str(uuid.uuid4()),
                    account_id=acc.id,
                    cardholder_name=cardholder_name,
                    last4=last4,
                    exp_month=exp_month,
                    exp_year=exp_year,
                    status="active",
                    provisioning_token=token,
                    provisioned=True
                )
                session.add(vc)
                action = "Created"
            
            session.commit()
            created_cards.append(vc)
            print(f"✓ {action} virtual card id={vc.id} for account id={acc.id} (token={token})")
        except Exception as e:
            session.rollback()
            print(f"ERROR: Failed to create/update virtual card for account id={acc.id}: {e}")

    print(f"\n✅ Processed {len(accounts)} accounts. {len(created_cards)} virtual cards created/updated.")
    print("Note: tokens are simulated. Real wallet provisioning requires a tokenization provider (Stripe Issuing, Visa MDES, etc.)")
    print("\nCard IDs for API testing:")
    for vc in created_cards:
        print(f"  - Card ID: {vc.id} (last4: {vc.last4})")


if __name__ == "__main__":
    print("============================================================")
    print("🔧 DEVELOPMENT ONLY: Account & Card Provisioning")
    print("============================================================")
    activate_and_provision()
