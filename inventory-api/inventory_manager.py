// inventory-api/inventory_manager.py
"""
Core inventory management logic with caching
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class InventoryManager:
    """Manages product inventory with thread-safe operations"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
        self.lock = threading.RLock()
        
        # In-memory inventory (in production, this would be a database)
        self.inventory = self._initialize_inventory()
        self.reservations = {}  # order_id -> {item_id: quantity}
        self.adjustment_log = []
    
    def _initialize_inventory(self) -> Dict[int, Dict]:
        """Initialize sample inventory data"""
        return {
            1001: {'item_id': 1001, 'name': 'Laptop Pro 15"', 'stock': 47, 'reserved': 3, 'sku': 'LAP-PRO-15'},
            1002: {'item_id': 1002, 'name': 'Wireless Mouse', 'stock': 234, 'reserved': 12, 'sku': 'MSE-WRL-01'},
            1003: {'item_id': 1003, 'name': 'Mechanical Keyboard', 'stock': 89, 'reserved': 5, 'sku': 'KBD-MCH-01'},
            1004: {'item_id': 1004, 'name': 'USB-C Hub', 'stock': 156, 'reserved': 8, 'sku': 'HUB-USC-01'},
            1005: {'item_id': 1005, 'name': '27" Monitor 4K', 'stock': 23, 'reserved': 2, 'sku': 'MON-27-4K'},
            1006: {'item_id': 1006, 'name': 'Webcam HD Pro', 'stock': 78, 'reserved': 6, 'sku': 'WBC-HD-PRO'},
            1007: {'item_id': 1007, 'name': 'Desk Lamp LED', 'stock': 142, 'reserved': 4, 'sku': 'LMP-DSK-LED'},
            1008: {'item_id': 1008, 'name': 'Cable Organizer', 'stock': 8, 'reserved': 1, 'sku': 'ORG-CBL-01'},
            1009: {'item_id': 1009, 'name': 'Laptop Stand', 'stock': 5, 'reserved': 0, 'sku': 'STD-LAP-01'},
            1010: {'item_id': 1010, 'name': 'Headphones Noise Cancel', 'stock': 112, 'reserved': 15, 'sku': 'HDP-NC-01'},
        }
    
    def get_item(self, item_id: int) -> Dict:
        """Get inventory information for an item"""
        # Check cache first
        cached = self.cache.get(f'item:{item_id}')
        if cached:
            logger.debug(f"Cache hit for item {item_id}")
            return cached
        
        with self.lock:
            if item_id not in self.inventory:
                return {'error': 'Item not found', 'item_id': item_id}
            
            item = self.inventory[item_id].copy()
            item['available'] = item['stock'] - item['reserved']
            item['last_checked'] = datetime.utcnow().isoformat()
            
            # Cache the result
            self.cache.set(f'item:{item_id}', item, ttl=60)
            
            return item
    
    def check_availability(self, item_id: int, quantity: int) -> bool:
        """Check if requested quantity is available"""
        with self.lock:
            if item_id not in self.inventory:
                return False
            
            item = self.inventory[item_id]
            available = item['stock'] - item['reserved']
            
            return available >= quantity
    
    def reserve_items(self, order_id: str, items: List[Dict]) -> Dict:
        """
        Reserve inventory for an order
        
        Args:
            order_id: Unique order identifier
            items: List of {item_id, quantity} dicts
        
        Returns:
            Result dictionary with status
        """
        with self.lock:
            # Check if order already has reservations
            if order_id in self.reservations:
                return {
                    'status': 'failed',
                    'error': 'Order already has reservations',
                    'order_id': order_id
                }
            
            # Validate all items are available first
            for item_request in items:
                item_id = item_request['item_id']
                quantity = item_request['quantity']
                
                if not self.check_availability(item_id, quantity):
                    return {
                        'status': 'failed',
                        'error': f'Insufficient inventory for item {item_id}',
                        'item_id': item_id,
                        'requested': quantity,
                        'available': self.inventory[item_id]['stock'] - self.inventory[item_id]['reserved']
                    }
            
            # All items available - reserve them
            reservation_details = {}
            for item_request in items:
                item_id = item_request['item_id']
                quantity = item_request['quantity']
                
                self.inventory[item_id]['reserved'] += quantity
                reservation_details[item_id] = quantity
                
                # Invalidate cache
                self.cache.delete(f'item:{item_id}')
                
                logger.info(f"Reserved {quantity} units of item {item_id} for order {order_id}")
            
            self.reservations[order_id] = {
                'items': reservation_details,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return {
                'status': 'reserved',
                'order_id': order_id,
                'items_reserved': len(reservation_details),
                'reservation_details': reservation_details
            }
    
    def release_reservation(self, order_id: str) -> Dict:
        """Release reserved inventory for an order"""
        with self.lock:
            if order_id not in self.reservations:
                return {
                    'status': 'not_found',
                    'error': 'No reservation found for order',
                    'order_id': order_id
                }
            
            reservation = self.reservations[order_id]
            
            for item_id, quantity in reservation['items'].items():
                self.inventory[item_id]['reserved'] -= quantity
                
                # Invalidate cache
                self.cache.delete(f'item:{item_id}')
                
                logger.info(f"Released {quantity} units of item {item_id} from order {order_id}")
            
            del self.reservations[order_id]
            
            return {
                'status': 'released',
                'order_id': order_id,
                'items_released': len(reservation['items'])
            }
    
    def adjust_inventory(self, item_id: int, adjustment: int, reason: str) -> Dict:
        """
        Adjust inventory levels (for receiving stock, damage, theft, etc.)
        
        Args:
            item_id: Item to adjust
            adjustment: Amount to adjust (positive or negative)
            reason: Reason for adjustment
        """
        with self.lock:
            if item_id not in self.inventory:
                return {'error': 'Item not found', 'item_id': item_id}
            
            old_stock = self.inventory[item_id]['stock']
            new_stock = old_stock + adjustment
            
            if new_stock < 0:
                return {
                    'error': 'Adjustment would result in negative stock',
                    'item_id': item_id,
                    'current_stock': old_stock,
                    'adjustment': adjustment
                }
            
            self.inventory[item_id]['stock'] = new_stock
            
            # Log the adjustment
            log_entry = {
                'item_id': item_id,
                'old_stock': old_stock,
                'new_stock': new_stock,
                'adjustment': adjustment,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat()
            }
            self.adjustment_log.append(log_entry)
            
            # Invalidate cache
            self.cache.delete(f'item:{item_id}')
            
            logger.info(f"Adjusted inventory for item {item_id}: {old_stock} -> {new_stock} ({reason})")
            
            return {
                'status': 'adjusted',
                'item_id': item_id,
                'old_stock': old_stock,
                'new_stock': new_stock,
                'adjustment': adjustment,
                'reason': reason
            }
    
    def get_low_stock_items(self, threshold: int = 10) -> List[Dict]:
        """Get items below stock threshold"""
        with self.lock:
            low_stock = []
            
            for item_id, item in self.inventory.items():
                available = item['stock'] - item['reserved']
                
                if available <= threshold:
                    low_stock.append({
                        'item_id': item_id,
                        'name': item['name'],
                        'sku': item['sku'],
                        'stock': item['stock'],
                        'reserved': item['reserved'],
                        'available': available
                    })
            
            return sorted(low_stock, key=lambda x: x['available'])
