"""
Banking Operations Routes
Transfer, deposit, withdrawal, balance check endpoints
"""
from flask import Blueprint, jsonify, request, g
from src.auth.service import get_auth_service
from src.database.service import get_db_service
from datetime import datetime

banking_bp = Blueprint('banking', __name__, url_prefix='/api/v1/banking')
auth_service = get_auth_service()
db_service = get_db_service()


@banking_bp.route('/accounts', methods=['GET'])
@auth_service.require_auth()
def get_accounts():
    """Get all accounts for current user"""
    try:
        user_id = g.user_id
        accounts = db_service.get_user_accounts(user_id)
        
        return jsonify({
            'success': True,
            'accounts': accounts,
            'total_accounts': len(accounts)
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve accounts: {str(e)}',
            'error_code': 'ACCOUNT_FETCH_FAILED'
        }), 500


@banking_bp.route('/accounts/<account_id>', methods=['GET'])
@auth_service.require_auth()
def get_account_details(account_id):
    """Get account details"""
    try:
        account = db_service.get_account_by_id(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get recent transactions
        transactions = db_service.get_account_transactions(account_id, limit=10)
        
        return jsonify({
            'success': True,
            'account': account.to_dict(),
            'recent_transactions': transactions
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve account: {str(e)}',
            'error_code': 'ACCOUNT_FETCH_FAILED'
        }), 500


@banking_bp.route('/accounts/<account_id>/balance', methods=['GET'])
@auth_service.require_auth()
def get_balance(account_id):
    """Get account balance"""
    try:
        account = db_service.get_account_by_id(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        return jsonify({
            'success': True,
            'account_id': account_id,
            'balance': account.balance,
            'available_balance': account.available_balance,
            'last_updated': account.updated_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve balance: {str(e)}',
            'error_code': 'BALANCE_FETCH_FAILED'
        }), 500


@banking_bp.route('/deposit', methods=['POST'])
@auth_service.require_auth()
def deposit():
    """Deposit money into account
    
    Expected JSON:
    {
        "account_id": "...",
        "amount": 1000.00,
        "description": "Cash deposit"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        required_fields = ['account_id', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        account_id = data['account_id']
        amount = float(data['amount'])
        description = data.get('description', 'Deposit')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        account = db_service.get_account_by_id(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Create transaction
        transaction = db_service.create_transaction(
            transaction_type='deposit',
            amount=amount,
            to_account_id=account_id,
            description=description,
            status='completed'
        )
        
        # Update account balance
        new_balance = account.balance + amount
        db_service.update_account_balance(account_id, new_balance)
        
        # Create ledger entry
        db_service.create_ledger_entry(
            account_id=account_id,
            credit=amount,
            balance_after=new_balance,
            entry_type='deposit',
            description=description,
            transaction_id=transaction['id']
        )
        
        return jsonify({
            'success': True,
            'message': f'Deposit of ${amount:,.2f} successful',
            'transaction': transaction,
            'new_balance': new_balance
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Deposit failed: {str(e)}',
            'error_code': 'DEPOSIT_FAILED'
        }), 500


@banking_bp.route('/withdraw', methods=['POST'])
@auth_service.require_auth()
def withdraw():
    """Withdraw money from account
    
    Expected JSON:
    {
        "account_id": "...",
        "amount": 500.00,
        "description": "ATM withdrawal"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        required_fields = ['account_id', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        account_id = data['account_id']
        amount = float(data['amount'])
        description = data.get('description', 'Withdrawal')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        account = db_service.get_account_by_id(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Check sufficient funds
        if account.balance < amount:
            return jsonify({
                'error': 'Insufficient funds',
                'available_balance': account.balance
            }), 400
        
        # Create transaction
        transaction = db_service.create_transaction(
            transaction_type='withdrawal',
            amount=amount,
            from_account_id=account_id,
            description=description,
            status='completed'
        )
        
        # Update account balance
        new_balance = account.balance - amount
        db_service.update_account_balance(account_id, new_balance)
        
        # Create ledger entry
        db_service.create_ledger_entry(
            account_id=account_id,
            debit=amount,
            balance_after=new_balance,
            entry_type='withdrawal',
            description=description,
            transaction_id=transaction['id']
        )
        
        return jsonify({
            'success': True,
            'message': f'Withdrawal of ${amount:,.2f} successful',
            'transaction': transaction,
            'new_balance': new_balance
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Withdrawal failed: {str(e)}',
            'error_code': 'WITHDRAWAL_FAILED'
        }), 500


@banking_bp.route('/transfer', methods=['POST'])
@auth_service.require_auth()
def transfer():
    """Transfer money between accounts
    
    Expected JSON:
    {
        "from_account_id": "...",
        "to_account_number": "ACC002",
        "amount": 250.00,
        "description": "Payment to Jane"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        required_fields = ['from_account_id', 'to_account_number', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        from_account_id = data['from_account_id']
        to_account_number = data['to_account_number']
        amount = float(data['amount'])
        description = data.get('description', 'Transfer')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Get from account
        from_account = db_service.get_account_by_id(from_account_id)
        
        if not from_account:
            return jsonify({'error': 'From account not found'}), 404
        
        # Verify ownership
        if from_account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Get to account
        to_account = db_service.get_account_by_number(to_account_number)
        
        if not to_account:
            return jsonify({'error': 'To account not found'}), 404
        
        # Check sufficient funds
        if from_account.balance < amount:
            return jsonify({
                'error': 'Insufficient funds',
                'available_balance': from_account.balance
            }), 400
        
        # Create transfer transaction
        transaction = db_service.create_transaction(
            transaction_type='transfer',
            amount=amount,
            from_account_id=from_account_id,
            to_account_id=to_account.id,
            description=description,
            status='completed'
        )
        
        # Update from account balance
        from_new_balance = from_account.balance - amount
        db_service.update_account_balance(from_account_id, from_new_balance)
        
        # Update to account balance
        to_new_balance = to_account.balance + amount
        db_service.update_account_balance(to_account.id, to_new_balance)
        
        # Create ledger entries
        db_service.create_ledger_entry(
            account_id=from_account_id,
            debit=amount,
            balance_after=from_new_balance,
            entry_type='transfer_out',
            description=f"{description} to {to_account_number}",
            transaction_id=transaction['id']
        )
        
        db_service.create_ledger_entry(
            account_id=to_account.id,
            credit=amount,
            balance_after=to_new_balance,
            entry_type='transfer_in',
            description=f"{description} from {from_account.account_number}",
            transaction_id=transaction['id']
        )
        
        return jsonify({
            'success': True,
            'message': f'Transfer of ${amount:,.2f} successful',
            'transaction': transaction,
            'from_account_balance': from_new_balance,
            'to_account_balance': to_new_balance
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Transfer failed: {str(e)}',
            'error_code': 'TRANSFER_FAILED'
        }), 500


@banking_bp.route('/accounts/<account_id>/transactions', methods=['GET'])
@auth_service.require_auth()
def get_account_transactions(account_id):
    """Get transaction history for account"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        account = db_service.get_account_by_id(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        transactions = db_service.get_account_transactions(account_id, limit)
        
        return jsonify({
            'success': True,
            'account_id': account_id,
            'transactions': transactions,
            'total_transactions': len(transactions)
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve transactions: {str(e)}',
            'error_code': 'TRANSACTION_FETCH_FAILED'
        }), 500


@banking_bp.route('/accounts/<account_id>/ledger', methods=['GET'])
@auth_service.require_auth()
def get_account_ledger(account_id):
    """Get ledger entries for account"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        account = db_service.get_account_by_id(account_id)
        
        if not account:
            return jsonify({'error': 'Account not found'}), 404
        
        # Verify ownership
        if account.owner_id != g.user_id:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        ledger = db_service.get_account_ledger(account_id, limit)
        
        return jsonify({
            'success': True,
            'account_id': account_id,
            'ledger': ledger,
            'total_entries': len(ledger)
        }), 200
    except Exception as e:
        return jsonify({
            'error': f'Failed to retrieve ledger: {str(e)}',
            'error_code': 'LEDGER_FETCH_FAILED'
        }), 500
