# Copilot Instructions for Bank Platform

## Project Overview
**Bank Platform** is a Django REST Framework banking application with integrated virtual card provisioning, fund transfers, transactions, and account management. This is **production-grade code** - treat all financial operations as critical.

The main application lives in `django-banking-app/` (Django REST API). Legacy Flask modules in `src/` are NOT integrated and kept for historical reference only.

## Architecture Quick Reference

### Core Components
- **Django REST API** (`django-banking-app/`) - Production application
  - `banking/settings.py` - Environment-driven, SSL enforced in production, TokenAuth
  - `accounts/models.py` - User↔Account(1:1), VirtualCard, Transaction, Transfer, CardTransaction
  - `accounts/views.py` - ViewSets with atomic transactions for fund transfers
  - `accounts/serializers.py` - Validates all input, nested relationships
  - `accounts/urls.py` - DRF router registering all ViewSets
  - `accounts/migrations/` - Version-controlled schema; 0002_seed_cards.py bootstraps test data

- **Database Layer** - SQLite (dev/test), upgradable to PostgreSQL
  - All balance fields use `Decimal('x.xx')` - NEVER floats
  - Foreign keys cascade to related_name targets
  - Migrations are immutable production records

### Critical Data Flow
1. **Token Auth**: Client → HTTP header `Authorization: Token <hex>` → REST framework validates against authtoken.models.Token
2. **Account Queries**: Always `Account.objects.filter(user=self.request.user)` - never expose other users' data
3. **Fund Transfers**: MUST be wrapped in `transaction.atomic()` to prevent race conditions and partial failures
4. **Virtual Cards**: Provisioning disabled (no Channels/Celery/Redis) - fields present but unused

## Critical Workflows

### First Time Setup
```powershell
cd django-banking-app
python manage.py migrate                    # Initialize database schema
python manage.py migrate --run-syncdb       # Ensure all tables exist
python manage.py runserver 0.0.0.0:8000     # Start dev server
```
**Result**: Server at `http://localhost:8000`, admin at `/admin/` (no users yet - create with `createsuperuser`)

### Running in Production
```powershell
cd django-banking-app
export DJANGO_SETTINGS_MODULE=banking.settings
gunicorn banking.wsgi:application --bind 0.0.0.0:8000 --workers 4 --worker-class sync --timeout 120
```
**Key settings enforced via .env**: DEBUG=False, ALLOWED_HOSTS, CSRF cookie secure, SSL redirect

### Database Migrations (CRITICAL)
```powershell
# After ANY model.py change:
cd django-banking-app
python manage.py makemigrations accounts    # Creates migration file
python manage.py migrate                    # Applies to database
# COMMIT migration file - it's versioned history
```
**Never**: Manually edit migration files. Never skip migrations. Migrations run top-to-bottom.

### Testing
```powershell
cd django-banking-app
pytest                                      # All tests
pytest -k transfer                          # Filter by keyword (e.g., transfer tests)
pytest --cov=accounts --cov-report=html     # Coverage report
```
**Test data**: Seeded by `0002_seed_cards.py` migration (runs automatically), also `test_cards.py` in root

## Code Patterns & Conventions

### ViewSet Pattern (accounts/views.py)
```python
class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        # CRITICAL: Always filter by current user
        return Account.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        sender = self.get_object()  # Automatically filtered to request.user
        # ... validate receiver exists and is different user
        # ... always use transaction.atomic() for multi-model changes
```

### Atomic Transactions (CRITICAL for Fund Transfers)
```python
# WRONG: Balance updates can fail mid-operation, corrupting data
sender_account.balance -= amount
sender_account.save()
receiver_account.balance += amount
receiver_account.save()  # What if this fails?

# CORRECT: All-or-nothing operation
from django.db import transaction
with transaction.atomic():
    sender_account.balance -= amount
    sender_account.save()
    receiver_account.balance += amount
    receiver_account.save()
    # Create audit records
    Transfer.objects.create(sender=sender_account, receiver=receiver_account, amount=amount, status='completed')
    Transaction.objects.create(account=sender_account, transaction_type='transfer', amount=-amount, status='completed')
    Transaction.objects.create(account=receiver_account, transaction_type='transfer', amount=amount, status='completed')
    # If ANY step fails, entire block rolls back
```

### Decimal Money Fields (CRITICAL)
```python
# WRONG: Floats have precision errors
balance = 10.1 + 20.2  # Results in 30.299999999999997
from_account.balance = 100.50  # Wrong type

# CORRECT: Always use Decimal for currency
from decimal import Decimal
balance = Decimal('10.10') + Decimal('20.20')  # Exactly 30.30
model_field = models.DecimalField(max_digits=12, decimal_places=2)
amount = Decimal('100.50')
validation = MinValueValidator(Decimal('0.00'))
```

### Serializer Validation (Request Input)
```python
class TransferCreateSerializer(serializers.Serializer):
    receiver_account_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    def validate_receiver_account_id(self, value):
        try:
            account = Account.objects.get(id=value)
            return account  # Return object, not ID
        except Account.DoesNotExist:
            raise serializers.ValidationError("Receiver account not found")
    
    def validate_amount(self, value):
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Amount must be positive")
        return value
```

### Status & Choice Fields
```python
# Model definition
STATUS_CHOICES = (
    ('pending', 'Pending'),     # lowercase for database, Display for UI
    ('completed', 'Completed'),
    ('failed', 'Failed'),
)
status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

# Query: Always use lowercase
transactions = Transaction.objects.filter(status='completed')  # Correct

# Response: REST Framework includes display value
# {"status": "completed"}  # Not "Completed"
```

## Important Implementation Details

### Virtual Card Provisioning (DISABLED)
- `provisioning_token`, `provisioned` fields exist but unused
- Channels (WebSocket), Celery (async tasks), Redis cache removed for simplicity
- Card transactions logged in `CardTransaction` model but provisioning logic not implemented
- **Do NOT enable without: Channels setup, Celery broker, Redis instance, webhook handlers**
- Wallet payload functions (`get_wallet_payload`, `list_wallet_cards`) are simulated for testing only

### Environment Configuration
- Read from `.env` via `os.environ.get()` in settings.py
- Production: SSL enforced (SECURE_SSL_REDIRECT=True, SESSION_COOKIE_SECURE=True)
- No Redis/Celery: using LocMemCache, sync operations only
- Stripe fields present but not integrated (STRIPE_SECRET_KEY read but unused)
- ALLOWED_HOSTS must be set for production (e.g., `localhost,127.0.0.1,.railway.app`)

### Authentication Scheme
- Django's built-in Token auth (not JWT)
- Token generated on User creation signals (if enabled, currently disabled)
- Client sends: `Authorization: Token <hex_token>` (not "Bearer")
- No token refresh endpoint (stock tokens are permanent)
- Tokens stored in authtoken.models.Token, linked to User via OneToOne

### Testing Requirements
- Unit tests: Check serializer validation with valid/invalid inputs
- Integration tests: Use `APIClient` with Token auth to test full request cycle
- Sample data: Seeded by `0002_seed_cards.py` migration (runs during `migrate`)
- Test users: `admin_user`, `acct_user1-3`, `testuser1-5` with pre-seeded accounts
- Run migrations before tests: `python manage.py migrate`

## API Endpoints Reference

### Authentication
```
POST /api/token/                    # Get token: {"username": "admin_user", "password": ""}
```

### Account Management
```
GET    /api/accounts/               # List current user's accounts
GET    /api/accounts/<id>/          # Get account details
GET    /api/accounts/<id>/balance/  # Get current balance
POST   /api/accounts/<id>/transfer/ # Transfer funds (body: receiver_account_id, amount, description)
```

### Transactions & Cards
```
GET    /api/transactions/           # List all transactions for user's accounts
GET    /api/cards/                  # List virtual cards
POST   /api/cards/                  # Create new card (body: cardholder_name, daily_limit, monthly_limit)
GET    /api/transfers/              # List all transfers (sent/received)
```

### Example Real-Time Flow
```bash
# 1. Authenticate (using test seed data)
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin_user","password":""}'
# Response: {"token":"abc123..."}

# 2. Get user's accounts
curl -H "Authorization: Token abc123..." \
  http://localhost:8000/api/accounts/
# Response: [{"id":1,"account_number":"1000-ADMIN","balance":"50000.00",...}]

# 3. Transfer funds (atomic operation)
curl -X POST http://localhost:8000/api/accounts/1/transfer/ \
  -H "Authorization: Token abc123..." \
  -H "Content-Type: application/json" \
  -d '{"receiver_account_id":2,"amount":"100.00","description":"Payment"}'
# Response: Full Transfer object with status='completed' or error

# 4. Check updated balance
curl -H "Authorization: Token abc123..." \
  http://localhost:8000/api/accounts/1/balance/
```

## File Organization Rules

- **Models**: Defined in `accounts/models.py`, one file for clarity
- **Migrations**: Auto-generated in `accounts/migrations/`, never edit by hand
- **Views**: Keep related ViewSets in `accounts/views.py` (not split per model)
- **Serializers**: All in `accounts/serializers.py` for manageability
- **URLs**: Single router in `accounts/urls.py` with register() calls
- **Tests**: Root-level `test_cards.py`, or structured in `tests/` subdirectory
- **Static/Media**: `static/` and `media/` folders, managed by WhiteNoise + collectstatic

## Common Pitfalls

1. **Balance arithmetic with floats**: Use `Decimal('x')` always, never division with floats
2. **Non-atomic transfers**: Multi-step account updates MUST be in transaction.atomic() block
3. **Missing migration creation**: After model changes, run `makemigrations` before pushing
4. **Hardcoded status strings**: Use model choice tuples, not magic strings
5. **Ignoring permission_classes**: Every ViewSet must specify IsAuthenticated to block anonymous access
6. **Querying all users' accounts**: Always filter by `request.user` in get_queryset()
7. **Token auth header format**: Use `Authorization: Token <hex>` NOT `Bearer <token>`
8. **Forgetting to wrap transfers**: ANY multi-step account operation fails without transaction.atomic()

## Debugging Tips

- **500 errors in production**: Check logs: `docker logs bank_platform_api`
- **Migration conflicts**: Delete conflicting migration files, create new one with `makemigrations`
- **Token not recognized**: Verify token format (should be hex string), check user's token wasn't revoked
- **Balance mismatches**: Check Transaction records match Account adjustments (audit trail)
- **Account creation fails**: Likely missing OneToOne User relation; check signals or create endpoint
- **"Token not in request"**: Check header is exactly `Authorization: Token <token>` (case-sensitive, space matters)
- **Transfer shows status='pending' indefinitely**: Endpoint must explicitly set `completed_at` timestamp in atomic block

## Cross-File Dependencies
- `settings.py` → imported by `manage.py`, wsgi.py; never hardcode settings
- `models.py` → imported by serializers, views, migrations; changes trigger makemigrations
- `views.py` → references models, serializers, permissions; register ViewSets in urls.py
- `urls.py` → included in `banking/urls.py` via `include('accounts.urls')`
- `0002_seed_cards.py` → runs on `migrate`, creates test users (admin_user, acct_user1-3, testuser1-5)

## When to Ask for Clarification
- **Project scope unclear**: Confirm Django app vs Flask modules usage
- **Database schema change**: Validate atomic operation requirements with transfer workflow
- **New authentication method**: Understand current Token auth limitations before replacing
- **External service integration**: Verify Stripe/WebSocket/Celery requirements before enabling
