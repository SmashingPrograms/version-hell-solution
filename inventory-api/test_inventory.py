// inventory-api/test_inventory.py
"""
Test suite for inventory API service
"""

import pytest
from app import app
from inventory_manager import InventoryManager
from cache_manager import CacheManager
import json


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def manager():
    """Create inventory manager instance"""
    cache = CacheManager()
    return InventoryManager(cache)


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'inventory-api'


def test_get_item(client):
    """Test getting item inventory"""
    response = client.get('/api/v1/inventory/item/1001')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['item_id'] == 1001
    assert 'stock' in data
    assert 'reserved' in data
    assert 'available' in data


def test_get_nonexistent_item(client):
    """Test getting nonexistent item"""
    response = client.get('/api/v1/inventory/item/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


def test_check_availability(manager):
    """Test availability checking"""
    # Item 1001 has 47 stock, 3 reserved = 44 available
    assert manager.check_availability(1001, 40) == True
    assert manager.check_availability(1001, 50) == False


def test_reserve_items_success(manager):
    """Test successful item reservation"""
    items = [
        {'item_id': 1001, 'quantity': 5},
        {'item_id': 1002, 'quantity': 10}
    ]
    
    result = manager.reserve_items('order_001', items)
    
    assert result['status'] == 'reserved'
    assert result['order_id'] == 'order_001'
    assert result['items_reserved'] == 2
    
    # Verify reservation increased
    item = manager.get_item(1001)
    assert item['reserved'] == 8  # Was 3, now 8


def test_reserve_insufficient_stock(manager):
    """Test reservation fails with insufficient stock"""
    items = [
        {'item_id': 1001, 'quantity': 1000}  # Way more than available
    ]
    
    result = manager.reserve_items('order_002', items)
    
    assert result['status'] == 'failed'
    assert 'Insufficient inventory' in result['error']


def test_reserve_duplicate_order(manager):
    """Test cannot reserve same order twice"""
    items = [{'item_id': 1001, 'quantity': 5}]
    
    # First reservation succeeds
    result1 = manager.reserve_items('order_003', items)
    assert result1['status'] == 'reserved'
    
    # Second reservation fails
    result2 = manager.reserve_items('order_003', items)
    assert result2['status'] == 'failed'
    assert 'already has reservations' in result2['error']


def test_release_reservation(manager):
    """Test releasing reservation"""
    items = [{'item_id': 1001, 'quantity': 5}]
    
    # Reserve first
    manager.reserve_items('order_004', items)
    
    # Get current reserved amount
    item_before = manager.get_item(1001)
    reserved_before = item_before['reserved']
    
    # Release
    result = manager.release_reservation('order_004')
    assert result['status'] == 'released'
    
    # Verify reservation decreased
    item_after = manager.get_item(1001)
    assert item_after['reserved'] == reserved_before - 5


def test_adjust_inventory_increase(manager):
    """Test inventory adjustment (increase)"""
    item_before = manager.get_item(1001)
    old_stock = item_before['stock']
    
    result = manager.adjust_inventory(1001, 100, 'Received shipment')
    
    assert result['status'] == 'adjusted'
    assert result['new_stock'] == old_stock + 100
    assert result['adjustment'] == 100


def test_adjust_inventory_decrease(manager):
    """Test inventory adjustment (decrease)"""
    item_before = manager.get_item(1002)
    old_stock = item_before['stock']
    
    result = manager.adjust_inventory(1002, -10, 'Damaged items')
    
    assert result['status'] == 'adjusted'
    assert result['new_stock'] == old_stock - 10
    assert result['adjustment'] == -10


def test_adjust_inventory_negative_stock(manager):
    """Test adjustment cannot result in negative stock"""
    result = manager.adjust_inventory(1001, -10000, 'Invalid adjustment')
    
    assert 'error' in result
    assert 'negative stock' in result['error']


def test_get_low_stock_items(manager):
    """Test getting low stock items"""
    # Items 1008 (8 stock) and 1009 (5 stock) are low
    items = manager.get_low_stock_items(threshold=10)
    
    assert len(items) >= 2
    assert all(item['available'] <= 10 for item in items)
    
    # Should be sorted by available quantity
    for i in range(len(items) - 1):
        assert items[i]['available'] <= items[i + 1]['available']


def test_cache_functionality():
    """Test cache operations"""
    cache = CacheManager()
    
    # Set and get
    cache.set('test_key', {'data': 'test_value'}, ttl=60)
    result = cache.get('test_key')
    assert result == {'data': 'test_value'}
    
    # Cache hit
    assert cache.hits == 1
    
    # Cache miss
    result = cache.get('nonexistent_key')
    assert result is None
    assert cache.misses == 1
    
    # Delete
    cache.delete('test_key')
    result = cache.get('test_key')
    assert result is None
    
    # Clear
    cache.set('key1', 'value1')
    cache.set('key2', 'value2')
    cache.clear()
    assert cache.get('key1') is None
    assert cache.get('key2') is None


def test_cache_expiry():
    """Test cache TTL expiration"""
    import time
    
    cache = CacheManager()
    cache.set('expiring_key', 'value', ttl=1)  # 1 second TTL
    
    # Should be available immediately
    assert cache.get('expiring_key') == 'value'
    
    # Wait for expiration
    time.sleep(2)
    
    # Should be expired now
    assert cache.get('expiring_key') is None
