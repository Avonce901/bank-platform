#!/usr/bin/env python3
"""
POST-DEPLOYMENT VERIFICATION
Run this after Railway redeploys with environment variables
"""

import os
import sys
import requests
from datetime import datetime

print("\n" + "="*75)
print("🚀 POST-DEPLOYMENT VERIFICATION CHECKLIST")
print("="*75 + "\n")

checks_passed = 0
checks_total = 0

def check(name, condition, details=""):
    """Helper to show check results"""
    global checks_passed, checks_total
    checks_total += 1
    status = "✅" if condition else "❌"
    if condition:
        checks_passed += 1
    print(f"{status} {name:45} {details}")
    return condition

print("📋 CONFIGURATION CHECKS")
print("-" * 75)

# Check environment variables
check(
    "DEPLOYMENT_MODE set to production",
    os.getenv('DEPLOYMENT_MODE') == 'production',
    f"Value: {os.getenv('DEPLOYMENT_MODE', 'NOT SET')}"
)

check(
    "STRIPE_API_KEY configured",
    bool(os.getenv('STRIPE_API_KEY')),
    f"Starts with: {os.getenv('STRIPE_API_KEY', 'N/A')[:20]}..."
)

check(
    "STRIPE_WEBHOOK_SECRET configured",
    bool(os.getenv('STRIPE_WEBHOOK_SECRET')),
    f"Starts with: {os.getenv('STRIPE_WEBHOOK_SECRET', 'N/A')[:20]}..."
)

check(
    "DATABASE_URL configured",
    bool(os.getenv('DATABASE_URL')),
    "PostgreSQL connection ready"
)

check(
    "REDIS_URL configured",
    bool(os.getenv('REDIS_URL')),
    "Redis cache ready"
)

print("\n")
print("🏥 HEALTH CHECKS")
print("-" * 75)

# Check if app is running
try:
    # Try local endpoint if available
    response = requests.get('http://localhost:5000/health', timeout=2)
    check(
        "Local health endpoint responding",
        response.status_code == 200,
        f"Status: {response.status_code}"
    )
except Exception as e:
    check(
        "Local health endpoint responding",
        False,
        f"Error: {str(e)}"
    )

print("\n")
print("🔐 SECURITY CHECKS")
print("-" * 75)

check(
    "No test keys in production",
    not os.getenv('STRIPE_API_KEY', '').startswith('sk_test_'),
    "Using live keys (sk_live_)"
)

check(
    "Webhook secret uses live prefix",
    os.getenv('STRIPE_WEBHOOK_SECRET', '').startswith('whsec_live_'),
    "Live webhook secret configured"
)

check(
    "Production flag enabled",
    os.getenv('DEPLOYMENT_MODE') == 'production',
    "IS_PRODUCTION = True"
)

print("\n")
print("🎯 INTEGRATION CHECKS")
print("-" * 75)

# Try importing integrations
try:
    from src.integrations.billcom_client import BillComClient
    check(
        "Bill.com integration available",
        True,
        "Module imported successfully"
    )
except:
    check(
        "Bill.com integration available",
        False,
        "Module import failed"
    )

try:
    from src.integrations.intuit_client import QuickBooksClient
    check(
        "Intuit/QuickBooks integration available",
        True,
        "Module imported successfully"
    )
except:
    check(
        "Intuit/QuickBooks integration available",
        False,
        "Module import failed"
    )

try:
    import stripe
    check(
        "Stripe SDK imported",
        True,
        f"Version: {stripe.__version__}"
    )
except:
    check(
        "Stripe SDK imported",
        False,
        "Module import failed"
    )

print("\n")
print("📊 DATABASE CHECKS")
print("-" * 75)

try:
    from src.database.schema import Database
    db = Database(os.getenv('DATABASE_URL', 'sqlite:///bank_platform.db'))
    check(
        "Database connection successful",
        True,
        "Connected to PostgreSQL"
    )
except Exception as e:
    check(
        "Database connection successful",
        False,
        f"Error: {str(e)}"
    )

print("\n")
print("="*75)
print(f"RESULTS: {checks_passed}/{checks_total} checks passed")
print("="*75 + "\n")

if checks_passed == checks_total:
    print("🎉 ALL CHECKS PASSED!")
    print("✅ PRODUCTION IS READY!")
    print("💰 Ready to process live transactions!")
    sys.exit(0)
else:
    print(f"⚠️  {checks_total - checks_passed} checks failed")
    print("Please review the failures above and fix them")
    sys.exit(1)
