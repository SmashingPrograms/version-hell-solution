// payment-gateway/models.py
"""
Database models for payment transactions
"""

from sqlalchemy import Column, String, Float, DateTime, Integer
from datetime import datetime
from database import Base


class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(16), unique=True, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(String(20), nullable=False)
    card_last_four = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'transaction_id': self.transaction_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'card_last_four': self.card_last_four,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
