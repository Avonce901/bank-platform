#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create a sample banking account
"""
import sys
import json
import hashlib
from datetime import datetime

# Sample user and account creation
def create_sample_account():
    """Create a sample banking account"""
    
    # User data
    user = {
        "id": 1,
        "username": "anthony_doe",
        "email": "anthony@banking.com",
        "password_hash": hashlib.sha256("SecurePassword123!".encode()).hexdigest(),
        "role": "CUSTOMER",
        "created_at": datetime.now().isoformat()
    }
    
    # Account data
    account = {
        "id": 1,
        "account_number": "ACC001",
        "account_type": "CHECKING",
        "balance": 10000.00,
        "currency": "USD",
        "user_id": user["id"],
        "status": "ACTIVE",
        "created_at": datetime.now().isoformat()
    }
    
    # Save to JSON files
    with open('data/users.json', 'w') as f:
        json.dump([user], f, indent=2)
    
    with open('data/accounts.json', 'w') as f:
        json.dump([account], f, indent=2)
    
    print("\n" + "="*60)
    print("BANKING ACCOUNT CREATED SUCCESSFULLY")
    print("="*60)
    print("\nUser Information:")
    print(f"  Username: {user['username']}")
    print(f"  Email: {user['email']}")
    print(f"  Role: {user['role']}")
    print(f"  Status: Active")
    
    print("\nAccount Information:")
    print(f"  Account Number: {account['account_number']}")
    print(f"  Account Type: {account['account_type']}")
    print(f"  Balance: ${account['balance']:,.2f}")
    print(f"  Currency: {account['currency']}")
    print(f"  Status: {account['status']}")
    
    print("\nNext Steps:")
    print("  1. Start the API: python src/api/main.py")
    print("  2. Login with your credentials:")
    print(f"     Username: {user['username']}")
    print("     Password: SecurePassword123!")
    print("  3. Access your account at: http://localhost:5000/api/v1/banking/accounts/1")
    
    print("\n" + "="*60)
    print("Account files saved to:")
    print("  - data/users.json")
    print("  - data/accounts.json")
    print("="*60 + "\n")
    
    return user, account

if __name__ == "__main__":
    try:
        user, account = create_sample_account()
        sys.exit(0)
    except Exception as e:
        print(f"Error creating account: {e}")
        sys.exit(1)
