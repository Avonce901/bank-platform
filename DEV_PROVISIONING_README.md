# Development-Only Account Provisioning and Virtual Cards

⚠️ **WARNING: DEVELOPMENT/TEST ONLY** ⚠️

This directory contains development-only tools for account provisioning and virtual card simulation. **DO NOT USE IN PRODUCTION.**

## Overview

This feature set provides:

1. **Account Activation & Provisioning** - Activates or creates three accounts with $1,000,000 balance
2. **Virtual Card Creation** - Creates/provisions simulated virtual cards for those accounts
3. **Dev API Endpoint** - Exposes a wallet-ready provisioning payload for a given card
4. **Client Scripts** - Small helper scripts to interact with the provisioning API
5. **Hardened Verify Helper** - API verification tool with timeout and error handling

## Files Added

```
accounts/
  management/
    commands/
      activate_and_provision.py   # Django management command for provisioning
cards/
  views.py                        # Dev endpoint for wallet payloads
  urls.py                         # URL routing for card endpoints
scripts/
  provision_cards_via_api.py      # Client script to fetch wallet payloads
verify_api.py                     # Hardened API verification helper
```

## Usage

### 1. Run the Provisioning Command (Django)

**Note:** This repository uses Flask, not Django. The command below is provided as a reference implementation for Django-based projects or future migration.

```bash
# For Django projects:
python manage.py activate_and_provision
```

This command will:
- Look for accounts belonging to users: `acct_user1`, `acct_user2`, `acct_user3`
- If not found, look for accounts with balance >= $1,000,000
- If still not enough, create placeholder users/accounts with $1M balance
- Create a `VirtualCard` record for each account with simulated provisioning token
- Activate all accounts (set `is_active=True`)

### 2. Fetch Wallet Payloads via API

```bash
# Fetch payloads for specific card IDs
python scripts/provision_cards_via_api.py --base http://localhost:8000 --card-ids 1 2 3
```

Output example:
```
Card 1 payload: {'card_id': 1, 'cardholder_name': 'John Doe', 'last4': '1001', ...}
Card 2 payload: {'card_id': 2, 'cardholder_name': 'Jane Smith', 'last4': '1002', ...}
Card 3 payload: {'card_id': 3, 'cardholder_name': 'Bob Johnson', 'last4': '1003', ...}
```

### 3. Verify API Health

```bash
# Default to http://localhost:8000
python verify_api.py

# Or specify custom base URL
BASE_URL=http://example.com:5000 python verify_api.py
```

## API Endpoint

### GET /cards/{card_id}/wallet_payload/

Returns a simulated wallet provisioning payload for a given VirtualCard.

**Response:**
```json
{
  "card_id": 1,
  "cardholder_name": "John Doe",
  "last4": "1001",
  "exp_month": 11,
  "exp_year": 2027,
  "provisioning_token": "sim-token-abc123...",
  "wallet_instructions": "This is a simulated payload. Use real provider tokens for real wallets."
}
```

## Adaptation for Flask

Since this repository uses **Flask** (not Django), you may need to adapt these files:

1. **Management Command** → Create a Flask CLI command or standalone script
2. **Django Views** → Convert to Flask views/blueprints
3. **Django URLs** → Add to Flask blueprint routing
4. **Models** → Use SQLAlchemy models instead of Django ORM

### Example: Flask Adaptation

Create a Flask CLI command:

```python
# In your Flask app
from flask import Blueprint
from src.database.models import Account, User

@app.cli.command("activate_and_provision")
def activate_and_provision():
    """Activate 3 accounts and create virtual cards (dev only)"""
    # Implementation similar to Django command
    pass
```

## VirtualCard Model

You may need to add a `VirtualCard` model to your database:

```python
# In src/database/models.py
class VirtualCard(Base):
    __tablename__ = 'virtual_cards'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False)
    cardholder_name = Column(String(120), nullable=False)
    last4 = Column(String(4), nullable=False)
    exp_month = Column(Integer, nullable=False)
    exp_year = Column(Integer, nullable=False)
    status = Column(String(20), default="active")
    provisioning_token = Column(String(255), nullable=True)
    provisioned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    account = relationship("Account", backref="virtual_cards")
```

## Security Considerations

⚠️ **These tools are for development/testing ONLY:**

- Simulated tokens are **not secure** and should never be used in production
- Accounts with $1M balances are test data only
- No real wallet provisioning is performed
- Real wallet provisioning requires integration with:
  - Stripe Issuing
  - Visa MDES (Mobile Device Enablement Service)
  - Mastercard MDES
  - Other tokenization providers

## Production Wallet Provisioning

For production use, you must:

1. Partner with a card issuing platform (e.g., Stripe Issuing, Marqeta, Lithic)
2. Implement proper tokenization using their SDK
3. Handle PCI-DSS compliance
4. Use real provisioning tokens signed by the provider
5. Implement proper authentication and authorization
6. Add rate limiting and security controls

## Protective Checks

All code includes protective checks:

- ✅ Try/except blocks around model imports
- ✅ Graceful fallback if models don't exist
- ✅ Clear error messages when dependencies are missing
- ✅ Will not crash if app/model names differ
- ✅ Best-effort field name detection (is_active, active, enabled)

## Questions?

These tools are reference implementations meant to be adapted to your specific stack and requirements. Adjust import paths, model names, and logic as needed for your application.
