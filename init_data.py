"""
Bank Platform - Account and Ledger Initialization Script
Initializes sample accounts, ledger entries, and test data
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

def initialize_accounts():
    """Initialize sample bank accounts"""
    print("\n[+] Initializing bank accounts...")
    
    accounts = {
        "accounts": [
            {
                "account_id": "ACC001",
                "account_holder": "John Doe",
                "account_type": "Checking",
                "balance": 5000.00,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "account_id": "ACC002",
                "account_holder": "Jane Smith",
                "account_type": "Savings",
                "balance": 15000.00,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "account_id": "ACC003",
                "account_holder": "Business Corp",
                "account_type": "Business",
                "balance": 50000.00,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "account_id": "ACC004",
                "account_holder": "Investment Fund",
                "account_type": "Investment",
                "balance": 100000.00,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        ]
    }
    
    # Save accounts to file
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    with open(data_dir / "accounts.json", "w") as f:
        json.dump(accounts, f, indent=2)
    
    print(f"    [OK] Created {len(accounts['accounts'])} sample accounts")
    for account in accounts['accounts']:
        print(f"         - {account['account_id']}: {account['account_holder']} (${account['balance']:.2f})")
    
    return accounts

def initialize_ledger():
    """Initialize transaction ledger"""
    print("\n[+] Initializing transaction ledger...")
    
    base_date = datetime.now() - timedelta(days=30)
    
    transactions = {
        "transactions": [
            {
                "transaction_id": "TXN001",
                "from_account": "ACC001",
                "to_account": "ACC002",
                "amount": 500.00,
                "type": "transfer",
                "description": "Payment for services",
                "timestamp": (base_date + timedelta(days=5)).isoformat(),
                "status": "completed"
            },
            {
                "transaction_id": "TXN002",
                "from_account": "ACC002",
                "to_account": "ACC001",
                "amount": 250.00,
                "type": "transfer",
                "description": "Refund",
                "timestamp": (base_date + timedelta(days=10)).isoformat(),
                "status": "completed"
            },
            {
                "transaction_id": "TXN003",
                "from_account": "ACC003",
                "to_account": "ACC004",
                "amount": 10000.00,
                "type": "investment",
                "description": "Investment deposit",
                "timestamp": (base_date + timedelta(days=15)).isoformat(),
                "status": "completed"
            },
            {
                "transaction_id": "TXN004",
                "from_account": "ACC001",
                "to_account": "ACC003",
                "amount": 1000.00,
                "type": "payment",
                "description": "Bill payment",
                "timestamp": (base_date + timedelta(days=20)).isoformat(),
                "status": "completed"
            },
            {
                "transaction_id": "TXN005",
                "from_account": "ACC002",
                "to_account": "ACC001",
                "amount": 750.00,
                "type": "transfer",
                "description": "Personal transfer",
                "timestamp": (base_date + timedelta(days=25)).isoformat(),
                "status": "pending"
            }
        ]
    }
    
    # Save transactions to file
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    with open(data_dir / "ledger.json", "w") as f:
        json.dump(transactions, f, indent=2)
    
    print(f"    [OK] Created {len(transactions['transactions'])} sample transactions")
    for txn in transactions['transactions']:
        print(f"         - {txn['transaction_id']}: {txn['from_account']} -> {txn['to_account']} (${txn['amount']:.2f})")
    
    return transactions

def initialize_users():
    """Initialize user accounts for authentication"""
    print("\n[+] Initializing user accounts...")
    
    users = {
        "users": [
            {
                "user_id": "USER001",
                "username": "admin",
                "email": "admin@bankplatform.local",
                "role": "administrator",
                "password_hash": "hashed_password_admin",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "user_id": "USER002",
                "username": "john_doe",
                "email": "john@example.com",
                "role": "customer",
                "password_hash": "hashed_password_john",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            },
            {
                "user_id": "USER003",
                "username": "jane_smith",
                "email": "jane@example.com",
                "role": "customer",
                "password_hash": "hashed_password_jane",
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        ]
    }
    
    # Save users to file
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    with open(data_dir / "users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    print(f"    [OK] Created {len(users['users'])} user accounts")
    for user in users['users']:
        print(f"         - {user['username']} ({user['role']})")
    
    return users

def main():
    """Main initialization orchestration"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   Bank Platform - Account & Ledger Initialization         ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Initialize components
        accounts = initialize_accounts()
        ledger = initialize_ledger()
        users = initialize_users()
        
        # Create summary
        print("""
╔═══════════════════════════════════════════════════════════╗
║              ✅ Initialization Complete!                  ║
╚═══════════════════════════════════════════════════════════╝

📊 Summary:
   • Accounts: 4 initialized
   • Transactions: 5 ledger entries
   • Users: 3 accounts created

📁 Data Files:
   • data/accounts.json
   • data/ledger.json
   • data/users.json

🚀 Next Steps:
1. Start the API:
   python -m src.api.main

2. Access the dashboard:
   http://localhost:5000

3. For admin panel (Streamlit):
   streamlit run admin_panel.py

✨ Your banking platform is ready!
        """)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
