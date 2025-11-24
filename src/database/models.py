"""
Database Models
SQLAlchemy ORM models for banking operations
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Enum, Integer  # pyright: ignore
from sqlalchemy.ext.declarative import declarative_base  # pyright: ignore
from sqlalchemy.orm import relationship  # pyright: ignore
import enum
import uuid

Base = declarative_base()


class TransactionStatus(enum.Enum):
    """Transaction status"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionType(enum.Enum):
    """Transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"


class AccountType(enum.Enum):
    """Account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    BUSINESS = "business"
    INVESTMENT = "investment"


class UserRole(enum.Enum):
    """User roles"""
    ADMIN = "admin"
    CUSTOMER = "customer"
    MANAGER = "manager"


class User(Base):
    """User model"""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(80), nullable=True)
    last_name = Column(String(80), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")
    transactions_from = relationship(
        "Transaction",
        foreign_keys="Transaction.from_account_id",
        back_populates="from_account_rel"
    )
    transactions_to = relationship(
        "Transaction",
        foreign_keys="Transaction.to_account_id",
        back_populates="to_account_rel"
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role.value if self.role else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Account(Base):
    """Account model"""
    __tablename__ = 'accounts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(120), nullable=False)
    account_type = Column(Enum(AccountType), default=AccountType.CHECKING)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    balance = Column(Float, default=0.0)
    available_balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="accounts")
    transactions_from = relationship(
        "Transaction",
        foreign_keys="Transaction.from_account_id",
        back_populates="from_account"
    )
    transactions_to = relationship(
        "Transaction",
        foreign_keys="Transaction.to_account_id",
        back_populates="to_account"
    )

    def __repr__(self):
        return f'<Account {self.account_number}>'

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'account_name': self.account_name,
            'account_type': self.account_type.value if self.account_type else None,
            'owner_id': self.owner_id,
            'balance': self.balance,
            'available_balance': self.available_balance,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Transaction(Base):
    """Transaction model"""
    __tablename__ = 'transactions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id = Column(String(20), unique=True, nullable=False, index=True)
    from_account_id = Column(String(36), ForeignKey('accounts.id'), nullable=True)
    to_account_id = Column(String(36), ForeignKey('accounts.id'), nullable=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    description = Column(String(255), nullable=True)
    reference_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    from_account = relationship(
        "Account",
        foreign_keys=[from_account_id],
        back_populates="transactions_from"
    )
    to_account = relationship(
        "Account",
        foreign_keys=[to_account_id],
        back_populates="transactions_to"
    )

    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'from_account_id': self.from_account_id,
            'to_account_id': self.to_account_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type.value if self.transaction_type else None,
            'status': self.status.value if self.status else None,
            'description': self.description,
            'reference_number': self.reference_number,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Ledger(Base):
    """Ledger model for audit trail"""
    __tablename__ = 'ledgers'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False)
    transaction_id = Column(String(36), ForeignKey('transactions.id'), nullable=True)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    balance_after = Column(Float, nullable=False)
    entry_type = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Ledger {self.account_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'transaction_id': self.transaction_id,
            'debit': self.debit,
            'credit': self.credit,
            'balance_after': self.balance_after,
            'entry_type': self.entry_type,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


class VirtualCard(Base):
    """Virtual Card model for development/testing wallet provisioning"""
    __tablename__ = 'virtual_cards'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String(36), ForeignKey('accounts.id'), nullable=False)
    cardholder_name = Column(String(120), nullable=False)
    last4 = Column(String(4), nullable=False)
    exp_month = Column(Integer, nullable=False)
    exp_year = Column(Integer, nullable=False)
    status = Column(String(20), default='active')
    provisioning_token = Column(String(255), nullable=True)
    provisioned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", backref="virtual_cards")

    def __repr__(self):
        return f'<VirtualCard {self.last4}>'

    def to_dict(self):
        return {
            'id': self.id,
            'account_id': self.account_id,
            'cardholder_name': self.cardholder_name,
            'last4': self.last4,
            'exp_month': self.exp_month,
            'exp_year': self.exp_year,
            'status': self.status,
            'provisioning_token': self.provisioning_token,
            'provisioned': self.provisioned,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
