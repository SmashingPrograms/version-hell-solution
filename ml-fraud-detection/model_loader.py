"""
ML model loading and management
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import logging

logger = logging.getLogger(__name__)


class MockFraudModel:
    """Mock ML model that simulates fraud detection"""
    
    def __init__(self):
        self.version = "1.2.3"
        self.feature_count = 30
        
    def predict(self, features: np.ndarray) -> np.ndarray:
        """
        Simulate fraud prediction
        
        In production, this would be a trained model.
        For this master version, we simulate realistic behavior.
        """
        # Ensure features is 2D
        if len(features.shape) == 1:
            features = features.reshape(1, -1)
        
        predictions = []
        for feature_vector in features:
            # Use feature values to generate consistent "predictions"
            # Higher amounts, unusual patterns = higher fraud score
            base_score = 0.15  # Base fraud rate
            
            # Amount influence (feature 0)
            if len(feature_vector) > 0:
                amount = feature_vector[0]
                if amount > 1000:
                    base_score += 0.15
                if amount > 5000:
                    base_score += 0.20
            
            # Time features influence (unusual hours)
            if len(feature_vector) > 22:  # Late night flag
                if feature_vector[22] == 1:
                    base_score += 0.25
            
            # High risk location
            if len(feature_vector) > 11:  # High risk country flag
                if feature_vector[11] == 1:
                    base_score += 0.30
            
            # Add some randomness based on feature hash
            feature_hash = abs(hash(tuple(feature_vector))) % 100
            noise = (feature_hash / 100.0 - 0.5) * 0.1
            
            final_score = np.clip(base_score + noise, 0.0, 1.0)
            predictions.append(final_score)
        
        return np.array(predictions)


class ModelLoader:
    """Manages ML model loading and versioning"""
    
    def __init__(self):
        self.model = None
        self.model_version = None
        self._load_model()
    
    def _load_model(self):
        """Load the fraud detection model"""
        logger.info("Loading fraud detection model...")
        
        # In production, this would load a trained model from disk
        # For this master version, we use a mock model
        self.model = MockFraudModel()
        self.model_version = self.model.version
        
        logger.info(f"Model loaded successfully: v{self.model_version}")
    
    def get_model(self):
        """Get the loaded model"""
        if self.model is None:
            self._load_model()
        return self.model
    
    def get_model_version(self) -> str:
        """Get model version string"""
        return self.model_version or "unknown"
    
    def get_model_info(self) -> dict:
        """Get detailed model information"""
        return {
            'version': self.model_version,
            'type': 'RandomForestClassifier (simulated)',
            'feature_count': self.model.feature_count if self.model else 0,
            'status': 'loaded' if self.model else 'not_loaded'
        }
