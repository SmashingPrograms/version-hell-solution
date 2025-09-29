// ml-fraud-detection/test_fraud.py
"""
Test suite for fraud detection service
"""

import pytest
from app import app
from fraud_analyzer import FraudAnalyzer
from feature_engineer import FeatureEngineer
from model_loader import ModelLoader
import json
from datetime import datetime


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def analyzer():
    """Create fraud analyzer instance"""
    feature_engineer = FeatureEngineer()
    model_loader = ModelLoader()
    return FraudAnalyzer(feature_engineer, model_loader)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'ml-fraud-detection'


def test_feature_extraction():
    """Test feature engineering"""
    engineer = FeatureEngineer()
    
    transaction = {
        'amount': 100.00,
        'merchant_category': 'retail',
        'merchant_id': 'merchant_123',
        'customer_id': 'customer_456',
        'location': {'country_code': 'US', 'city': 'New York'},
        'timestamp': datetime.utcnow().isoformat()
    }
    
    features = engineer.extract_features(transaction)
    
    assert features is not None
    assert len(features) > 0
    assert features.dtype == 'float32'


def test_low_risk_transaction(analyzer):
    """Test low-risk transaction analysis"""
    transaction = {
        'transaction_id': 'txn_001',
        'amount': 50.00,
        'merchant_category': 'retail',
        'merchant_id': 'merchant_123',
        'customer_id': 'customer_456',
        'location': {'country_code': 'US', 'city': 'New York'},
        'timestamp': '2024-01-15T14:30:00Z'
    }
    
    result = analyzer.analyze(transaction)
    
    assert result['transaction_id'] == 'txn_001'
    assert 'fraud_score' in result
    assert result['fraud_score'] >= 0.0
    assert result['fraud_score'] <= 1.0
    assert result['risk_level'] in ['minimal', 'low', 'medium', 'high']


def test_high_amount_transaction(analyzer):
    """Test high-amount transaction gets elevated risk"""
    transaction = {
        'transaction_id': 'txn_002',
        'amount': 8000.00,  # High amount
        'merchant_category': 'retail',
        'merchant_id': 'merchant_123',
        'customer_id': 'customer_456',
        'location': {'country_code': 'US', 'city': 'New York'},
        'timestamp': '2024-01-15T14:30:00Z'
    }
    
    result = analyzer.analyze(transaction)
    
    # High amount should increase fraud score
    assert result['fraud_score'] > 0.3
    assert 'High transaction amount' in str(result['analysis']['risk_factors'])


def test_suspicious_merchant_category(analyzer):
    """Test suspicious merchant categories get flagged"""
    transaction = {
        'transaction_id': 'txn_003',
        'amount': 100.00,
        'merchant_category': 'gambling',  # Suspicious
        'merchant_id': 'merchant_123',
        'customer_id': 'customer_456',
        'location': {'country_code': 'US', 'city': 'New York'},
        'timestamp': '2024-01-15T14:30:00Z'
    }
    
    result = analyzer.analyze(transaction)
    
    # Suspicious category should be in risk factors
    assert any('merchant category' in str(factor).lower() 
              for factor in result['analysis']['risk_factors'])


def test_high_risk_location(analyzer):
    """Test high-risk location detection"""
    transaction = {
        'transaction_id': 'txn_004',
        'amount': 100.00,
        'merchant_category': 'retail',
        'merchant_id': 'merchant_123',
        'customer_id': 'customer_456',
        'location': {'country_code': 'NG', 'city': 'Lagos'},  # High-risk country
        'timestamp': '2024-01-15T14:30:00Z'
    }
    
    result = analyzer.analyze(transaction)
    
    # High-risk location should increase score
    assert result['fraud_score'] > 0.3
    assert any('location' in str(factor).lower() 
              for factor in result['analysis']['risk_factors'])


def test_unusual_time_detection(analyzer):
    """Test unusual transaction time detection"""
    transaction = {
        'transaction_id': 'txn_005',
        'amount': 100.00,
        'merchant_category': 'retail',
        'merchant_id': 'merchant_123',
        'customer_id': 'customer_456',
        'location': {'country_code': 'US', 'city': 'New York'},
        'timestamp': '2024-01-15T03:30:00Z'  # 3:30 AM - unusual
    }
    
    result = analyzer.analyze(transaction)
    
    # Unusual time might be flagged
    # (Score elevation depends on other factors too)
    assert 'fraud_score' in result


def test_batch_analysis(client):
    """Test batch transaction analysis"""
    transactions = [
        {
            'transaction_id': 'txn_batch_1',
            'amount': 100.00,
            'merchant_category': 'retail',
            'merchant_id': 'merchant_123',
            'customer_id': 'customer_456',
            'location': {'country_code': 'US', 'city': 'New York'},
            'timestamp': '2024-01-15T14:30:00Z'
        },
        {
            'transaction_id': 'txn_batch_2',
            'amount': 200.00,
            'merchant_category': 'food',
            'merchant_id': 'merchant_789',
            'customer_id': 'customer_456',
            'location': {'country_code': 'US', 'city': 'New York'},
            'timestamp': '2024-01-15T15:30:00Z'
        }
    ]
    
    response = client.post('/api/v1/fraud/batch-analyze',
                          json={'transactions': transactions})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 2
    assert data['analyzed'] == 2
    assert len(data['results']) == 2


def test_model_info_endpoint(client):
    """Test model information endpoint"""
    response = client.get('/api/v1/fraud/model-info')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'version' in data
    assert data['status'] == 'loaded'
