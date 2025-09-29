// ml-fraud-detection/app.py
"""
ML Fraud Detection Service
Analyzes transactions for fraud using machine learning patterns
Python 3.10 compatible
"""

from flask import Flask, request, jsonify
import logging
from fraud_analyzer import FraudAnalyzer
from feature_engineer import FeatureEngineer
from model_loader import ModelLoader

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ML components
feature_engineer = FeatureEngineer()
model_loader = ModelLoader()
analyzer = FraudAnalyzer(feature_engineer, model_loader)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ml-fraud-detection',
        'version': '1.0.0',
        'python_version': '3.10',
        'model_version': model_loader.get_model_version()
    }), 200


@app.route('/api/v1/fraud/analyze', methods=['POST'])
def analyze_transaction():
    """Analyze transaction for fraud"""
    data = request.get_json()
    
    required_fields = ['transaction_id', 'amount', 'merchant_category', 
                      'customer_id', 'location']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'required': required_fields
        }), 400
    
    result = analyzer.analyze(data)
    logger.info(f"Transaction {data['transaction_id']}: "
               f"risk_score={result['fraud_score']:.2f}, "
               f"risk_level={result['risk_level']}")
    
    return jsonify(result), 200


@app.route('/api/v1/fraud/batch-analyze', methods=['POST'])
def batch_analyze():
    """Batch analyze multiple transactions"""
    data = request.get_json()
    
    if 'transactions' not in data:
        return jsonify({'error': 'Missing transactions array'}), 400
    
    results = []
    for transaction in data['transactions']:
        try:
            result = analyzer.analyze(transaction)
            results.append(result)
        except Exception as e:
            logger.error(f"Error analyzing transaction: {e}")
            results.append({
                'transaction_id': transaction.get('transaction_id', 'unknown'),
                'error': str(e)
            })
    
    return jsonify({
        'total': len(results),
        'analyzed': len([r for r in results if 'error' not in r]),
        'errors': len([r for r in results if 'error' in r]),
        'results': results
    }), 200


@app.route('/api/v1/fraud/model-info', methods=['GET'])
def model_info():
    """Get information about the loaded model"""
    return jsonify(model_loader.get_model_info()), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
