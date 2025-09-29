// ml-fraud-detection/fraud_analyzer.py
"""
Core fraud analysis logic with ML-based risk scoring
"""

import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class FraudAnalyzer:
    """Analyzes transactions for fraudulent patterns"""
    
    # Risk thresholds
    LOW_RISK_THRESHOLD = 0.3
    MEDIUM_RISK_THRESHOLD = 0.6
    HIGH_RISK_THRESHOLD = 0.85
    
    def __init__(self, feature_engineer, model_loader):
        self.feature_engineer = feature_engineer
        self.model_loader = model_loader
        self.risk_rules = self._initialize_risk_rules()
    
    def _initialize_risk_rules(self) -> Dict:
        """Initialize rule-based risk checks"""
        return {
            'high_amount_threshold': 5000.00,
            'suspicious_merchant_categories': ['gambling', 'cryptocurrency', 'adult'],
            'high_risk_countries': ['NG', 'PK', 'RU', 'CN'],
            'velocity_threshold': 5,  # Max transactions per hour
        }
    
    def analyze(self, transaction: Dict) -> Dict:
        """
        Analyze a transaction for fraud
        
        Returns fraud score (0-1) and risk level
        """
        transaction_id = transaction.get('transaction_id', 'unknown')
        
        # Extract and engineer features
        features = self.feature_engineer.extract_features(transaction)
        
        # Get ML model prediction
        ml_score = self._get_ml_prediction(features)
        
        # Apply rule-based adjustments
        rule_adjustment = self._apply_risk_rules(transaction)
        
        # Combine scores
        final_score = self._combine_scores(ml_score, rule_adjustment)
        
        # Determine risk level
        risk_level = self._determine_risk_level(final_score)
        
        # Generate detailed analysis
        analysis = self._generate_analysis(transaction, features, ml_score, 
                                          rule_adjustment, final_score)
        
        return {
            'transaction_id': transaction_id,
            'fraud_score': round(final_score, 4),
            'risk_level': risk_level,
            'ml_score': round(ml_score, 4),
            'rule_adjustment': round(rule_adjustment, 4),
            'recommendation': self._get_recommendation(risk_level),
            'analysis': analysis
        }
    
    def _get_ml_prediction(self, features: np.ndarray) -> float:
        """Get ML model prediction"""
        model = self.model_loader.get_model()
        
        # Simulate ML model prediction
        # In production, this would be: model.predict_proba(features)[0][1]
        prediction = model.predict(features)
        
        return float(prediction[0])
    
    def _apply_risk_rules(self, transaction: Dict) -> float:
        """Apply rule-based risk adjustments"""
        adjustment = 0.0
        
        # High amount check
        amount = float(transaction.get('amount', 0))
        if amount > self.risk_rules['high_amount_threshold']:
            adjustment += 0.15
            logger.debug(f"High amount detected: ${amount}")
        
        # Suspicious merchant category
        merchant_category = transaction.get('merchant_category', '').lower()
        if merchant_category in self.risk_rules['suspicious_merchant_categories']:
            adjustment += 0.20
            logger.debug(f"Suspicious category: {merchant_category}")
        
        # High-risk location
        location = transaction.get('location', {})
        country_code = location.get('country_code', '')
        if country_code in self.risk_rules['high_risk_countries']:
            adjustment += 0.25
            logger.debug(f"High-risk country: {country_code}")
        
        # Time-based anomalies
        if self._is_unusual_time(transaction):
            adjustment += 0.10
            logger.debug("Unusual transaction time detected")
        
        return min(adjustment, 0.5)  # Cap rule adjustment at 0.5
    
    def _is_unusual_time(self, transaction: Dict) -> bool:
        """Check if transaction occurs at unusual time"""
        from datetime import datetime
        
        timestamp_str = transaction.get('timestamp')
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            hour = timestamp.hour
            
            # Flagging 2 AM - 5 AM as unusual
            return 2 <= hour < 5
        except:
            return False
    
    def _combine_scores(self, ml_score: float, rule_adjustment: float) -> float:
        """Combine ML and rule-based scores"""
        # Weighted combination: 70% ML, 30% rules
        combined = (0.7 * ml_score) + (0.3 * rule_adjustment)
        
        # Apply rule adjustment on top
        combined = min(combined + rule_adjustment, 1.0)
        
        return combined
    
    def _determine_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= self.HIGH_RISK_THRESHOLD:
            return 'high'
        elif score >= self.MEDIUM_RISK_THRESHOLD:
            return 'medium'
        elif score >= self.LOW_RISK_THRESHOLD:
            return 'low'
        else:
            return 'minimal'
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get action recommendation based on risk level"""
        recommendations = {
            'minimal': 'Approve transaction',
            'low': 'Approve transaction with standard monitoring',
            'medium': 'Request additional verification',
            'high': 'Decline transaction and flag for review'
        }
        return recommendations.get(risk_level, 'Manual review required')
    
    def _generate_analysis(self, transaction: Dict, features: np.ndarray,
                          ml_score: float, rule_adjustment: float, 
                          final_score: float) -> Dict:
        """Generate detailed analysis"""
        risk_factors = []
        
        amount = float(transaction.get('amount', 0))
        if amount > self.risk_rules['high_amount_threshold']:
            risk_factors.append(f"High transaction amount: ${amount:.2f}")
        
        merchant_category = transaction.get('merchant_category', '').lower()
        if merchant_category in self.risk_rules['suspicious_merchant_categories']:
            risk_factors.append(f"Suspicious merchant category: {merchant_category}")
        
        location = transaction.get('location', {})
        country_code = location.get('country_code', '')
        if country_code in self.risk_rules['high_risk_countries']:
            risk_factors.append(f"High-risk location: {country_code}")
        
        if self._is_unusual_time(transaction):
            risk_factors.append("Transaction at unusual hour")
        
        return {
            'risk_factors': risk_factors,
            'feature_count': len(features),
            'model_confidence': round(abs(ml_score - 0.5) * 2, 4),
            'rule_contribution': round(rule_adjustment / final_score * 100 if final_score > 0 else 0, 2)
        }
