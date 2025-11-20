"""
Bank Platform - Admin Panel (Streamlit)
Account management, transaction monitoring, and user administration
"""

import streamlit as st  # pyright: ignore
import json
from pathlib import Path
from datetime import datetime
import pandas as pd  # pyright: ignore

# Page configuration
st.set_page_config(
    page_title="Bank Platform Admin",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def load_data(filename):
    """Load JSON data from file"""
    try:
        with open(Path("data") / filename) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(filename, data):
    """Save data to JSON file"""
    Path("data").mkdir(exist_ok=True)
    with open(Path("data") / filename, "w") as f:
        json.dump(data, f, indent=2)

# Main app
st.title("🏦 Bank Platform Admin Panel")

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Accounts", "Transactions", "Users", "Reports"]
)

# Dashboard Page
if page == "Dashboard":
    st.header("Dashboard Overview")
    
    # Load all data
    accounts_data = load_data("accounts.json")
    ledger_data = load_data("ledger.json")
    users_data = load_data("users.json")
    
    # Calculate metrics
    total_accounts = len(accounts_data.get("accounts", []))
    total_balance = sum(acc["balance"] for acc in accounts_data.get("accounts", []))
    total_transactions = len(ledger_data.get("transactions", []))
    active_users = len([u for u in users_data.get("users", []) if u.get("status") == "active"])
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Accounts", total_accounts)
    
    with col2:
        st.metric("Total Balance", f"${total_balance:,.2f}")
    
    with col3:
        st.metric("Transactions", total_transactions)
    
    with col4:
        st.metric("Active Users", active_users)
    
    st.divider()
    
    # Recent transactions
    st.subheader("Recent Transactions")
    transactions = ledger_data.get("transactions", [])
    if transactions:
        df = pd.DataFrame([
            {
                "ID": t["transaction_id"],
                "From": t["from_account"],
                "To": t["to_account"],
                "Amount": f"${t['amount']:.2f}",
                "Type": t["type"],
                "Status": t["status"]
            }
            for t in sorted(transactions, key=lambda x: x["timestamp"], reverse=True)[:5]
        ])
        st.dataframe(df, use_container_width=True)

# Accounts Page
elif page == "Accounts":
    st.header("Account Management")
    
    accounts_data = load_data("accounts.json")
    accounts = accounts_data.get("accounts", [])
    
    # Display accounts table
    if accounts:
        df = pd.DataFrame([
            {
                "Account ID": a["account_id"],
                "Holder": a["account_holder"],
                "Type": a["account_type"],
                "Balance": f"${a['balance']:,.2f}",
                "Status": a["status"]
            }
            for a in accounts
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No accounts found")
    
    st.divider()
    
    # Add new account
    st.subheader("Create New Account")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        account_id = st.text_input("Account ID", "ACC005")
    
    with col2:
        account_holder = st.text_input("Account Holder Name")
    
    with col3:
        account_type = st.selectbox("Account Type", ["Checking", "Savings", "Business", "Investment"])
    
    initial_balance = st.number_input("Initial Balance", value=0.00, min_value=0.00)
    
    if st.button("Create Account"):
        new_account = {
            "account_id": account_id,
            "account_holder": account_holder,
            "account_type": account_type,
            "balance": initial_balance,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        accounts.append(new_account)
        accounts_data["accounts"] = accounts
        save_data("accounts.json", accounts_data)
        st.success(f"Account {account_id} created successfully!")

# Transactions Page
elif page == "Transactions":
    st.header("Transaction Management")
    
    ledger_data = load_data("ledger.json")
    transactions = ledger_data.get("transactions", [])
    
    # Display transactions
    if transactions:
        df = pd.DataFrame([
            {
                "ID": t["transaction_id"],
                "From": t["from_account"],
                "To": t["to_account"],
                "Amount": f"${t['amount']:,.2f}",
                "Type": t["type"],
                "Description": t["description"],
                "Status": t["status"],
                "Date": t["timestamp"][:10]
            }
            for t in sorted(transactions, key=lambda x: x["timestamp"], reverse=True)
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No transactions found")

# Users Page
elif page == "Users":
    st.header("User Management")
    
    users_data = load_data("users.json")
    users = users_data.get("users", [])
    
    # Display users
    if users:
        df = pd.DataFrame([
            {
                "User ID": u["user_id"],
                "Username": u["username"],
                "Email": u["email"],
                "Role": u["role"],
                "Status": u["status"]
            }
            for u in users
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found")
    
    st.divider()
    
    # Add new user
    st.subheader("Create New User")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        user_id = st.text_input("User ID", "USER004")
    
    with col2:
        username = st.text_input("Username")
    
    with col3:
        email = st.text_input("Email")
    
    col1, col2 = st.columns(2)
    
    with col1:
        role = st.selectbox("Role", ["customer", "administrator", "manager"])
    
    with col2:
        password = st.text_input("Password", type="password")
    
    if st.button("Create User"):
        new_user = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role,
            "password_hash": "hashed_" + password,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        users.append(new_user)
        users_data["users"] = users
        save_data("users.json", users_data)
        st.success(f"User {username} created successfully!")

# Reports Page
elif page == "Reports":
    st.header("Reports & Analytics")
    
    accounts_data = load_data("accounts.json")
    ledger_data = load_data("ledger.json")
    
    # Account balance distribution
    st.subheader("Account Balance Distribution")
    accounts = accounts_data.get("accounts", [])
    if accounts:
        balance_data = {a["account_holder"]: a["balance"] for a in accounts}
        st.bar_chart(balance_data)
    
    # Transaction summary
    st.subheader("Transaction Summary")
    transactions = ledger_data.get("transactions", [])
    if transactions:
        # Group by type
        type_summary = {}
        for t in transactions:
            t_type = t["type"]
            type_summary[t_type] = type_summary.get(t_type, 0) + t["amount"]
        
        st.bar_chart(type_summary)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    if transactions:
        col1, col2, col3 = st.columns(3)
        
        total_volume = sum(t["amount"] for t in transactions)
        avg_amount = total_volume / len(transactions)
        max_amount = max(t["amount"] for t in transactions)
        
        with col1:
            st.metric("Total Transaction Volume", f"${total_volume:,.2f}")
        
        with col2:
            st.metric("Average Amount", f"${avg_amount:,.2f}")
        
        with col3:
            st.metric("Largest Transaction", f"${max_amount:,.2f}")

# Footer
st.divider()
st.markdown("""
---
**Bank Platform Admin Panel** | Built with Streamlit
""")
