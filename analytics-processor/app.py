"""
Analytics Processor Service
Processes sales data and generates analytics reports
Python 3.10 compatible
"""

from flask import Flask, request, jsonify, send_file
import logging
from analytics_engine import AnalyticsEngine
from report_generator import ReportGenerator
import io

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
analytics_engine = AnalyticsEngine()
report_generator = ReportGenerator()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'analytics-processor',
        'version': '1.0.0',
        'python_version': '3.10'
    }), 200


@app.route('/api/v1/analytics/sales-summary', methods=['POST'])
def sales_summary():
    """Generate sales summary from transaction data"""
    data = request.get_json()
    
    if 'transactions' not in data:
        return jsonify({'error': 'Missing transactions data'}), 400
    
    summary = analytics_engine.generate_sales_summary(data['transactions'])
    
    return jsonify(summary), 200


@app.route('/api/v1/analytics/time-series', methods=['POST'])
def time_series_analysis():
    """Perform time series analysis on sales data"""
    data = request.get_json()
    
    required_fields = ['transactions', 'period']
    if not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields',
            'required': required_fields
        }), 400
    
    analysis = analytics_engine.time_series_analysis(
        data['transactions'],
        data['period']
    )
    
    return jsonify(analysis), 200


@app.route('/api/v1/analytics/customer-segments', methods=['POST'])
def customer_segmentation():
    """Segment customers based on purchase behavior"""
    data = request.get_json()
    
    if 'customers' not in data:
        return jsonify({'error': 'Missing customers data'}), 400
    
    segments = analytics_engine.segment_customers(data['customers'])
    
    return jsonify(segments), 200


@app.route('/api/v1/analytics/product-performance', methods=['POST'])
def product_performance():
    """Analyze product performance metrics"""
    data = request.get_json()
    
    if 'products' not in data:
        return jsonify({'error': 'Missing products data'}), 400
    
    performance = analytics_engine.analyze_product_performance(data['products'])
    
    return jsonify(performance), 200


@app.route('/api/v1/analytics/generate-report', methods=['POST'])
def generate_report():
    """Generate comprehensive analytics report"""
    data = request.get_json()
    
    report_type = data.get('report_type', 'summary')
    report_format = data.get('format', 'json')
    
    if 'data' not in data:
        return jsonify({'error': 'Missing data for report generation'}), 400
    
    report = report_generator.generate(
        report_type,
        data['data'],
        report_format
    )
    
    if report_format == 'csv':
        output = io.StringIO()
        output.write(report)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name='analytics_report.csv'
        )
    
    return jsonify(report), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=False)
