// payment-gateway/test_payment.py
"""
Test suite for payment gateway service
"""

import pytest
from app import app
from payment_processor import PaymentProcessor
import json


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def processor():
    """Create payment processor instance"""
    return PaymentProcessor()


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'payment-gateway'


def test_card_validation(processor):
    """Test Luhn algorithm card validation"""
    # Valid card numbers
    assert processor.validate_card('4532015112830366') == True  # Visa
    assert processor.validate_card('5425233430109903') == True  # Mastercard
    
    # Invalid card numbers
    assert processor.validate_card('1234567812345678') == False
    assert processor.validate_card('') == False
    assert processor.validate_card('abcd') == False


def test_expiry_validation(processor):
    """Test card expiry validation"""
    assert processor.validate_expiry('12/25') == True
    assert processor.validate_expiry('01/30') == True
    
    # Invalid formats
    assert processor.validate_expiry('13/25') == False  # Invalid month
    assert processor.validate_expiry('00/25') == False  # Invalid month
    assert processor.validate_expiry('12/20') == False  # Past date


def test_process_payment_success(processor):
    """Test successful payment processing"""
    result = processor.process_payment(
        amount=100.00,
        currency='USD',
        card_number='4532015112830366',
        cvv='123',
        expiry='12/25'
    )
    
    assert result['status'] == 'processed'
    assert result['amount'] == 100.00
    assert result['currency'] == 'USD'
    assert 'transaction_id' in result
    assert result['card_last_four'] == '0366'


def test_process_payment_invalid_card(processor):
    """Test payment with invalid card"""
    result = processor.process_payment(
        amount=100.00,
        currency='USD',
        card_number='1234567812345678',
        cvv='123',
        expiry='12/25'
    )
    
    assert result['status'] == 'failed'
    assert result['code'] == 'INVALID_CARD'


def test_process_payment_invalid_amount(processor):
    """Test payment with invalid amount"""
    result = processor.process_payment(
        amount=-50.00,
        currency='USD',
        card_number='4532015112830366',
        cvv='123',
        expiry='12/25'
    )
    
    assert result['status'] == 'failed'
    assert result['code'] == 'INVALID_AMOUNT'


def test_processing_fee_calculation(processor):
    """Test processing fee calculation"""
    fee = processor.calculate_processing_fee(100.00)
    expected_fee = round(100.00 * 0.029 + 0.30, 2)
    assert fee == expected_fee


def test_refund_transaction(processor):
    """Test transaction refund"""
    # First process a payment
    payment_result = processor.process_payment(
        amount=50.00,
        currency='USD',
        card_number='4532015112830366',
        cvv='123',
        expiry='12/25'
    )
    
    transaction_id = payment_result['transaction_id']
    
    # Now refund it
    refund_result = processor.refund_transaction(transaction_id)
    
    assert refund_result['status'] == 'refunded'
    assert refund_result['refund_amount'] == 50.00
    
    # Try to refund again (should fail)
    second_refund = processor.refund_transaction(transaction_id)
    assert second_refund['status'] == 'failed'
    assert second_refund['code'] == 'ALREADY_REFUNDED'


def test_api_key_required(client):
    """Test that API key is required for protected endpoints"""
    response = client.post('/api/v1/payment/process', json={
        'amount': 100.00,
        'currency': 'USD',
        'card_number': '4532015112830366',
        'cvv': '123',
        'expiry': '12/25'
    })
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Missing API key' in data['error']


def test_payment_with_valid_api_key(client):
    """Test payment processing with valid API key"""
    headers = {'X-API-Key': 'test_key_12345'}
    
    response = client.post('/api/v1/payment/process', 
        headers=headers,
        json={
            'amount': 100.00,
            'currency': 'USD',
            'card_number': '4532015112830366',
            'cvv': '123',
            'expiry': '12/25'
        })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'processed'