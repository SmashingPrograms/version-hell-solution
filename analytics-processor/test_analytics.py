// analytics-processor/test_analytics.py
"""
Test suite for analytics processor service
"""

import pytest
from app import app
from analytics_engine import AnalyticsEngine
from report_generator import ReportGenerator
import json
from datetime import datetime, timedelta


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def engine():
    """Create analytics engine instance"""
    return AnalyticsEngine()


@pytest.fixture
def sample_transactions():
    """Generate sample transaction data"""
    transactions = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(100):
        transactions.append({
            'transaction_id': f'txn_{i:04d}',
            'amount': 50.0 + (i * 2.5),
            'timestamp': (base_date + timedelta(days=i % 30)).isoformat(),
            'customer_id': f'customer_{i % 20}',
            'product_id': f'product_{i % 10}'
        })
    
    return transactions


@pytest.fixture
def sample_customers():
    """Generate sample customer data"""
    base_date = datetime(2024, 1, 1)
    
    customers = []
    for i in range(50):
        customers.append({
            'customer_id': f'customer_{i}',
            'last_purchase_date': (base_date - timedelta(days=i * 5)).isoformat(),
            'purchase_count': 5 + (i % 10),
            'total_spend': 500.0 + (i * 100)
        })
    
    return customers


@pytest.fixture
def sample_products():
    """Generate sample product data"""
    products = []
    for i in range(20):
        products.append({
            'product_id': f'product_{i}',
            'product_name': f'Product {i}',
            'category': ['Electronics', 'Clothing', 'Books', 'Home'][i % 4],
            'units_sold': 100 + (i * 50),
            'revenue': 10000 + (i * 5000),
            'returns': 5 + (i % 10),
            'profit_margin': 0.20 + (i % 3) * 0.1
        })
    
    return products


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'analytics-processor'


def test_sales_summary(engine, sample_transactions):
    """Test sales summary generation"""
    summary = engine.generate_sales_summary(sample_transactions)
    
    assert 'total_transactions' in summary
    assert summary['total_transactions'] == 100
    assert 'total_revenue' in summary
    assert summary['total_revenue'] > 0
    assert 'average_transaction' in summary
    assert 'median_transaction' in summary
    assert 'percentiles' in summary


def test_sales_summary_empty_data(engine):
    """Test sales summary with no data"""
    summary = engine.generate_sales_summary([])
    
    assert 'error' in summary or summary['total_transactions'] == 0


def test_time_series_daily(engine, sample_transactions):
    """Test daily time series analysis"""
    analysis = engine.time_series_analysis(sample_transactions, 'daily')
    
    assert 'period' in analysis
    assert analysis['period'] == 'daily'
    assert 'time_series' in analysis
    assert len(analysis['time_series']) > 0
    assert 'trend' in analysis


def test_time_series_monthly(engine, sample_transactions):
    """Test monthly time series analysis"""
    analysis = engine.time_series_analysis(sample_transactions, 'monthly')
    
    assert analysis['period'] == 'monthly'
    assert 'time_series' in analysis
    
    # Check that each data point has required fields
    for data_point in analysis['time_series']:
        assert 'period' in data_point
        assert 'total_revenue' in data_point
        assert 'transaction_count' in data_point
        assert 'average_transaction' in data_point


def test_customer_segmentation(engine, sample_customers):
    """Test customer segmentation"""
    segments = engine.segment_customers(sample_customers)
    
    assert 'total_customers' in segments
    assert segments['total_customers'] == 50
    assert 'segments' in segments
    assert len(segments['segments']) > 0
    
    # Check segment structure
    for segment in segments['segments']:
        assert 'segment' in segment
        assert 'customer_count' in segment
        assert 'avg_recency' in segment
        assert 'avg_frequency' in segment
        assert 'avg_monetary' in segment


def test_customer_segmentation_rfm_scores(engine, sample_customers):
    """Test RFM score calculation in segmentation"""
    segments = engine.segment_customers(sample_customers)
    
    # Verify all customers are accounted for
    total_segmented = sum(seg['customer_count'] for seg in segments['segments'])
    assert total_segmented == len(sample_customers)
    
    # Verify percentages add up to 100
    total_percentage = sum(seg['percentage_of_customers'] for seg in segments['segments'])
    assert 99.0 <= total_percentage <= 101.0  # Allow for rounding


def test_product_performance(engine, sample_products):
    """Test product performance analysis"""
    performance = engine.analyze_product_performance(sample_products)
    
    assert 'total_products' in performance
    assert performance['total_products'] == 20
    assert 'total_revenue' in performance
    assert 'total_units_sold' in performance
    assert 'top_products_by_revenue' in performance
    assert 'top_products_by_units' in performance


def test_product_performance_rankings(engine, sample_products):
    """Test product ranking logic"""
    performance = engine.analyze_product_performance(sample_products)
    
    # Check top products are actually sorted
    top_revenue = performance['top_products_by_revenue']
    if len(top_revenue) > 1:
        for i in range(len(top_revenue) - 1):
            assert top_revenue[i]['revenue'] >= top_revenue[i + 1]['revenue']


def test_report_generation():
    """Test report generation"""
    generator = ReportGenerator()
    
    data = {
        'total_revenue': 100000,
        'transaction_count': 500,
        'average_transaction': 200,
        'period': 'January 2024'
    }
    
    report = generator.generate('summary', data, 'json')
    
    assert 'report_type' in report
    assert report['report_type'] == 'summary'
    assert 'generated_at' in report
    assert 'summary' in report


def test_executive_report_generation():
    """Test executive report generation"""
    generator = ReportGenerator()
    
    data = {
        'total_revenue': 100000,
        'growth_rate': 15.5,
        'customer_count': 250,
        'top_products': [
            {'product_name': 'Product A', 'revenue': 50000},
            {'product_name': 'Product B', 'revenue': 30000}
        ]
    }
    
    report = generator.generate('executive', data, 'json')
    
    assert report['report_type'] == 'executive'
    assert 'key_insights' in report
    assert 'recommendations' in report
    assert len(report['key_insights']) > 0


def test_recommendations_for_declining_growth():
    """Test that recommendations are generated for declining metrics"""
    generator = ReportGenerator()
    
    data = {
        'growth_rate': -10.0,  # Negative growth
        'total_revenue': 50000
    }
    
    report = generator.generate('detailed', data, 'json')
    
    assert 'recommendations' in report
    assert len(report['recommendations']) > 0
    assert any('decline' in rec.lower() for rec in report['recommendations'])


def test_csv_report_generation():
    """Test CSV format report generation"""
    generator = ReportGenerator()
    
    data = {
        'total_revenue': 100000,
        'transaction_count': 500
    }
    
    csv_output = generator.generate('summary', data, 'csv')
    
    assert isinstance(csv_output, str)
    assert len(csv_output) > 0


def test_api_sales_summary_endpoint(client, sample_transactions):
    """Test sales summary API endpoint"""
    response = client.post('/api/v1/analytics/sales-summary',
                          json={'transactions': sample_transactions})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_transactions' in data
    assert 'total_revenue' in data


def test_api_time_series_endpoint(client, sample_transactions):
    """Test time series API endpoint"""
    response = client.post('/api/v1/analytics/time-series',
                          json={
                              'transactions': sample_transactions,
                              'period': 'weekly'
                          })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'period' in data
    assert 'time_series' in data


def test_api_customer_segmentation_endpoint(client, sample_customers):
    """Test customer segmentation API endpoint"""
    response = client.post('/api/v1/analytics/customer-segments',
                          json={'customers': sample_customers})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'segments' in data
    assert 'total_customers' in data


def test_api_product_performance_endpoint(client, sample_products):
    """Test product performance API endpoint"""
    response = client.post('/api/v1/analytics/product-performance',
                          json={'products': sample_products})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'total_products' in data
    assert 'top_products_by_revenue' in data
