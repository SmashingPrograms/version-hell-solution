// inventory-api/app.py
"""
Inventory API Service
Manages product inventory with async database operations
Python 3.10 compatible
"""

from flask import Flask, request, jsonify
import logging
import asyncio
from inventory_manager import InventoryManager
from cache_manager import CacheManager

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize managers
cache_manager = CacheManager()
inventory_manager = InventoryManager(cache_manager)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'inventory-api',
        'version': '1.0.0',
        'python_version': '3.10',
        'cache_status': cache_manager.get_status()
    }), 200


@app.route('/api/v1/inventory/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get inventory for specific item"""
    result = inventory_manager.get_item(item_id)
    
    if result.get('error'):
        return jsonify(result), 404
    
    return jsonify(result), 200


@app.route('/api/v1/inventory/check', methods=['POST'])
def check_availability():
    """Check if items are available"""
    data = request.get_json()
    
    if 'items' not in data:
        return jsonify({'error': 'Missing items list'}), 400
    
    results = []
    for item_request in data['items']:
        item_id = item_request.get('item_id')
        quantity = item_request.get('quantity', 1)
        
        if not item_id:
            results.append({'error': 'Missing item_id'})
            continue
        
        available = inventory_manager.check_availability(item_id, quantity)
        results.append({
            'item_id': item_id,
            'requested_quantity': quantity,
            'available': available
        })
    
    return jsonify({'results': results}), 200


@app.route('/api/v1/inventory/reserve', methods=['POST'])
def reserve_items():
    """Reserve inventory for order"""
    data = request.get_json()
    
    required_fields = ['order_id', 'items']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = inventory_manager.reserve_items(
        data['order_id'],
        data['items']
    )
    
    if result.get('status') == 'failed':
        return jsonify(result), 400
    
    return jsonify(result), 200


@app.route('/api/v1/inventory/release', methods=['POST'])
def release_reservation():
    """Release reserved inventory"""
    data = request.get_json()
    
    if 'order_id' not in data:
        return jsonify({'error': 'Missing order_id'}), 400
    
    result = inventory_manager.release_reservation(data['order_id'])
    return jsonify(result), 200


@app.route('/api/v1/inventory/adjust', methods=['POST'])
def adjust_inventory():
    """Adjust inventory levels (admin operation)"""
    data = request.get_json()
    
    required_fields = ['item_id', 'adjustment', 'reason']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = inventory_manager.adjust_inventory(
        data['item_id'],
        data['adjustment'],
        data['reason']
    )
    
    return jsonify(result), 200


@app.route('/api/v1/inventory/low-stock', methods=['GET'])
def get_low_stock():
    """Get items with low stock levels"""
    threshold = request.args.get('threshold', 10, type=int)
    items = inventory_manager.get_low_stock_items(threshold)
    
    return jsonify({
        'threshold': threshold,
        'count': len(items),
        'items': items
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=False)
