// install_dependencies.sh
#!/bin/bash

set -e  # Exit on any error

echo "========================================"
echo "Installing Dependencies for All Services"
echo "========================================"
echo ""

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "Error: pyenv is not installed"
    echo "Install it first: curl https://pyenv.run | bash"
    exit 1
fi

# Check if correct Python version is available
if ! pyenv versions | grep -q "3.10.13"; then
    echo "Python 3.10.13 not found. Installing..."
    pyenv install 3.10.13
fi

# Set local Python version
echo "Setting Python version to 3.10.13..."
pyenv local 3.10.13

# Verify Python version
PYTHON_VERSION=$(python --version)
echo "Using: $PYTHON_VERSION"
echo ""

# Install dependencies for each service
services=("payment-gateway" "ml-fraud-detection" "inventory-api" "analytics-processor")

for service in "${services[@]}"; do
    echo "Installing dependencies for $service..."
    cd "$service"
    pip install -r requirements.txt
    cd ..
    echo ""
done

echo "========================================"
echo "✅ All dependencies installed"
echo "========================================"
echo ""
echo "Run tests with: ./run_all_tests.sh"
