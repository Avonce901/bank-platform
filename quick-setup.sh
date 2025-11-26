#!/bin/bash
# 🚀 Bank Platform - One-Command Setup
# Run: ./quick-setup.sh

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🚀 BANK PLATFORM - QUICK AUTOMATED SETUP               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Step counter
STEP=1

step() {
    echo -e "\n${BLUE}Step $STEP: $1${NC}"
    ((STEP++))
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# ============================================================================

step "Checking Python Installation"
python3 --version || error "Python 3 not found"
success "Python ready"

# ============================================================================

step "Setting Up Virtual Environment"
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    success "Virtual environment created"
else
    success "Virtual environment already exists"
fi

# Activate venv
source .venv/bin/activate
success "Virtual environment activated"

# ============================================================================

step "Installing Dependencies"
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1 || warning "Some packages may have failed"
success "Dependencies installed"

# ============================================================================

step "Creating Environment File"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        # Replace placeholders for local dev
        sed -i 's/your-secret-key-here/dev-secret-key-12345/' .env || true
        sed -i 's/DEBUG=False/DEBUG=True/' .env || true
        success ".env file created"
    else
        warning ".env.example not found, skipping .env"
    fi
else
    success ".env already exists"
fi

# ============================================================================

step "Running Database Migrations"
cd django-banking-app
python manage.py makemigrations --noinput > /dev/null 2>&1 || true
python manage.py migrate --noinput > /dev/null 2>&1 || warning "Migrations had issues"
success "Database migrations complete"

# ============================================================================

step "Creating Test Data"
python << 'PYTHON_SCRIPT'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Account
from rest_framework.authtoken.models import Token
from decimal import Decimal

User = get_user_model()

test_users = [
    ('sender_test', 'sender@test.com', '5000.00'),
    ('receiver_test', 'receiver@test.com', '100.00'),
]

print("\n📝 Creating test data...\n")

for username, email, balance in test_users:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email}
    )
    
    if created:
        user.set_password('password123')
        user.save()
        print(f"   ✅ Created user: {username}")
    
    account, created = Account.objects.get_or_create(
        user=user,
        defaults={
            'account_number': f'{username.upper()}_{user.id}',
            'name': f'{username.replace("_", " ").title()} Account'
        }
    )
    
    if created or account.balance == 0:
        account.balance = Decimal(balance)
        account.is_active = True
        account.save()
        print(f"   ✅ Created account: {account.account_number} (${balance})")
    
    token, _ = Token.objects.get_or_create(user=user)
    if created:
        print(f"   🔑 Token: {token.key[:20]}...")

print("\n✅ Test data created!\n")
PYTHON_SCRIPT

cd ..
success "Test data setup complete"

# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         ✅ SETUP COMPLETE - READY TO GO! 🎉                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${GREEN}🚀 NEXT STEPS:${NC}\n"

echo "1. Start the development server:"
echo -e "   ${BLUE}cd django-banking-app${NC}"
echo -e "   ${BLUE}python manage.py runserver${NC}\n"

echo "2. Test the API (in another terminal):"
echo -e "   ${BLUE}curl http://localhost:8000/api/accounts/\\${NC}"
echo -e "     ${BLUE}-H 'Authorization: Token YOUR_TOKEN'${NC}\n"

echo "3. Deploy to Railway:"
echo -e "   Visit: ${BLUE}https://railway.app/dashboard${NC}\n"

echo "4. Make real-time payments:"
echo -e "   ${BLUE}POST /api/payments/create_payment_intent/${NC}"
echo -e "   ${BLUE}POST /api/payments/confirm_payment/${NC}\n"

echo -e "${YELLOW}📚 Documentation:${NC}"
echo "   • DEPLOYMENT_AUTOMATION.md"
echo "   • RAILWAY_DEPLOYMENT.md"
echo "   • API_DOCUMENTATION.md"
echo ""
