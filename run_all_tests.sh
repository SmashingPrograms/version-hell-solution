// run_all_tests.sh
#!/bin/bash

# Run all service tests and generate summary report
# This script validates that all services are working correctly

set -e  # Exit on first error

echo "========================================"
echo "E-Commerce Services Test Suite"
echo "Python Version: $(python --version)"
echo "========================================"
echo ""

# Track test results
TOTAL_PASSED=0
TOTAL_FAILED=0
FAILED_SERVICES=()

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_dir=$2
    
    echo "========================================"
    echo "Testing $service_name"
    echo "========================================"
    
    cd "$service_dir"
    
    # Run pytest and capture output
    if python -m pytest test_*.py -v --tb=short 2>&1 | tee test_output.log; then
        # Extract test count from pytest output
        PASSED=$(grep -oP '\d+(?= passed)' test_output.log | tail -1)
        PASSED=${PASSED:-0}
        
        echo -e "${GREEN}✅ All $PASSED tests passed${NC}"
        TOTAL_PASSED=$((TOTAL_PASSED + PASSED))
    else
        # Tests failed
        FAILED=$(grep -oP '\d+(?= failed)' test_output.log | tail -1)
        FAILED=${FAILED:-1}
        
        echo -e "${RED}❌ $FAILED test(s) failed${NC}"
        TOTAL_FAILED=$((TOTAL_FAILED + FAILED))
        FAILED_SERVICES+=("$service_name")
    fi
    
    rm -f test_output.log
    cd - > /dev/null
    echo ""
}

# Run tests for each service
run_service_tests "Payment Gateway Service" "payment-gateway"
run_service_tests "ML Fraud Detection Service" "ml-fraud-detection"
run_service_tests "Inventory API Service" "inventory-api"
run_service_tests "Analytics Processor Service" "analytics-processor"

# Print summary
echo "========================================"
echo "SUMMARY"
echo "========================================"

if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL SERVICES PASSED${NC}"
    echo "Total: $TOTAL_PASSED tests passed, $TOTAL_FAILED failed"
    exit 0
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo "Total: $TOTAL_PASSED tests passed, $TOTAL_FAILED failed"
    echo ""
    echo "Failed services:"
    for service in "${FAILED_SERVICES[@]}"; do
        echo -e "  ${RED}• $service${NC}"
    done
    exit 1
fi
