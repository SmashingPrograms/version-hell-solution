// README.md
# E-Commerce Order Processing Platform - Master Version

**Status:** ✅ Working Baseline (All services compatible with Python 3.10)

This is the **golden master** version of the e-commerce microservices platform. All services run on Python 3.10.13 and work correctly together. This serves as the baseline before introducing the intentional version conflicts for the pyenv runtime management exercise.

## Architecture

The platform consists of 4 microservices:

1. **Payment Gateway** (Port 5001) - Processes payments with Stripe-like patterns
2. **ML Fraud Detection** (Port 5002) - Analyzes transactions for fraud using ML
3. **Inventory API** (Port 5003) - Manages product inventory with caching
4. **Analytics Processor** (Port 5004) - Processes sales data and generates reports

```
┌─────────────────┐
│  Payment API    │  Port 5001
│  (Flask)        │  
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fraud Detection │  Port 5002
│  (Flask + ML)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Inventory API  │  Port 5003
│ (Flask + Cache) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Analytics     │  Port 5004
│ (Flask + Pandas)│
└─────────────────┘
```

## Prerequisites

- Python 3.10.13 (all services)
- pyenv (for Python version management)
- pip (Python package installer)

## Quick Start

### 1. Install pyenv and Python 3.10

```bash
# Install pyenv (macOS/Linux)
curl https://pyenv.run | bash

# Install Python 3.10.13
pyenv install 3.10.13

# Set global Python version
pyenv global 3.10.13

# Verify installation
python --version  # Should show Python 3.10.13
```

### 2. Set Up All Services

```bash
# Clone/navigate to project directory
cd ecommerce-services

# Set local Python version for the project
pyenv local 3.10.13

# Install dependencies for each service
cd payment-gateway
pip install -r requirements.txt
cd ..

cd ml-fraud-detection
pip install -r requirements.txt
cd ..

cd inventory-api
pip install -r requirements.txt
cd ..

cd analytics-processor
pip install -r requirements.txt
cd ..
```

### 3. Run All Tests

```bash
# Make test script executable
chmod +x run_all_tests.sh

# Run all service tests
./run_all_tests.sh
```

Expected output:
```
========================================
Testing Payment Gateway Service
========================================
✅ All 8 tests passed

========================================
Testing ML Fraud Detection Service
========================================
✅ All 9 tests passed

========================================
Testing Inventory API Service
========================================
✅ All 12 tests passed

========================================
Testing Analytics Processor Service
========================================
✅ All 15 tests passed

========================================
SUMMARY
========================================
✅ ALL SERVICES PASSED
Total: 44 tests passed, 0 failed
```

### 4. Run Individual Services

```bash
# Terminal 1 - Payment Gateway
cd payment-gateway
python app.py

# Terminal 2 - Fraud Detection
cd ml-fraud-detection
python app.py

# Terminal 3 - Inventory API
cd inventory-api
python app.py

# Terminal 4 - Analytics Processor
cd analytics-processor
python app.py
```

### 5. Test Service Endpoints

```bash
# Payment Gateway Health Check
curl http://localhost:5001/health

# Fraud Detection Health Check
curl http://localhost:5002/health

# Inventory API Health Check
curl http://localhost:5003/health

# Analytics Processor Health Check
curl http://localhost:5004/health
```

## Service Details

### Payment Gateway (Python 3.10)

**Dependencies:**
- Flask==2.3.0
- SQLAlchemy==2.0.15
- pytest==7.3.1
- requests==2.31.0

**Features:**
- Payment processing with Luhn algorithm validation
- JWT-style API key authentication
- SQLite database for transaction storage
- Refund processing
- Processing fee calculations

**Key Files:**
- `app.py` - Flask application and routes
- `payment_processor.py` - Payment processing logic
- `auth_middleware.py` - API authentication
- `models.py` - Database models
- `database.py` - Database configuration
- `test_payment.py` - 8 comprehensive tests

### ML Fraud Detection (Python 3.10)

**Dependencies:**
- Flask==2.3.0
- numpy==1.24.3
- scikit-learn==1.2.2
- pytest==7.3.1
- requests==2.31.0

**Features:**
- ML-based fraud scoring (mock model)
- Feature engineering with 30+ features
- Rule-based risk adjustments
- Batch transaction analysis
- Risk level categorization

**Key Files:**
- `app.py` - Flask application and routes
- `fraud_analyzer.py` - Core analysis logic
- `feature_engineer.py` - Feature extraction
- `model_loader.py` - ML model management
- `test_fraud.py` - 9 comprehensive tests

### Inventory API (Python 3.10)

**Dependencies:**
- Flask==2.3.0
- pytest==7.3.1
- requests==2.31.0

**Features:**
- Real-time inventory tracking
- Reservation system for orders
- In-memory caching with TTL
- Low stock alerts
- Inventory adjustment logging

**Key Files:**
- `app.py` - Flask application and routes
- `inventory_manager.py` - Inventory logic
- `cache_manager.py` - Caching implementation
- `test_inventory.py` - 12 comprehensive tests

### Analytics Processor (Python 3.10)

**Dependencies:**
- Flask==2.3.0
- pandas==2.0.1
- numpy==1.24.3
- pytest==7.3.1
- requests==2.31.0

**Features:**
- Sales summary statistics
- Time series analysis (daily/weekly/monthly)
- Customer segmentation (RFM analysis)
- Product performance metrics
- Report generation (JSON/CSV)

**Key Files:**
- `app.py` - Flask application and routes
- `analytics_engine.py` - Core analytics with pandas
- `report_generator.py` - Report formatting
- `test_analytics.py` - 15 comprehensive tests

## Testing

Each service has comprehensive pytest test suites:

```bash
# Test individual service
cd payment-gateway
python -m pytest test_payment.py -v

# Test with coverage
python -m pytest test_payment.py --cov=. --cov-report=html
```

## Validation Checklist

Use this checklist to verify the master version is working correctly:

- [ ] Python 3.10.13 installed via pyenv
- [ ] All dependencies install without errors
- [ ] Payment Gateway: 8/8 tests pass
- [ ] Fraud Detection: 9/9 tests pass
- [ ] Inventory API: 12/12 tests pass
- [ ] Analytics Processor: 15/15 tests pass
- [ ] All services start without errors
- [ ] Health check endpoints respond correctly
- [ ] No syntax errors or import failures
- [ ] No database connection errors
- [ ] No missing dependencies

## Next Steps

Once this master version is validated:

1. **Document the working state** - Record all test results
2. **Create exercise version** - Introduce intentional version conflicts
3. **Test broken state** - Verify conflicts produce expected errors
4. **Create solution guide** - Document how to fix each conflict

## Troubleshooting

### Issue: Python version mismatch

```bash
# Verify Python version
python --version

# Should show: Python 3.10.13

# If not, set local version
pyenv local 3.10.13
```

### Issue: Import errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Issue: Tests fail

```bash
# Run tests with verbose output
python -m pytest test_*.py -v -s

# Check for missing test dependencies
pip install pytest requests
```

## Project Structure

```
ecommerce-services/
├── README.md
├── run_all_tests.sh
├── docker-compose.yml
├── .python-version          # Contains: 3.10.13
├── payment-gateway/
│   ├── app.py
│   ├── payment_processor.py
│   ├── auth_middleware.py
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   └── test_payment.py
├── ml-fraud-detection/
│   ├── app.py
│   ├── fraud_analyzer.py
│   ├── feature_engineer.py
│   ├── model_loader.py
│   ├── requirements.txt
│   └── test_fraud.py
├── inventory-api/
│   ├── app.py
│   ├── inventory_manager.py
│   ├── cache_manager.py
│   ├── requirements.txt
│   └── test_inventory.py
└── analytics-processor/
    ├── app.py
    ├── analytics_engine.py
    ├── report_generator.py
    ├── requirements.txt
    └── test_analytics.py
```

## License

MIT License - Educational purposes

---

**Note:** This is the MASTER version - all services are compatible and working. The exercise version will introduce intentional conflicts for learning purposes.
