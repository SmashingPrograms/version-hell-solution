// payment-gateway/payment_processor.py
"""
Payment processing logic with realistic validation and transaction handling
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """Simulates payment processing with realistic patterns"""
    
    def __init__(self):
        self.processed_transactions = {}
        self.refunded_transactions = set()
    
    def generate_transaction_id(self, amount: float, currency: str, timestamp: str) -> str:
        """Generate unique transaction ID using SHA-256"""
        data = f"{amount}{currency}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def validate_card(self, card_number: str) -> bool:
        """Luhn algorithm for card validation"""
        if not card_number.isdigit():
            return False
        
        digits = [int(d) for d in card_number]
        checksum = 0
        
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            checksum += digit
        
        return checksum % 10 == 0
    
    def validate_expiry(self, expiry: str) -> bool:
        """Validate card expiry format MM/YY"""
        try:
            month, year = expiry.split('/')
            month_int = int(month)
            year_int = int(year)
            
            if not (1 <= month_int <= 12):
                return False
            
            current_year = datetime.now().year % 100
            current_month = datetime.now().month
            
            if year_int < current_year:
                return False
            if year_int == current_year and month_int < current_month:
                return False
            
            return True
        except (ValueError, AttributeError):
            return False
    
    def calculate_processing_fee(self, amount: float) -> float:
        """Calculate processing fee (2.9% + $0.30)"""
        return round(amount * 0.029 + 0.30, 2)
    
    def process_payment(self, amount: float, currency: str, card_number: str, 
                       cvv: str, expiry: str) -> Dict:
        """Process payment transaction with full validation"""
        
        # Amount validation
        if amount <= 0:
            return {
                'status': 'failed',
                'error': 'Invalid amount',
                'code': 'INVALID_AMOUNT'
            }
        
        if amount > 999999.99:
            return {
                'status': 'failed',
                'error': 'Amount exceeds maximum',
                'code': 'AMOUNT_TOO_LARGE'
            }
        
        # Card validation
        if not self.validate_card(card_number):
            return {
                'status': 'failed',
                'error': 'Invalid card number',
                'code': 'INVALID_CARD'
            }
        
        # CVV validation
        if len(cvv) not in [3, 4] or not cvv.isdigit():
            return {
                'status': 'failed',
                'error': 'Invalid CVV',
                'code': 'INVALID_CVV'
            }
        
        # Expiry validation
        if not self.validate_expiry(expiry):
            return {
                'status': 'failed',
                'error': 'Invalid or expired card',
                'code': 'INVALID_EXPIRY'
            }
        
        # Currency validation
        valid_currencies = ['USD', 'EUR', 'GBP', 'CAD', 'AUD']
        if currency not in valid_currencies:
            return {
                'status': 'failed',
                'error': f'Unsupported currency. Supported: {valid_currencies}',
                'code': 'INVALID_CURRENCY'
            }
        
        # Generate transaction
        timestamp = datetime.utcnow().isoformat()
        transaction_id = self.generate_transaction_id(amount, currency, timestamp)
        processing_fee = self.calculate_processing_fee(amount)
        
        transaction = {
            'transaction_id': transaction_id,
            'amount': amount,
            'currency': currency,
            'processing_fee': processing_fee,
            'net_amount': round(amount - processing_fee, 2),
            'status': 'processed',
            'timestamp': timestamp,
            'card_last_four': card_number[-4:],
            'card_type': self._detect_card_type(card_number),
            'processor': 'StripeSimulator',
            'processor_response_code': '00',
            'authorization_code': self._generate_auth_code()
        }
        
        self.processed_transactions[transaction_id] = transaction
        logger.info(f"Processed transaction: {transaction_id} for ${amount} {currency}")
        
        return transaction
    
    def _detect_card_type(self, card_number: str) -> str:
        """Detect card type from number"""
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif card_number.startswith(('34', '37')):
            return 'American Express'
        elif card_number.startswith('6'):
            return 'Discover'
        return 'Unknown'
    
    def _generate_auth_code(self) -> str:
        """Generate 6-digit authorization code"""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    def refund_transaction(self, transaction_id: str) -> Dict:
        """Refund a processed transaction"""
        if transaction_id not in self.processed_transactions:
            return {
                'status': 'failed',
                'error': 'Transaction not found',
                'code': 'TRANSACTION_NOT_FOUND'
            }
        
        if transaction_id in self.refunded_transactions:
            return {
                'status': 'failed',
                'error': 'Transaction already refunded',
                'code': 'ALREADY_REFUNDED'
            }
        
        transaction = self.processed_transactions[transaction_id]
        self.refunded_transactions.add(transaction_id)
        
        logger.info(f"Refunded transaction: {transaction_id}")
        
        return {
            'status': 'refunded',
            'transaction_id': transaction_id,
            'refund_amount': transaction['amount'],
            'refund_timestamp': datetime.utcnow().isoformat()
        }
