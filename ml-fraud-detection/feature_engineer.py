// ml-fraud-detection/feature_engineer.py
"""
Feature engineering for fraud detection
"""

import numpy as np
from typing import Dict
from datetime import datetime
import hashlib


class FeatureEngineer:
    """Extracts and engineers features from raw transaction data"""
    
    def extract_features(self, transaction: Dict) -> np.ndarray:
        """
        Extract and engineer features from transaction
        
        Returns numpy array of features suitable for ML model
        """
        features = []
        
        # Amount-based features
        features.extend(self._extract_amount_features(transaction))
        
        # Merchant features
        features.extend(self._extract_merchant_features(transaction))
        
        # Location features
        features.extend(self._extract_location_features(transaction))
        
        # Time-based features
        features.extend(self._extract_time_features(transaction))
        
        # Customer features
        features.extend(self._extract_customer_features(transaction))
        
        return np.array(features, dtype=np.float32)
    
    def _extract_amount_features(self, transaction: Dict) -> list:
        """Extract amount-related features"""
        amount = float(transaction.get('amount', 0))
        
        return [
            amount,  # Raw amount
            np.log1p(amount),  # Log-transformed amount
            1 if amount > 1000 else 0,  # High amount flag
            1 if amount < 10 else 0,  # Low amount flag
            amount / 100.0,  # Normalized amount
        ]
    
    def _extract_merchant_features(self, transaction: Dict) -> list:
        """Extract merchant-related features"""
        merchant_category = transaction.get('merchant_category', 'unknown').lower()
        
        # One-hot encode common categories
        categories = ['retail', 'food', 'travel', 'entertainment', 'gambling', 
                     'cryptocurrency', 'adult', 'utilities', 'healthcare', 'education']
        
        category_features = [1 if merchant_category == cat else 0 for cat in categories]
        
        # Merchant risk score (hash-based for consistency)
        merchant_id = transaction.get('merchant_id', 'unknown')
        merchant_hash = int(hashlib.md5(merchant_id.encode()).hexdigest()[:8], 16)
        merchant_risk = (merchant_hash % 100) / 100.0
        
        return category_features + [merchant_risk]
    
    def _extract_location_features(self, transaction: Dict) -> list:
        """Extract location-related features"""
        location = transaction.get('location', {})
        country_code = location.get('country_code', 'US')
        city = location.get('city', 'unknown')
        
        # High-risk country flags
        high_risk_countries = ['NG', 'PK', 'RU', 'CN', 'VN']
        is_high_risk = 1 if country_code in high_risk_countries else 0
        
        # Distance from customer's typical location (simulated)
        distance_hash = int(hashlib.md5(city.encode()).hexdigest()[:8], 16)
        distance_km = (distance_hash % 10000) / 10.0  # 0-1000 km
        
        return [
            is_high_risk,
            distance_km,
            np.log1p(distance_km),
        ]
    
    def _extract_time_features(self, transaction: Dict) -> list:
        """Extract time-based features"""
        timestamp_str = transaction.get('timestamp', datetime.utcnow().isoformat())
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except:
            timestamp = datetime.utcnow()
        
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        return [
            hour / 24.0,  # Normalized hour
            day_of_week / 7.0,  # Normalized day
            1 if 2 <= hour < 6 else 0,  # Late night flag
            1 if day_of_week >= 5 else 0,  # Weekend flag
            np.sin(2 * np.pi * hour / 24),  # Cyclical hour encoding
            np.cos(2 * np.pi * hour / 24),
        ]
    
    def _extract_customer_features(self, transaction: Dict) -> list:
        """Extract customer-related features"""
        customer_id = transaction.get('customer_id', 'unknown')
        
        # Customer history score (hash-based simulation)
        customer_hash = int(hashlib.md5(customer_id.encode()).hexdigest()[:8], 16)
        
        # Simulate customer metrics
        account_age_days = (customer_hash % 1000)
        transaction_count = (customer_hash % 500)
        avg_transaction_amount = ((customer_hash % 10000) / 10.0)
        
        return [
            np.log1p(account_age_days),
            np.log1p(transaction_count),
            np.log1p(avg_transaction_amount),
            1 if account_age_days < 30 else 0,  # New account flag
        ]
