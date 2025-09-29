"""
Payment Gateway Service
Handles payment processing with Stripe-like integration patterns
Python 3.10 compatible
"""

from flask import Flask, request, jsonify
from datetime import datetime
import logging
from payment_processor import PaymentProcessor
from auth_middleware import require_api_key
from database import db_session, init_db
from models import Transaction

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

processor = PaymentProcessor()

@app.before_first_request
def setup():
    init_db()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'payment-gateway',
        'version': '1.0.0',
        'python_version': '3.10'
    }), 200

@app.route('/api/v1/payment/process', methods=['POST'])
@require_api_key
def process_payment():
    """Process a payment transaction"""
    data = request.get_json()
    
    required_fields = ['amount', 'currency', 'card_number', 'cvv', 'expiry']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'required': required_fields
        }), 400
    
    result = processor.process_payment(
        amount=float(data['amount']),
        currency=data['currency'],
        card_number=data['card_number'],
        cvv=data['cvv'],
        expiry=data['expiry']
    )
    
    if result['status'] == 'failed':
        return jsonify(result), 400
    
    # Save to database
    transaction = Transaction(
        transaction_id=result['transaction_id'],
        amount=result['amount'],
        currency=result['currency'],
        status=result['status'],
        card_last_four=result['card_last_four']
    )
    db_session.add(transaction)
    db_session.commit()
    
    return jsonify(result), 200

@app.route('/api/v1/payment/transaction/<transaction_id>', methods=['GET'])
@require_api_key
def get_transaction(transaction_id):
    """Retrieve transaction details"""
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
    
    if not transaction:
        return jsonify({
            'error': 'Transaction not found'
        }), 404
    
    return jsonify(transaction.to_dict()), 200

@app.route('/api/v1/payment/refund', methods=['POST'])
@require_api_key
def refund_payment():
    """Refund a payment transaction"""
    data = request.get_json()
    
    if 'transaction_id' not in data:
        return jsonify({'error': 'Missing transaction_id'}), 400
    
    result = processor.refund_transaction(data['transaction_id'])
    return jsonify(result), 200 if result['status'] == 'refunded' else 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
