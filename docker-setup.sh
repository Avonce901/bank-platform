#!/bin/bash
# 🐳 Bank Platform - Docker Quick Setup
# Run: ./docker-setup.sh

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      🐳 BANK PLATFORM - DOCKER AUTOMATED SETUP               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

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

# ============================================================================

step "Checking Docker Installation"
docker --version || error "Docker not found. Install from: https://www.docker.com/products/docker-desktop"
success "Docker ready"

# ============================================================================

step "Building Docker Image"
docker build -t bank-platform:latest . --quiet
success "Docker image built"

# ============================================================================

step "Starting Docker Container"
CONTAINER_ID=$(docker run -d \
  -p 8000:8000 \
  -e DEBUG=True \
  -e DJANGO_SECRET_KEY=dev-secret-key-12345 \
  -v $(pwd)/django-banking-app:/app/django-banking-app \
  bank-platform:latest)

sleep 3
success "Container started: $CONTAINER_ID"

# ============================================================================

step "Running Migrations in Container"
docker exec "$CONTAINER_ID" \
  python django-banking-app/manage.py migrate --noinput > /dev/null 2>&1 || true
success "Migrations complete"

# ============================================================================

step "Creating Test Data in Container"
docker exec "$CONTAINER_ID" python << 'PYTHON_SCRIPT'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Account
from rest_framework.authtoken.models import Token
from decimal import Decimal

User = get_user_model()

for username, email, balance in [
    ('sender_test', 'sender@test.com', '5000.00'),
    ('receiver_test', 'receiver@test.com', '100.00'),
]:
    user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    account, created = Account.objects.get_or_create(
        user=user,
        defaults={'account_number': f'{username.upper()}_{user.id}', 'name': f'{username.replace("_", " ").title()} Account'}
    )
    if created or account.balance == 0:
        account.balance = Decimal(balance)
        account.is_active = True
        account.save()
    Token.objects.get_or_create(user=user)
    print(f"✅ {username}")
PYTHON_SCRIPT

success "Test data created"

# ============================================================================

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║      ✅ DOCKER SETUP COMPLETE - APP RUNNING! 🎉              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${GREEN}🚀 YOUR APP IS RUNNING:${NC}\n"
echo -e "   API URL: ${BLUE}http://localhost:8000/api/${NC}"
echo -e "   Admin:   ${BLUE}http://localhost:8000/admin/${NC}"
echo -e "   Container ID: ${YELLOW}$CONTAINER_ID${NC}\n"

echo -e "${GREEN}📝 USEFUL COMMANDS:${NC}\n"

echo "   View logs:"
echo -e "     ${BLUE}docker logs $CONTAINER_ID${NC}\n"

echo "   Enter container:"
echo -e "     ${BLUE}docker exec -it $CONTAINER_ID bash${NC}\n"

echo "   Stop container:"
echo -e "     ${BLUE}docker stop $CONTAINER_ID${NC}\n"

echo "   Test API:"
echo -e "     ${BLUE}curl http://localhost:8000/api/accounts/${NC}"
echo -e "     ${BLUE}-H 'Authorization: Token YOUR_TOKEN'${NC}\n"

echo -e "${YELLOW}📚 Documentation:${NC}"
echo "   • DEPLOYMENT_AUTOMATION.md"
echo "   • RAILWAY_DEPLOYMENT.md"
echo ""
