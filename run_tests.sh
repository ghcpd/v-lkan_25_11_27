#!/bin/bash
# Test execution script for Multi-Annotator Conflict Detection System
# Supports both local Python and Docker environments

set -e  # Exit on error

echo "============================================="
echo "Multi-Annotator Conflict Detection System"
echo "Test Suite Execution"
echo "============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for test environment
DOCKER_AVAILABLE=false
VENV_AVAILABLE=false

if command -v docker &> /dev/null; then
    DOCKER_AVAILABLE=true
fi

if [ -d "venv" ]; then
    VENV_AVAILABLE=true
fi

# Create output directories
mkdir -p test_reports
mkdir -p test_output

# Function to run tests with Python
run_local_tests() {
    echo -e "${BLUE}Running tests with local Python environment...${NC}"
    echo ""
    
    # Activate virtual environment if available
    if [ "$VENV_AVAILABLE" = true ]; then
        echo "Activating virtual environment..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        elif [ -f "venv/Scripts/activate" ]; then
            source venv/Scripts/activate
        fi
    fi
    
    # Run unit tests
    echo -e "${YELLOW}Running unit tests...${NC}"
    python -m pytest test_conflict_detection.py -v --tb=short \
        --html=test_reports/test_report.html \
        --self-contained-html \
        --cov=analyzer \
        --cov-report=html:test_reports/coverage \
        --cov-report=term-missing \
        --junit-xml=test_reports/junit_results.xml
    
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
    else
        echo -e "${RED}✗ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
    fi
    
    return $TEST_EXIT_CODE
}

# Function to run tests with unittest
run_unittest() {
    echo -e "${BLUE}Running tests with unittest...${NC}"
    echo ""
    
    # Activate virtual environment if available
    if [ "$VENV_AVAILABLE" = true ]; then
        echo "Activating virtual environment..."
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        elif [ -f "venv/Scripts/activate" ]; then
            source venv/Scripts/activate
        fi
    fi
    
    # Run with unittest
    echo -e "${YELLOW}Running test suite...${NC}"
    python -m unittest discover -s . -p "test_*.py" -v
    
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
    else
        echo -e "${RED}✗ Some tests failed (exit code: $TEST_EXIT_CODE)${NC}"
    fi
    
    return $TEST_EXIT_CODE
}

# Function to run tests with Docker
run_docker_tests() {
    echo -e "${BLUE}Running tests with Docker...${NC}"
    echo ""
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t conflict-detection-system:test .
    
    echo -e "${YELLOW}Running test suite in Docker...${NC}"
    docker run --rm \
        -v "$(pwd)/test_output:/app/output" \
        -v "$(pwd)/test_reports:/app/test_reports" \
        conflict-detection-system:test \
        python -m unittest discover -s . -p "test_*.py" -v
    
    TEST_EXIT_CODE=$?
    
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed in Docker!${NC}"
    else
        echo -e "${RED}✗ Some tests failed in Docker (exit code: $TEST_EXIT_CODE)${NC}"
    fi
    
    return $TEST_EXIT_CODE
}

# Function to run integration tests
run_integration_tests() {
    echo ""
    echo -e "${BLUE}Running integration tests...${NC}"
    echo ""
    
    # Activate virtual environment if available
    if [ "$VENV_AVAILABLE" = true ]; then
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
        elif [ -f "venv/Scripts/activate" ]; then
            source venv/Scripts/activate
        fi
    fi
    
    # Test 1: Analysis of provided dataset
    echo -e "${YELLOW}Test 1: Analyzing provided dataset...${NC}"
    python main.py text_label.jsonl \
        --output test_output/integration_test_results.jsonl \
        --report test_output/integration_test_report.json \
        --conflicts-only \
        -v
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Integration test 1 passed${NC}"
    else
        echo -e "${RED}✗ Integration test 1 failed${NC}"
        return 1
    fi
    
    # Test 2: Verify output file format
    echo -e "${YELLOW}Test 2: Verifying output file format...${NC}"
    if [ -f "test_output/integration_test_results.jsonl" ]; then
        echo -e "${GREEN}✓ Output file created${NC}"
    else
        echo -e "${RED}✗ Output file not created${NC}"
        return 1
    fi
    
    # Test 3: Verify report generation
    echo -e "${YELLOW}Test 3: Verifying report generation...${NC}"
    if [ -f "test_output/integration_test_report.json" ]; then
        echo -e "${GREEN}✓ Report file created${NC}"
    else
        echo -e "${RED}✗ Report file not created${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ All integration tests passed!${NC}"
    return 0
}

# Main execution
echo "Available test options:"
echo "1. Run unit tests (pytest)"
echo "2. Run unit tests (unittest)"
echo "3. Run integration tests"
echo "4. Run all tests locally"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "5. Run all tests with Docker"
    echo "6. Run all tests (Docker + local)"
fi
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    read -p "Choose option (1-6) [4]: " TEST_OPTION
else
    read -p "Choose option (1-4) [4]: " TEST_OPTION
fi

TEST_OPTION=${TEST_OPTION:-4}

case $TEST_OPTION in
    1)
        run_local_tests
        TEST_EXIT_CODE=$?
        ;;
    2)
        run_unittest
        TEST_EXIT_CODE=$?
        ;;
    3)
        run_integration_tests
        TEST_EXIT_CODE=$?
        ;;
    4)
        run_unittest
        TEST_EXIT_CODE=$?
        if [ $TEST_EXIT_CODE -eq 0 ]; then
            run_integration_tests
            TEST_EXIT_CODE=$?
        fi
        ;;
    5)
        if [ "$DOCKER_AVAILABLE" = true ]; then
            run_docker_tests
            TEST_EXIT_CODE=$?
        else
            echo -e "${RED}Docker is not available${NC}"
            TEST_EXIT_CODE=1
        fi
        ;;
    6)
        if [ "$DOCKER_AVAILABLE" = true ]; then
            run_unittest
            TEST_EXIT_CODE=$?
            if [ $TEST_EXIT_CODE -eq 0 ]; then
                run_docker_tests
                TEST_EXIT_CODE=$?
            fi
        else
            echo -e "${RED}Docker is not available${NC}"
            TEST_EXIT_CODE=1
        fi
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        TEST_EXIT_CODE=1
        ;;
esac

echo ""
echo "============================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Test execution completed successfully!${NC}"
    echo "Test reports are available in: test_reports/"
else
    echo -e "${RED}Test execution failed!${NC}"
    echo "Check test_reports/ for details"
fi
echo "============================================="
echo ""

exit $TEST_EXIT_CODE
