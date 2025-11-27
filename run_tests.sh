#!/bin/bash

# Test Runner Script
# Executes all tests and generates a comprehensive test report

set -e

echo "======================================"
echo "Running Test Suite"
echo "======================================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

# Create test reports directory
mkdir -p reports

echo ""
echo "[1/3] Running unit tests..."
python -m pytest tests/test_conflict_analyzer.py -v --tb=short --junit-xml=reports/test_results.xml

echo ""
echo "[2/3] Running coverage analysis..."
python -m pytest tests/test_conflict_analyzer.py --cov=src --cov-report=html:reports/coverage --cov-report=term

echo ""
echo "[3/3] Generating test summary..."
python << 'EOF'
import xml.etree.ElementTree as ET
import json
from pathlib import Path

# Parse test results
results_file = "reports/test_results.xml"
if Path(results_file).exists():
    tree = ET.parse(results_file)
    root = tree.getroot()
    
    testsuite = root
    total_tests = int(testsuite.get('tests', 0))
    failures = int(testsuite.get('failures', 0))
    errors = int(testsuite.get('errors', 0))
    skipped = int(testsuite.get('skipped', 0))
    passed = total_tests - failures - errors - skipped
    
    print(f"\n{'='*50}")
    print(f"Test Summary")
    print(f"{'='*50}")
    print(f"Total Tests:    {total_tests}")
    print(f"Passed:         {passed} ✓")
    print(f"Failed:         {failures}")
    print(f"Errors:         {errors}")
    print(f"Skipped:        {skipped}")
    print(f"Success Rate:   {passed/total_tests*100:.1f}%" if total_tests > 0 else "N/A")
    print(f"{'='*50}\n")
EOF

echo "✓ Tests completed! Check reports/ for detailed results."
