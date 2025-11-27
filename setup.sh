#!/bin/bash
# Setup script for Multi-Annotator Conflict Detection System
# Supports both local environment and Docker setup

set -e  # Exit on error

echo "============================================="
echo "Multi-Annotator Conflict Detection System"
echo "Setup Script"
echo "============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
OS_TYPE=$(uname -s)
echo "Detected OS: $OS_TYPE"

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠ Docker not found. Will use local Python environment.${NC}"
    DOCKER_AVAILABLE=false
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python found: $PYTHON_VERSION${NC}"
    PYTHON_AVAILABLE=true
else
    echo -e "${RED}✗ Python 3 is required but not found${NC}"
    PYTHON_AVAILABLE=false
fi

echo ""
echo "============================================="
echo "Installation Options"
echo "============================================="
echo ""

if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "1. Docker-based setup (recommended)"
    echo "2. Local Python environment setup"
    echo "3. Both Docker and local setup"
    echo ""
    read -p "Choose installation option (1-3): " INSTALL_OPTION
else
    echo "1. Local Python environment setup"
    read -p "Continue with local Python setup? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        INSTALL_OPTION=1
    else
        echo "Installation cancelled."
        exit 1
    fi
fi

# Local Python setup
setup_local_environment() {
    echo ""
    echo "============================================="
    echo "Setting up Local Python Environment"
    echo "============================================="
    echo ""
    
    if [ "$PYTHON_AVAILABLE" = false ]; then
        echo -e "${RED}Error: Python 3 is required${NC}"
        exit 1
    fi
    
    # Create virtual environment
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    if [ "$OS_TYPE" = "Darwin" ] || [ "$OS_TYPE" = "Linux" ]; then
        source venv/bin/activate
    else
        source venv/Scripts/activate
    fi
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
    
    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    
    # Create output directory
    mkdir -p output
    echo -e "${GREEN}✓ Output directory created${NC}"
    
    echo ""
    echo -e "${GREEN}Local environment setup complete!${NC}"
    echo ""
    echo "To activate the environment in the future, run:"
    if [ "$OS_TYPE" = "Darwin" ] || [ "$OS_TYPE" = "Linux" ]; then
        echo "  source venv/bin/activate"
    else
        echo "  source venv/Scripts/activate"
    fi
}

# Docker setup
setup_docker_environment() {
    echo ""
    echo "============================================="
    echo "Setting up Docker Environment"
    echo "============================================="
    echo ""
    
    echo "Building Docker image..."
    docker build -t conflict-detection-system:latest .
    echo -e "${GREEN}✓ Docker image built${NC}"
    
    # Create output directory
    mkdir -p output
    echo -e "${GREEN}✓ Output directory created${NC}"
    
    echo ""
    echo -e "${GREEN}Docker setup complete!${NC}"
    echo ""
    echo "To run with Docker, use:"
    echo "  docker run -v \$(pwd)/output:/app/output conflict-detection-system:latest main.py text_label.jsonl"
}

# Execute selected option
case $INSTALL_OPTION in
    1)
        setup_local_environment
        ;;
    2)
        setup_docker_environment
        ;;
    3)
        setup_local_environment
        setup_docker_environment
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo "============================================="
echo "Setup Complete!"
echo "============================================="
echo ""
echo "Next steps:"
echo "1. Review the README.md file for usage examples"
echo "2. Run tests with: ./run_tests.sh"
echo "3. Analyze your dataset with: python main.py <input_file>"
echo ""
