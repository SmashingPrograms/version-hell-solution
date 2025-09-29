// inventory-api/cache_manager.py
"""
Cache management using in-memory storage
(In production, this would use Redis)
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional
import threading

logger = logging.getLogger(__name__)


class CacheManager:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self.cache = {}
        self.expiry = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self.lock:
            # Check if key exists and hasn't expired
            if key in self.cache:
                if key in self.expiry and datetime.now() > self.expiry[key]:
                    # Expired
                    del self.cache[key]
                    del self.expiry[key]
                    self.misses += 1
                    return None
                
                self.hits += 1
                logger.debug(f"Cache hit: {key}")
                return self.cache[key]
            
            self.misses += 1
            logger.debug(f"Cache miss: {key}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        with self.lock:
            self.cache[key] = value
            self.expiry[key] = datetime.now() + timedelta(seconds=ttl)
            logger.debug(f"Cached: {key} (TTL: {ttl}s)")
    
    def delete(self, key: str):
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.expiry:
                    del self.expiry[key]
                logger.debug(f"Deleted from cache: {key}")
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.expiry.clear()
            logger.info("Cache cleared")
    
    def get_status(self) -> dict:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'entries': len(self.cache),
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': round(hit_rate, 2)
            }
