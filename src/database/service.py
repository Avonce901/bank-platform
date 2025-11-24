"""
Database Service
Manages database connections and operations
"""
from sqlalchemy import create_engine  # pyright: ignore
from sqlalchemy.orm import sessionmaker, Session  # pyright: ignore
from contextlib import contextmanager
import os
from src.database.models import Base, User, Account, Transaction, Ledger, VirtualCard  # pyright: ignore


class DatabaseService:
    """Database service for managing connections"""

    def __init__(self, database_url: str | None = None):  # type: ignore
        """Initialize database service"""
        if database_url is None:
            database_url = os.getenv(
                'DATABASE_URL',
                'sqlite:///./bank_platform.db'
            )
        
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def init_db(self):
        """Initialize database tables"""
        Base.metadata.create_all(bind=self.engine)
        print("✓ Database tables created/verified")

    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_user(self, username: str, email: str, password_hash: str, 
                   first_name: str | None = None, last_name: str | None = None) -> User:  # type: ignore
        """Create a new user"""
        with self.session_scope() as session:
            user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            session.flush()
            return user.to_dict()

    def get_user_by_username(self, username: str) -> User:
        """Get user by username"""
        with self.session_scope() as session:
            return session.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        with self.session_scope() as session:
            return session.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: str) -> User:
        """Get user by ID"""
        with self.session_scope() as session:
            return session.query(User).filter(User.id == user_id).first()

    def create_account(self, account_number: str, account_name: str, 
                      owner_id: str, account_type: str = "checking", 
                      initial_balance: float = 0.0) -> Account:
        """Create a new account"""
        with self.session_scope() as session:
            account = Account(
                account_number=account_number,
                account_name=account_name,
                owner_id=owner_id,
                account_type=account_type,
                balance=initial_balance,
                available_balance=initial_balance
            )
            session.add(account)
            session.flush()
            return account.to_dict()

    def get_account_by_number(self, account_number: str) -> Account:
        """Get account by account number"""
        with self.session_scope() as session:
            return session.query(Account).filter(
                Account.account_number == account_number
            ).first()

    def get_account_by_id(self, account_id: str) -> Account:
        """Get account by ID"""
        with self.session_scope() as session:
            return session.query(Account).filter(Account.id == account_id).first()

    def get_user_accounts(self, user_id: str) -> list:
        """Get all accounts for a user"""
        with self.session_scope() as session:
            accounts = session.query(Account).filter(
                Account.owner_id == user_id
            ).all()
            return [acc.to_dict() for acc in accounts]

    def update_account_balance(self, account_id: str, new_balance: float) -> bool:
        """Update account balance"""
        with self.session_scope() as session:
            account = session.query(Account).filter(Account.id == account_id).first()
            if account:
                account.balance = new_balance
                account.available_balance = new_balance
                session.flush()
                return True
            return False

    def create_transaction(self, transaction_type: str, amount: float,
                          from_account_id: str | None = None, to_account_id: str | None = None,
                          description: str | None = None, status: str = "completed") -> Transaction:  # type: ignore
        """Create a new transaction"""
        import uuid
        with self.session_scope() as session:
            transaction = Transaction(
                transaction_id=f"TXN-{uuid.uuid4().hex[:10].upper()}",
                from_account_id=from_account_id,
                to_account_id=to_account_id,
                amount=amount,
                transaction_type=transaction_type,
                status=status,
                description=description
            )
            session.add(transaction)
            session.flush()
            return transaction.to_dict()

    def get_account_transactions(self, account_id: str, limit: int = 50) -> list:
        """Get transactions for an account"""
        with self.session_scope() as session:
            transactions = session.query(Transaction).filter(
                (Transaction.from_account_id == account_id) |
                (Transaction.to_account_id == account_id)
            ).order_by(Transaction.created_at.desc()).limit(limit).all()
            return [t.to_dict() for t in transactions]

    def create_ledger_entry(self, account_id: str, debit: float = 0.0,
                           credit: float = 0.0, balance_after: float = 0.0,
                           entry_type: str | None = None, description: str | None = None,
                           transaction_id: str | None = None) -> Ledger:  # type: ignore
        """Create ledger entry"""
        with self.session_scope() as session:
            ledger = Ledger(
                account_id=account_id,
                transaction_id=transaction_id,
                debit=debit,
                credit=credit,
                balance_after=balance_after,
                entry_type=entry_type,
                description=description
            )
            session.add(ledger)
            session.flush()
            return ledger.to_dict()

    def get_account_ledger(self, account_id: str, limit: int = 100) -> list:
        """Get ledger entries for account"""
        with self.session_scope() as session:
            entries = session.query(Ledger).filter(
                Ledger.account_id == account_id
            ).order_by(Ledger.created_at.desc()).limit(limit).all()
            return [e.to_dict() for e in entries]

    def close(self):
        """Close database connection"""
        self.engine.dispose()


# Global database instance
_db_service = None


def get_db_service() -> DatabaseService:
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service


def init_database():
    """Initialize database"""
    db = get_db_service()
    db.init_db()
