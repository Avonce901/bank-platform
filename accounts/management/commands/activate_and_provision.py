#!/usr/bin/env python
"""
Django management command to:
- Activate (enable) three existing accounts (acct_user1..acct_user3 or accounts with >= $1,000,000)
- Create a VirtualCard record for each account with test data and a simulated provisioning token

USAGE:
    python manage.py activate_and_provision

This command is safe for development/test only. It will do existence checks for models and will not crash the process if models aren't present; instead it prints explanatory errors.
"""
from django.core.management.base import BaseCommand
from decimal import Decimal
from django.contrib.auth import get_user_model
import uuid
import datetime

# Best-effort imports; if the project uses different module names adjust after the PR
try:
    from accounts.models import Account
except Exception:
    Account = None

try:
    from cards.models import VirtualCard
except Exception:
    VirtualCard = None

class Command(BaseCommand):
    help = "Activate 3 accounts and create provisioned virtual cards for them (development/test only)."

    def handle(self, *args, **options):
        if Account is None:
            self.stderr.write("ERROR: accounts.models.Account not found. Update import path in this command.")
            return
        if VirtualCard is None:
            self.stderr.write("ERROR: cards.models.VirtualCard not found. Update import path in this command.")
            return

        User = get_user_model()

        # Try to find accounts by usernames first
        usernames = ["acct_user1", "acct_user2", "acct_user3"]
        accounts = []
        for u in usernames:
            try:
                acc = Account.objects.filter(owner__username=u).first()
                if acc:
                    accounts.append(acc)
            except Exception:
                # fallback: try account with a user having that username
                pass

        # If not found by username, fallback to accounts with balance >= 1,000,000
        if len(accounts) < 3:
            qs = Account.objects.filter(balance__gte=Decimal("1000000.00")).order_by("id")
            for acc in qs:
                if acc not in accounts:
                    accounts.append(acc)
                if len(accounts) >= 3:
                    break

        # If still fewer than 3, create placeholder users/accounts (dev only)
        i = 1
        while len(accounts) < 3:
            uname = f"acct_user{i}"
            user, _ = User.objects.get_or_create(username=uname, defaults={"email": f"{uname}@example.com"})
            # Create account if none exists for user
            acc, created = Account.objects.get_or_create(owner=user, defaults={"balance": Decimal("1000000.00")})
            accounts.append(acc)
            i += 1

        created_cards = []
        for idx, acc in enumerate(accounts, start=1):
            # Activate the account
            try:
                # common field names: is_active / active / enabled — try the most common
                if hasattr(acc, 'is_active'):
                    acc.is_active = True
                elif hasattr(acc, 'active'):
                    setattr(acc, 'active', True)
                elif hasattr(acc, 'enabled'):
                    setattr(acc, 'enabled', True)
                acc.save()
            except Exception as e:
                self.stderr.write(f"Failed to activate account id={getattr(acc,'id',None)}: {e}")

            # Create a virtual card for this account
            now = datetime.date.today()
            exp_month = now.month
            exp_year = now.year + 3
            token = f"sim-token-{uuid.uuid4().hex}"

            last4 = ("0000" + str(1000 + idx))[-4:]

            try:
                vc, created = VirtualCard.objects.get_or_create(
                    account=acc,
                    defaults={
                        "cardholder_name": acc.owner.get_full_name() if hasattr(acc.owner, "get_full_name") else str(acc.owner),
                        "last4": last4,
                        "exp_month": exp_month,
                        "exp_year": exp_year,
                        "status": "active",
                        "provisioning_token": token,
                        "provisioned": True,
                    },
                )
                if not created:
                    vc.status = "active"
                    vc.provisioning_token = token
                    try:
                        vc.provisioned = True
                    except Exception:
                        pass
                    vc.save()
                created_cards.append(vc)
                self.stdout.write(self.style.SUCCESS(f"Created/updated virtual card id={getattr(vc,'id',None)} for account id={getattr(acc,'id',None)} (token={token})"))
            except Exception as e:
                self.stderr.write(f"Error creating virtual card for account id={getattr(acc,'id',None)}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Processed {len(accounts)} accounts. Created/updated {len(created_cards)} virtual cards."))
        self.stdout.write("Note: tokens are simulated. Real wallet provisioning requires a tokenization provider (Stripe Issuing, Visa MDES, etc.).")
