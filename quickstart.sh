#!/bin/bash

# Quick Start Script
# This script helps you get started quickly with the map-reduce system

echo "=================================================="
echo "  Map-Reduce System Quick Start"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Run tests
echo "Running system tests..."
python3 test_system.py

if [ $? -ne 0 ]; then
    echo "❌ Some tests failed. Please review the errors above."
    exit 1
fi

echo ""
echo "✓ All tests passed!"
echo ""

# Run quick demo
echo "Running quick demo (1,000 log records)..."
echo "This will take about 5-10 seconds..."
echo ""

python3 run_example.py log-analysis 1000

if [ $? -ne 0 ]; then
    echo "❌ Demo failed"
    exit 1
fi

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Review results in: log_analysis_results.txt"
echo "  2. Try larger dataset: python3 run_example.py log-analysis 10000"
echo "  3. Try sales analysis: python3 run_example.py sales-analysis 5000"
echo "  4. Read documentation: README.md, QUICKSTART.md"
echo ""
echo "For distributed deployment on multiple machines:"
echo "  1. Edit config.yaml with your machine IPs"
echo "  2. On each machine: python3 main.py start-worker worker-X"
echo "  3. On coordinator: python3 run_example.py log-analysis 100000"
echo ""
